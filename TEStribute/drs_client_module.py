"""
Functions that interact with the DRS service
"""
import logging

from typing import Dict, List, Set, Tuple, Union

from bravado.exception import HTTPNotFound
from drs_client import Client

logger = logging.getLogger("TEStribute")


def get_available_accessinfo(drs_url: str, drs_ids: Union[List, Set, Tuple]) -> Dict:
    """
    the function to return the available access information for a iterable object of drs_id's given at the DRS service
    at the specified url

    :param drs_uris:
    :param drs_id:

    :return: dict containing the uris at with the drs objects can be found
    """

    # TO-DO: incase drs is offline log & handle
    client = Client.Client(drs_url)
    objects_available = {}
    for drs_id in drs_ids:
        # TO-DO : cross check checksum for object
        access_options = fetch_object_metadata(client, drs_id)
        if access_options != {}:
            objects_available[drs_id] = access_options
    
    return objects_available


def fetch_object_metadata(client: Client, object_id: str) -> Dict:
    """
    Function uses the passed drs id & bravado client to return the object metadata ( limited to the requirements of the
    logic including the access information, checksums and size of the drs object given at the DRS the client is
    configured for)

    :param client: bravado client configured for drs
    :param object_id: object id needed

    :return: a dict with filtered response or empty dict in the case where object is not found
    """
    try:
        response = client.GetObject(object_id)
        response_dict = response._as_dict()
        return {
            "access_methods": response_dict["access_methods"],
            "checksums": response_dict["checksums"],
            "size": response_dict["size"],
        }
    except HTTPNotFound:
        return {}
