#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Written by Gerd Mund & Robert Logiewa

from app import create_app, db
import app.models as mdl


# Main app entry point
app = create_app()

# Werkzeug helper for creating dummy data
@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "data_set": mdl.DataSet,
        "measurement": mdl.Measurement,
        "classification": mdl.Classification,
        "fusion_hypotheses": mdl.FusionHypothesis,
        "bird_mappings": mdl.BirdMapping,
    }


@app.cli.command("init-dummy-data")
def initDummyData():
    import datetime

    # Raw dummy data
    c1 = mdl.Classification(id=1, set_id=1, bird_id=0, probability=0.75)
    c2 = mdl.Classification(id=2, set_id=1, bird_id=0, probability=0.341)
    c3 = mdl.Classification(id=3, set_id=1, bird_id=2, probability=0.42)

    m1 = mdl.Measurement(
        id=1, set_id=1, angle=0.3, deviation=0.5, sig_pow=6.5, snr="[5.6, 1.2, 6.7, 8.3]"  # noqa: E501
    )
    m2 = mdl.Measurement(
        id=2, set_id=1, angle=0.8, deviation=0.2, sig_pow=1.9, snr="[8.4, 4.0, 3.9, 7.3]"  # noqa: E501
    )

    d = mdl.DataSet(
        id=1,
        pi_id=1,
        timestamp=datetime.datetime.utcnow(),
        position="[0,0]",
        measurements=[m1, m2],
        classifications=[c1, c2, c3],
    )
    db.session.add(d)

    # Fusion response dummy data
    h1 = mdl.FusionHypothesis(
        id=1,
        response_id=1,
        weight=0.6,
        position="[0,0]",
        covariance="[[0,0],[0,0]",
        code="BC",
        timestamp=datetime.datetime.utcnow(),
    )
    h2 = mdl.FusionHypothesis(
        id=2,
        response_id=1,
        weight=0.3,
        position="[0,0]",
        covariance="[[0,0],[0,0]",
        code="PSF",
        timestamp=datetime.datetime.utcnow(),
    )
    db.session.add(h1)
    db.session.add(h2)

    db.session.commit()


@app.cli.command("init-database")
def initDatabase():
    from app.models import BirdMappingSchema

    birdCodeMapping = [
        {
            "id": "BC",
            "name": "Brown Creeper",
            "file": "brown_creeper",
            "vec_id": 0,
        },
        {
            "id": "PW",
            "name": "Pacific Wren",
            "file": "pacific_wren",
            "vec_id": 1,
        },
        {
            "id": "PSF",
            "name": "Pacific-slope Flycatcher",
            "file": "pacific-slope_flycatcher",
            "vec_id": 2,
        },
        {
            "id": "RBN",
            "name": "Red-breasted Nuthatch",
            "file": "red-breasted_nuthatch",
            "vec_id": 3,
        },
        {
            "id": "DEJ",
            "name": "Dark-eyed Junco",
            "file": "dark-eyed_junco",
            "vec_id": 4,
        },
        {
            "id": "OSF",
            "name": "Olive-sided Flycatcher",
            "file": "olive-sided_flycatcher",
            "vec_id": 5,
        },
        {
            "id": "HT",
            "name": "Hermit Thrush",
            "file": "hermit_thrush",
            "vec_id": 6,
        },
        {
            "id": "CBC",
            "name": "Chestnut-backed Chickadee",
            "file": "chestnut-backed_chickadee",
            "vec_id": 7,
        },
        {
            "id": "VT",
            "name": "Varied Thrush",
            "file": "varied_thrush",
            "vec_id": 8,
        },
        {
            "id": "HW",
            "name": "Hermit Warbler",
            "file": "hermit_warbler",
            "vec_id": 9,
        },
        {
            "id": "ST",
            "name": "Swaisons Thrush",
            "file": "swaisons_thrush",
            "vec_id": 10,
        },
        {
            "id": "HF",
            "name": "Hammond's Flycatcher",
            "file": "hammonds_flycatcher",
            "vec_id": 11,
        },
        {
            "id": "WT",
            "name": "Western Tanager",
            "file": "western_tanager",
            "vec_id": 12,
        },
        {
            "id": "BHG",
            "name": "Black-headed Grosbreak",
            "file": "black-headed_grosbeak",
            "vec_id": 13,
        },
        {
            "id": "GCK",
            "name": "Golden-crowned Kinglet",
            "file": "golden-crowned_kinglet",
            "vec_id": 14,
        },
        {
            "id": "WV",
            "name": "Warbling Vireo",
            "file": "warbling_vireo",
            "vec_id": 15,
        },
        {
            "id": "MW",
            "name": "MacGillivray's Warbler",
            "file": "macgillivrays_warbler",
            "vec_id": 16,
        },
        {
            "id": "SJ",
            "name": "Stellar's Jay",
            "file": "stellars_jay",
            "vec_id": 17,
        },
        {
            "id": "CN",
            "name": "Common Nighthawk",
            "file": "common_nighthawk",
            "vec_id": 18,
        },
    ]

    schema = BirdMappingSchema(many=True)
    result = schema.load(birdCodeMapping, db.session).data
    for r in result:
        db.session.add(r)

    db.session.commit()
