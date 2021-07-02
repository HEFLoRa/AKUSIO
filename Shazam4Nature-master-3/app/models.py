# Written by Gerd Mund & Robert Logiewa

from app import db, ma
from marshmallow_sqlalchemy import field_for

# Defines the mappings from and to
# input data, python objects and database schema

class BirdMapping(db.Model):
    __tablename__ = "bird_mappings"
    id = db.Column(db.String(10), primary_key=True)
    vec_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(250))
    file = db.Column(db.String(250))


class DataSet(db.Model):
    __tablename__ = "data_set"
    id = db.Column(db.Integer, primary_key=True)
    pi_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True)
    position = db.Column(db.String(255))
    measurements = db.relationship(
        "Measurement", backref="data_set", lazy=True
    )  # noqa: E501
    classifications = db.relationship(
        "Classification", backref="data_set", lazy=True
    )  # noqa: E501


class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(
        db.Integer, db.ForeignKey("data_set.id"), nullable=False
    )
    angle = db.Column(db.Float)
    deviation = db.Column(db.Float)
    sig_pow = db.Column(db.Float)
    snr = db.Column(db.String(50))


class Classification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(
        db.Integer, db.ForeignKey("data_set.id"), nullable=False
    )
    bird_id = db.Column(db.Integer)
    probability = db.Column(db.Float)


class FusionHypothesis(db.Model):
    __tablename__ = "fusion_hypotheses"

    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    position = db.Column(db.String(50), nullable=False)
    covariance = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, index=True)


class BaseSchema(ma.ModelSchema):
    class Meta:
        sqla_session = db.session


class BirdMappingSchema(BaseSchema):
    id = field_for(BirdMapping, "id")

    class Meta(BaseSchema.Meta):
        model = BirdMapping


class FusionHypothesisSchema(BaseSchema):
    id = field_for(FusionHypothesis, "id", dump_only=False)

    class Meta(BaseSchema.Meta):
        model = FusionHypothesis


class DataSetSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = DataSet

    measurements = ma.Nested("MeasurementSchema", many=True)
    classifications = ma.Nested("ClassificationSchema", many=True)
    id = field_for(DataSet, "id", dump_only=False)


class MeasurementSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Measurement

    id = field_for(Measurement, "id", dump_only=False)


class ClassificationSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Classification

    id = field_for(Classification, "id", dump_only=False)
