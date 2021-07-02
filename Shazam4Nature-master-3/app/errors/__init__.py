# Written by Gerd Mund & Robert Logiewa

from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.errors import handlers
