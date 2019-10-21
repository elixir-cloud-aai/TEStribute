"""
Custom errors, error handler functions and function to register error handlers
with a Connexion app instance.
"""
import logging
from typing import (Type, Union)

from connexion import App
from connexion.exceptions import ExtraParameterProblem
from flask import Response
from json import dumps
from werkzeug.exceptions import (BadRequest, InternalServerError, Unauthorized)

from TEStribute.decorators import log_exception

logger = logging.getLogger("TEStribute")


def register_error_handlers(app: App) -> App:
    """Adds custom handlers for exceptions to Connexion app instance."""
    # Add error handlers
    app.add_error_handler(BadRequest, handle_bad_request)
    app.add_error_handler(ExtraParameterProblem, handle_bad_request)
    app.add_error_handler(InternalServerError, handle_internal_server_error)
    app.add_error_handler(Unauthorized, handle_unauthorized)
    logger.info('Registered custom error handlers with Connexion app.')

    # Workaround for adding a custom handler for `connexion.problem` responses
    # Responses from request and paramater validators are not raised and
    # cannot be intercepted by `add_error_handler`; see here:
    # https://github.com/zalando/connexion/issues/138
    @app.app.after_request
    def _rewrite_bad_request(response: Response) -> Response:
        if (
            response.status_code == 400 and
            response.data.decode('utf-8').find('"title":') is not None and
            "detail" in response.json
        ):
            response = handle_bad_request_validation(response)
        return response

    return app


# Custom exceptions
class ValidationError(Exception):
    """Error raised for invalid input parameters."""

    def __init__(self, description: str, **kwargs):
        super(ValidationError, self).__init__(description, **kwargs)

class ResourceUnavailableError(Exception):
    """Error raised if a required resource is unavailable."""

    def __init__(self, description: str, **kwargs):
        super(ResourceUnavailableError, self).__init__(description, **kwargs)


@log_exception()
def handle_bad_request_validation(exception: Response) -> Response:
    return Response(
        response=dumps({
            'code': int(exception.status_code),
            'errors': [{
                'reason': exception.json["title"].replace(" ", ""),
                'message': [
                    exception.json["detail"],
                ],
            }],
            'message': "The request caused an error.",
        }),
        status=400,
        mimetype="application/problem+json",
    )


@log_exception()
def handle_bad_request(exception: BadRequest) -> Response:
    return Response(
        response=dumps({
            'code': int(exception.code),
            'errors': [{
                'reason': str(exception.__class__).split("'")[1],
                'message': exception.description,
            }],
            'message': "The request caused an error.",
        }),
        status=int(exception.code),
        mimetype="application/problem+json",
    )


@log_exception(tb=True)
def handle_internal_server_error(exception: InternalServerError) -> Response:
    return Response(
        response=dumps({
            'code': int(exception.code),
            'errors': [],
            'message': ['An unexpected error occurred.'],
            }),
        status=500,
        mimetype="application/problem+json",
    )


@log_exception()
def handle_unauthorized(exception: Unauthorized) -> Response:
    return Response(
        response=dumps({
            'code': int(exception.code),
            'errors': [{
                'reason': str(exception.__class__).split("'")[1],
                'message': exception.description,
            }],
            'message': "The request is unauthorized.",
        }),
        status=int(exception.code),
        mimetype="application/problem+json"
    )
