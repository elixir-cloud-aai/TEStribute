"""
Functions that interact with the TES service
"""
import logging
from typing import Dict, List

from bravado.exception import HTTPNotFound
from requests.exceptions import ConnectionError, HTTPError, MissingSchema
from simplejson.errors import JSONDecodeError
import tes_client
from werkzeug.exceptions import BadRequest

logger = logging.getLogger("TEStribute")


def fetch_tes_task_info(
    tes_uris: List[str],
    resource_requirements: Dict,
    check_results: bool = True,
    timeout: float = 3,
) -> Dict:
    """
    Given a set of resource requirements, returns queue time, cost estimates and
    related parameters at the specified TES instances.

    :param tes_uris: List (or other iterable object) of root URIs of TES
            instances.
    :param resource_requirements: Dict of compute resource requirements of the
            form defined in the `tesResources` model of the modified TES
            speficications in the `mock-TES` repository at:
            https://github.com/elixir-europe/mock-TES/blob/master/mock_tes/specs/schema.task_execution_service.d55bf88.openapi.modified.yaml
    :param check_results: Check whether the resulting dictionary contains data
            for at least one TES instance. Raises requests.exceptions.HTTPError
            if not.
    :param timeout: Time (in seconds) after which an unsuccessful connection
            attempt to the DRS should be terminated.

    :return: Dict of TES URIs in `tes_uris` (keys) and a dictionary containing
             queue time and cost estimates/rates (values) as defined in the
            `tesTaskInfo` model of the modified TES specifications in the
            `mock-TES` repository: https://github.com/elixir-europe/mock-TES
    """
    # Initialize results container
    result_dict = {}

    # Iterate over TES instances
    for uri in tes_uris:

        # Fetch task info at current TES instance
        task_info = _fetch_tes_task_info(
            uri=uri,
            resource_requirements=resource_requirements,
            timeout=timeout,
        )

        # If available, add task info to results container
        if task_info:
            result_dict[uri] = task_info
        
    # Check whether at least one TES instance provided task info
    if check_results and not result_dict:
        logger.error(
            "None of the specified TES instances provided any task info."
        )
        raise BadRequest(
            "None of the specified TES instances provided any task info."
        )
    
    # Return results
    return result_dict


def _fetch_tes_task_info(
    uri: str,
    resource_requirements: Dict,
    timeout: float = 3,
) -> Dict:
    """
    Given a set of resource requirements, returns queue time, cost estimates and
    related parameters at the specified TES instance.

    :param uri: Root URI of TES instance.
    :param resource_requirements: Dict of compute resource requirements of the
            form defined in the `tesResources` model of the modified TES
            speficications in the `mock-TES` repository at:
            https://github.com/elixir-europe/mock-TES/blob/master/mock_tes/specs/schema.task_execution_service.d55bf88.openapi.modified.yaml
    :param timeout: Time (in seconds) after which an unsuccessful connection
            attempt to the DRS should be terminated. Currently not implemented.

    :return: Dict of queue time and cost estimates/rates as defined in the
            `tesTaskInfo` model of the modified TES specifications in the
            `mock-TES` repository: https://github.com/elixir-europe/mock-TES

    """
    # Establish connection with TES; handle exceptions
    # TODO: Implement timeout
    try:
        client = tes_client.Client(uri)
    except TimeoutError:
        logger.warning(
            f"TES unavailable: connection attempt to '{uri}' timed out."
        )
        return {}
    except (ConnectionError, JSONDecodeError, HTTPNotFound, MissingSchema):
        logger.warning(
            f"TES unavailable: the provided URI '{uri}' could not be " \
            f"resolved."
        )
        return {}

    # Fetch task info; handle exceptions
    try:
        return client.getTaskInfo(
            timeout=timeout,
            **resource_requirements,
        )._as_dict()
    except TimeoutError:
        logger.warning(
            f"Connection attempt to TES {uri} timed out. TES " \
            f"unavailable. Skipped."
        )
        return {}
