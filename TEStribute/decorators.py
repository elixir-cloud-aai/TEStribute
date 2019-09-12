"""Custom decorators."""

from connexion import request
from flask import current_app
from functools import wraps
import logging
from typing import Callable

from werkzeug.exceptions import Unauthorized

from TEStribute.security.process_jwt import JWT

logger = logging.getLogger("TEStribute")


def auth_token_optional(fn: Callable) -> Callable:
    """
    The decorator protects an endpoint from being called without a valid
    authorization token.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):

        # Check if authentication is enabled
        if current_app.config["security"]["authorization_required"]:

            try:
                jwt = JWT(request=request)
                jwt.validate()
                jwt.get_user()
            except Exception as e:
                raise Unauthorized(e.args) from e

            # Return wrapped function with token data
            return fn(
                jwt=jwt.jwt,
                claims=jwt.claims,
                user_id=jwt.user,
                *args,
                **kwargs
            )

        # Return wrapped function without token data
        else:
            return fn(*args, **kwargs)

    return wrapper
