# Written by Gerd Mund & Robert Logiewa

from flask import Blueprint

bp = Blueprint('main', __name__, static_folder="static")

from app.main import handlers  # noqa: E402, F401
