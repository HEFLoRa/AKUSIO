# Written by Gerd Mund & Robert Logiewa

from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def error_response(status_code, message=None, error_list=None):
    """Create an error response with the given HTTP status code."""
    
    payload = {
        "status_code": HTTP_STATUS_CODES.get(status_code, "Unknown error")
    }

    if message:
        payload["message"] = message

    if error_list:
        payload["error_list"] = error_list

    response = jsonify(payload)
    response.status_code = status_code
    return response


# Define common errors
def bad_request(message):
    """Create a bad request error with the given message"""
    return error_response(400, message)


def not_found():
    """Create a not found error"""
    return error_response("The requested resource couldn't be found.")