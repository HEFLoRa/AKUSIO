# Written by Gerd Mund & Robert Logiewa

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_bootstrap import Bootstrap
import os
import logging
from logging.handlers import RotatingFileHandler
from config import Config
from flask_executor import Executor

# Create the various modules
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
bootstrap = Bootstrap()
exe = Executor()

# Initialize modules and main app 
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    bootstrap.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    exe.init_app(app)

    # Error routes
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # Main routes, may need to be refactored into own module
    from app.main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix=r"/")

    # Api routes
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix=r"/api/v1")

    # Logging setup if not in debug
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/s4n.log', maxBytes=10240, backupCount=10)  # noqa: E501
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Shazam 4 Nature startup')

    return app

from app import models  # noqa: E402, F401
