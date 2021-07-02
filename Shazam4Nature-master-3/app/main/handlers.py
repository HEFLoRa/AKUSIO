# Written by Gerd Mund & Robert Logiewa

from flask import (
    render_template,
    abort,
    current_app as app,
    json,
    make_response,
)
from app.main import bp
from app.api import handlers
import pandas as pd
from app.models import (
    DataSet,
    DataSetSchema,
    FusionHypothesis,
    FusionHypothesisSchema,
    BirdMapping,
    BirdMappingSchema,
)
from app.main import plotFunction as plt
import time

@bp.route("/")
@bp.route("/index")
def index():
    """ Index page, contains general results """
    app.logger.info("Opening index page")

    app.logger.debug("Retrieving data from birds api endpoint")
    response = handlers.getBirds()
    
    # Make sure the api returned actual results
    if not response or response.status_code != 200 or not response.is_json:
        app.logger.warning("birds api endpoint failed")
        abort(500)

    app.logger.debug("Retrieve bird mappings from database")
    mq = BirdMapping.query.all()
    ms = BirdMappingSchema(many=True)
    m = ms.dump(mq).data

    app.logger.debug("Combine mappings and data")
    mapping = pd.DataFrame(m).set_index("id")
    amounts = pd.DataFrame(response.get_json(), index=["weight"]).T
    data = pd.concat([amounts, mapping], axis=1, sort=True).fillna(0).T

    app.logger.debug("Finalize data for index page")
    birds_data = json.loads(data.to_json(orient="columns"))
    return (render_template("index.html", birdsData=birds_data), 200)


@bp.route("birds/<string:id>")
def bird_details(id):
    """ Shows the details of a particular bird """

    # Get bird details from api
    response = handlers.getBirdDetails(id)
    if not response or response.status_code != 200 or not response.is_json:
        abort(500)

    details = response.get_json()
    sd = pd.Series(details)

    # Filter the data based on the bird id
    m = BirdMapping.query.filter_by(id=id).first()
    ms = BirdMappingSchema()
    mo = ms.dump(m).data
    sm = pd.Series(mo)

    # Finalize data for details page
    df = pd.concat([sd, sm], axis=0)
    j = json.loads(df.to_json(orient="columns"))

    plt.calcPlot(j)
    return render_template("details.html", bird=j, title=j["name"])


@bp.route("dump_database", methods=["GET"])
def dumpDatabase():
    """Dumps the entirety of the database to a json file that is then downloaded"""
    
    # Query all bird mappings
    m = BirdMapping.query.all()
    ms = BirdMappingSchema(many=True)
    mo = ms.dump(m).data
        
    # Query all bird data
    d = DataSet.query.all()
    ds = DataSetSchema(many=True)
    do = ds.dump(d).data
    
    # Query all hypotheses
    h = FusionHypothesis.query.all()
    dh = FusionHypothesisSchema(many=True)
    ho = dh.dump(h).data
    
    # Make output object
    content = {"raw_data": do, "hypotheses": ho,  "mappings": mo}

    # Convert to json and then present file to user
    response = make_response(json.dumps(content))
    response.mimetype = "application/json"
    response.headers[
        "Content-Disposition"
    ] = "attachment;filename=database.json"
    return response
