"""
Functions that interact with the DRS service
"""
from collections import defaultdict
import logging
from typing import Dict, List, Union

from bravado.exception import HTTPNotFound
import drs_client
from requests.exceptions import ConnectionError, HTTPError, MissingSchema
from simplejson.errors import JSONDecodeError

from TEStribute.errors import ResourceUnavailableError

logger = logging.getLogger("TEStribute")


def fetch_drs_objects_metadata(
    drs_uris: List[str],
    drs_ids: List[str],
    check_results: bool = True,
    timeout: float = 3,
) -> Dict:
    """
    Returns access information for an iterable object of DRS identifiers
    available at the specified DRS instances.

    :param drs_uris: List (or other iterable object) of root URIs of DRS
            instances.
    :param drs_ids: List (or other iterable object) of globally unique DRS
            identifiers.
    :param check_results: Check whether every object is available at least at
            one DRS instance. Raises FileNotFoundError if not.
    :param timeout: Time (in seconds) after which an unsuccessful connection
            attempt to the DRS should be terminated.

    :return: Dict of dicts of DRS object identifers in `drs_ids` (keys outer
            dictionary) and DRS root URIs in `drs_uris` (keys inner
            dictionaries) and a dictionary containing the information defined by
            the `Object` model of the DRS specification (values inner
            dictionaries). The inner dictionary for any given DRS object will
            only contain values for DRS instances for which the object is
            available.
    """
    # Initialize results container
    result_dict = defaultdict(dict)

    # Iterate over DRS instances
    for drs_uri in drs_uris:

        # Fetch object metadata at current DRS instance
        metadata = _fetch_drs_objects_metadata(
            uri=drs_uri,
            ids=drs_ids,
            timeout=timeout,
        )

        # Add metadata for each object to results container, if available
        if metadata:
            for drs_id in metadata:
                result_dict[drs_id].update({
                    drs_uri: metadata[drs_id]
                })

        # Check whether any object is unavailable
        if check_results:

            # Check availability of objects
            for drs_id in drs_ids:
                if drs_id not in result_dict:
                    logger.error(
                        f"Object '{drs_id}' is not available at any of the " \
                        f"specified DRS instances."
                    )
                    raise ResourceUnavailableError(
                        f"Object '{drs_id}' is not available at any of the " \
                        f"specified DRS instances."
                    )

        # Return results
    return result_dict


def _fetch_drs_objects_metadata(
    uri: str,
    ids: List[str],
    timeout: float = 3,
) -> Dict:
    """
    Returns access information for an iterable object of DRS identifiers
    available at the specified DRS instance.

    :param uri: Root URI of DRS instance.
    :param ids: List (or other iterable object) of globally unique DRS
            identifiers.
    :param timeout: Time (in seconds) after which an unsuccessful connection
            attempt to the DRS should be terminated. Currently not implemented.

    :return: Dict of DRS object identifers in `ids` (keys) and a dictionary
            containing the information defined by the `Object` model of the DRS
            specification (values). Objects that are unavailable at the DRS
            instances will be omitted from the dictionary. In case of a
            connection error at any point, an empty dictionary is returned.
    """
    # Initialize results container
    objects_metadata = {}

    # Establish connection with DRS; handle exceptions
    try:
        client = drs_client.Client(uri)
    except TimeoutError:
        logger.warning(
            f"DRS unavailable: connection attempt to DRS '{uri}' timed out."
        )
        return {}
    except (
        ConnectionError,
        HTTPError,
        HTTPNotFound,
        JSONDecodeError,
        MissingSchema,
    ):
        logger.warning(
            f"DRS unavailable: the provided URI '{uri}' could not be " \
            f"resolved."
        )
        return {}

    # Fetch metadata for every object; handle exceptions
    for drs_id in ids:
        # TODO: Cross-check object checksums, die if differ
        # TODO: Cross-check object sizes, die if differ
        try:
            objects_metadata[drs_id] = client.getObject(
                drs_id
            )._as_dict()
        except HTTPNotFound:
            logger.debug(
                f"File '{drs_id}' is not available on DRS '{uri}'."
            )
            continue
        except TimeoutError:
            logger.warning(
                f"DRS unavailable: connection attempt to DRS '{uri}' timed " \
                f"out."
            )
            continue

    # Return object metadata
    return objects_metadata
