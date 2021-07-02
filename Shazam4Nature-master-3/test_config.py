from config import Config
import os

basedir = os.path.abspath(os.path.dirname(__file__))
class TestConfig(Config):
    # SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "app.db")  # noqa: E501
    