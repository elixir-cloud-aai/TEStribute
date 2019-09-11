"""
Custom errors, error handler functions and function to register error handlers
with a Connexion app instance.
"""
import logging

from connexion import App
from connexion.exceptions import ExtraParameterProblem
from flask import Response
from json import dumps
from werkzeug.exceptions import (BadRequest, InternalServerError)

logger = logging.getLogger("TEStribute")


def register_error_handlers(app: App) -> App:
    """Adds custom handlers for exceptions to Connexion app instance."""
    # Add error handlers
    app.add_error_handler(BadRequest, handle_bad_request)
    app.add_error_handler(ExtraParameterProblem, handle_bad_request)
    app.add_error_handler(InternalServerError, handle_internal_server_error)
    logger.info('Registered custom error handlers with Connexion app.')

    # Workaround for adding a custom handler for `connexion.problem` responses
    # Responses from request and paramater validators are not raised and
    # cannot be intercepted by `add_error_handler`; see here:
    # https://github.com/zalando/connexion/issues/138
    @app.app.after_request
    def _rewrite_bad_request(response):
        if (
            response.status_code == 400 and
            response.data.decode('utf-8').find('"title":') is not None and
            "detail" in response.json
        ):
            response = handle_bad_request_validation(response)
        return response
    
    return app


# Custom error handlers
def handle_bad_request_validation(response: Response) -> Response:
    return Response(
        response=dumps({
            'code': int(response.status_code),
            'errors': [{
                'reason': response.json["title"].replace(" ", ""),
                'message': [
                    response.json["detail"],
                ],
            }],
            'message': "The request could not be processed.",
        }),
        status=400,
        mimetype="application/problem+json",
    )


def handle_bad_request(exception: BadRequest) -> Response:
    return Response(
        response=dumps({
            'code': int(exception.code),
            'errors': [{
                'reason': str(exception.__class__).split("'")[1],
                'message': [
                    exception.description,
                ],
            }],
            'message': "The request could not be processed.",
        }),
        status=400,
        mimetype="application/problem+json",
    )


def handle_internal_server_error(exception: Exception) -> Response:
    return Response(
        response=dumps({
            'code': '500',
            'errors': [],
            'message': 'An unexpected error occurred.',
            }),
        status=500,
        mimetype="application/problem+json",
    )
