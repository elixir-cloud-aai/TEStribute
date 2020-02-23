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
        security_conf = current_app.config["security"]  # type: ignore
        if security_conf["authorization_required"]:
            try:
                jwt = JWT(request=request)
            except Exception as e:
                raise Unauthorized(e.args) from e

            # Return wrapped function with token data
            return fn(
                jwt=jwt.jwt,
                *args,
                **kwargs
            )

        # Return wrapped function without token data
        else:
            return fn(*args, **kwargs)

    return wrapper


def log_exception(
    logger: logging.Logger = logger,
    level: int = logging.ERROR,
    tb: bool = False,
    n: int = 0,
) -> Callable:
    """
    When attached to an error handler, logs every error caught by the handler.

    :param logger: Logger object.
    """

    def decorator(fn: Callable) -> Callable:

        @wraps(fn)
        def wrapper(*args, **kwargs):

            # Log exception
            e = args[n]
            err = f"{e.code} {e.name}: {''.join(e.description)}"
            logger.log(level=level, msg=err, exc_info=tb)

            # Return wrapped function
            return fn(*args, **kwargs)

        return wrapper

    return decorator
