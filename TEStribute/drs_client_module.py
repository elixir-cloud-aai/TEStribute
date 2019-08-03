"""
Functions that interact with the DRS service
"""
import logging

from typing import Dict, List, Set, Tuple, Union

from bravado.exception import HTTPNotFound
from drs_client import Client

logger = logging.getLogger("TEStribute")


def check_data_object(drs_id: str, drs_uris: Union[List, Set, Tuple]) -> Dict:
    """
    :param drs_uris:
    :param drs_id:

    :return: dict containing the uris at with the drs objects can be found
    """
    options_available = {}
    for drs_url in drs_uris:
        client = Client.Client(drs_url)
        # TO-DO : cross check checksum for object
        access_options = fetch_data_object(client, drs_id)
        if access_options != {}:
            options_available[drs_url] = access_options

    if options_available == {}:
        logger.warning(drs_id + " unavailable at all given instances")
        return {}

    # TO-DO: log_in different lines
    logger.info(drs_id + " is available at :")
    for drs_uri in list(options_available.keys()):
        logger.info("- {drs}".format(drs=drs_uri))
    return options_available


def fetch_data_object(client: Client, object_id: str) -> Dict:
    """
    :param client: bravado client configured for drs
    :param object_id: object id needed

    :return: a dict with access information for the url or
             empty dict

    """
    try:
        response = client.GetObject(object_id)
        response_dict = response._as_dict()
        return {
            "access_methods": response_dict["access_methods"],
            "checksums": response_dict["checksums"],
            "size": response_dict["size"]
        }
    except HTTPNotFound:
        return {}
