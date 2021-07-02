# Written by Gerd Mund & Robert Logiewa

from dominate.tags import datalist
from flask import request, jsonify, current_app as app, json
from app.api import bp, errors
from app import db, exe
import datetime
from app.models import (
    DataSet,
    DataSetSchema,
    FusionHypothesis,
    FusionHypothesisSchema,
    BirdMapping,
    BirdMappingSchema,
)
import pandas as pd
from app.fusion.fusion_center import FusionCenter
from app.fusion.model import Bearing, Hypothesis
import numpy as np


def ToHypothesis(h, mo):
    """Convert the database format to fusion centre format"""
    
    # Convert bird code to bird index
    css = 0
    for m in mo:
        if m["id"] == h["code"]:
            css = m["vec_id"]
            break

    # Convert position and covariance to np.arrays
    pos = np.array(json.loads(h["position"]))
    cov = np.array(json.loads(h["covariance"]))

    # Create the hypotheses object
    hypo = Hypothesis(
        timestamp=h["timestamp"],
        w=h["weight"],
        x=pos,
        P=cov,
        classification=css
    )

    return hypo


def FuseData(dataSet):
    """Fuses the pushed data and write the results into the database"""
    fc = FusionCenter()

    # Get all previous hypotheses from the database
    h = FusionHypothesis.query.all()
    hs = FusionHypothesisSchema(many=True)
    ho = hs.dump(h).data

    # Get all mappings from the database
    m = BirdMapping.query.all()
    ms = BirdMappingSchema(many=True)
    mo = ms.dump(m).data

    # Create a hypotheses dataframe
    # make sure the datetime is correct
    # and convert to fusion centre hypotheses
    df = pd.DataFrame(ho)
    hypotheses = []
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        ts = df["timestamp"].drop_duplicates().nlargest(1)

        if ts.empty:
            return

        df = df[df["timestamp"] > ts.iloc[-1]]

        j = json.loads(df.to_json(orient="records"))
        hypotheses = [ToHypothesis(o, mo) for o in j]

    for i, s in enumerate(dataSet.data):
        time = s.timestamp
        # Assume we only get one measurement, for now

        position = np.array([x for x in s.position[1:-1].split(",")], dtype=np.float)

        # Create the classification array
        css = [0] * 19
        for c in s.classifications:
            css[c.bird_id] = c.probability

        for meas in s.measurements:
            bearing = Bearing(position, meas.angle, meas.deviation)
            hypotheses = fc.update(time, hypotheses, bearing, css)

        # Calculate time diff between n and n+1
        if i + 1 <= len(dataSet.data):
            break

        # Predict each second over all hypotheses
        loop_time = time
        while True:
            if loop_time + datetime.timedelta(
                0, 1
            ) > datetime.datetime.fromtimestamp(dataSet.data[i + 1].timestamp):
                break

            hypotheses = fc.prediction(loop_time, hypotheses)
            loop_time += datetime.timedelta(0, 1)

    # Write finished data into database
    for h in hypotheses:
        ccode = ""
        for mapp in mo:
            if mapp["vec_id"] == h.classification:
                ccode = mapp["id"]
                break

        posStr = np.array2string(h.x, precision=4, separator=",")
        covStr = np.array2string(h.P, precision=4, separator=",")

        fh = FusionHypothesis(
            response_id=0,
            weight=h.w,
            position=posStr,
            covariance=covStr,
            code=ccode,
            timestamp=h.timestamp,
        )
        db.session.add(fh)

    db.session.commit()


@bp.route("data", methods=["POST"])
def postData():
    """ Accepts new data to be sent to the fusion algorithm.
        Format: {
            pi_id: <int>,
            timestamp: <datetime>,
            position: <string> in format "[x,y]",
            measurements: [
                {
                    angle: <float>,
                    deviation: <float>,
                    sig_pow: <float>,
                    snr: <float[4]> // as string
                },
                ...
            ],
            classifications: [
                {
                    bird_id: <int>,
                    probability: <float>,
                },
                ...
            ]
        }
    """
    app.logger.info("Posting data into database")

    if not request.json:
        return errors.bad_request("No json present")

    # Convert json into db object
    schema = DataSetSchema(many=True)
    dataSet = schema.load(request.json, db.session)

    # Make sure no errors have occurred while serializing
    if dataSet.errors:
        return errors.error_response(400,
            "{} error(s) occurred".format(len(dataSet.errors)),
            dataSet.errors
        )  # noqa: E501

    # Add data to db
    for s in dataSet.data:
        db.session.add(s)
    db.session.commit()
    # ToDo: Abort if commit fails

    # Use Flask-Executor to start long running background task
    # FuseData(dataSet)
    exe.submit(FuseData, dataSet)  # Doesn't work in localhost mode, as SQLite wants the same thread

    # Return the data added to the db to the user
    return schema.jsonify(dataSet.data), 201


@bp.route("data/fused", methods=["GET"])
def getFusedData():
    """ Returns the fused data from the database. """
    data = FusionHypothesis.query.all()
    schema = FusionHypothesisSchema(many=True, exclude=("id"))  # noqa: E501
    output = schema.dump(data).data

    return jsonify(output), 200


@bp.route("data/raw", methods=["GET"])
def getRawData():
    """ Returns the raw data from the database """
    app.logger.info("Making GET Request against database")
    sets = DataSet.query.all()
    schema = DataSetSchema(many=True)
    output = schema.dump(sets).data
    return jsonify(output)


@bp.route("birds", methods=["GET"])
def getBirds():
    """Get the birds and the total amount of each one of them"""
    app.logger.info("Requesting general bird data from database")

    app.logger.debug("Make database query")
    data = FusionHypothesis.query.all()
    schema = FusionHypothesisSchema(many=True)
    output = schema.dump(data).data

    app.logger.debug("Sum bird amount")
    df = pd.DataFrame(output)
    if df.empty:
        return jsonify([])
    
    df_sum = df.groupby("code")["weight"].sum()
    

    app.logger.debug("Create response object")
    j = json.loads(df_sum.to_json(orient="columns"))
    return jsonify(j)


@bp.route("birds/<string:birdId>", methods=["GET"])
def getBirdDetails(birdId):
    """ Gets the details of a bird with given id
        Response:
        {
            "id": <string>,
            "overall_amount: <int>,
            "hour_amount: [int] 24x1
        }
    """
    # Get all hypotheses from database
    hypotheses = FusionHypothesis.query.filter_by(code=birdId)
    hypothesesSchema = FusionHypothesisSchema(many=True)
    hypothesesData = hypothesesSchema.dump(hypotheses).data

    # Create data frame from hypotheses
    df = pd.DataFrame(hypothesesData)
    if df.empty:
        import datetime
        nullData = [
            {
                "code": birdId,
                "position": "[0,0]",
                "timestamp": datetime.datetime.utcnow(),
                "weight": 0,
            }
        ]
        df = pd.DataFrame(nullData)

    # Calculate overall amount of bid
    df_sum = df.groupby("code")["weight"].sum()

    # Make sure the timestamp is an actual datetime object
    df["timestamp"] = df[["timestamp"]].apply(pd.to_datetime)

    # Sum up all weights each hour,
    # i.e. how many birds are counted each hour
    hs = pd.Series(range(24))
    pt = df.pivot_table(
        index=df["timestamp"].dt.hour,
        columns="code",
        values="weight",
        aggfunc="sum",
    )

    # Fill up data with missing hours
    o = pd.concat([hs, pt], axis=1, sort=True)
    o = o.drop(o.columns[0], axis=1).fillna(0)
    birdsPerHourData = json.loads(o.to_json(orient="columns"))

    # extract a bird series to return
    details = pd.DataFrame(
        dict(amount=df_sum, per_hour=birdsPerHourData)
    ).iloc[0]

    return jsonify(json.loads(details.to_json(orient="columns")))
