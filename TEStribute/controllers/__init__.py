"""
Controller for `POST /rank-services` endpoint.
"""
from flask import Response
from werkzeug.exceptions import (BadRequest, InternalServerError, Unauthorized)

from TEStribute import rank_services as rank
from TEStribute.decorators import auth_token_optional
from TEStribute.errors import (ResourceUnavailableError, ValidationError)


@auth_token_optional
def rank_services(
    body,
    *args,
    **kwargs
) -> Response:
    """
    Rank services.

    :param body: Content of POST body, must conform to schema.

    :raises BadRequest: Request does not conform to schema or required external
            resources cannot be accessed.
    :raises Unauthorized: The user is not authorized to use the service.
    :raises InternalServiceError: An unknown error occurred.
    """
    # Handle JWT
    if "jwt" in kwargs:
        jwt=kwargs["jwt"]
    else:
        jwt=None
    # Rank services
    try:
        return rank(
            drs_ids=body.get("drs_ids"),
            drs_uris=body.get("drs_uris"),
            mode=body.get("mode"),
            resource_requirements=body.get("resource_requirements"),
            tes_uris=body.get("tes_uris"),
            jwt=jwt,
        ).to_dict()
    except ValidationError as e:
        raise BadRequest(e.args) from e
    except ResourceUnavailableError as e:
        raise BadRequest(e.args) from e
    except Unauthorized as e:
        raise Unauthorized(e.args) from e
    except Exception as e:
        raise InternalServerError(e.args) from e
