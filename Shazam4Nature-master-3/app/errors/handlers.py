# Written by Gerd Mund & Robert Logiewa

from flask import render_template
from app import db
from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    """Return a 404 error page"""
    db.session.rollback()
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    """Return a 500 error page"""
    db.session.rollback()
    return render_template('errors/500.html'), 500
