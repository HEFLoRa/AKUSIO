# Written by Gerd Mund & Robert Logiewa

from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import handlers  # noqa: E402, F401
