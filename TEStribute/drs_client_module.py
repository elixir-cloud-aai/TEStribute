""" Contains all functions to interact with the DRS
"""
from typing import Dict, List, Set, Tuple, Union
from bravado.exception import HTTPNotFound

from drs_client import Client


def fetch_data_object(client, object_id) -> Dict:
    """
    :param client: bravado client configured for drs
    :param object_id: object id needed

    :return: dict with information of the object id specified or
             raises bravado.exception for 404, resource not found
    """
    response = client.GetObject(object_id)
    response_dict = response._as_dict()
    return response_dict


def check_data_objects(drs_url: str, required_files: Union[List, Set, Tuple]) -> Dict:
    """
    :param drs_url: url at witch the Data Repository Service is Active
    :param required_files: an iterable object containing the object_id fields of data objects needed

    :return: should return the status of the data objects, access at the endpoint &
             the data if all objects exist
    """
    client = Client.Client(drs_url)
    objects_info = {}

    try:
        for obj_id in required_files:
            objects_info[obj_id] = fetch_data_object(client, obj_id)
    except HTTPNotFound:
        return {}

    return objects_info
