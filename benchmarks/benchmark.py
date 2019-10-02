"""
Module to setup TES and DRS instances as mentioned in config yaml file
"""
import os
import yaml

import logging
from typing import Dict

from bravado.exception import HTTPInternalServerError

from drs_client import Client as drs_cli
from tes_client import Client as tes_cli

from TEStribute.log import log_yaml
from TEStribute.log import setup_logger
from TEStribute import rank_services


log_file = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "log", "benchmarks.log")
)
logger = setup_logger("TEStribute_benchmarks", log_file, logging.DEBUG)

def setup_drs(uri: str, objects: Dict):
    """
    :param uri: sting uri for the service to be updated
    :param objects: list of objects that the db should be populated with
    """
    drs_client = drs_cli(uri)
    drs_client.updateDatabaseObjects(objects,False)
    return "updated"


def setup_tes(uri: str, costs: Dict):
    """
    :param uri: sting uri for the service to be updated
    :param costs: values that the config should be populated with
    """
    tes_client = tes_cli(uri)
    tes_client.updateTaskInfoConfig(costs["currency"],costs["unit_costs"])
    return "updated"


def setup_env(config_id: str):
    """
    :param config_id: id of file in the benchmarks folder according to which the config's of services should be setup
    :return: Dict that can be passed as input to the TEStribute.rank_server() directly
    """

    path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),"benchmark_configs/"+config_id))
    setup_dict = yaml.safe_load(open(path))

    try:
        drs_uris = setup_dict["drs_uris"]
        for uri in drs_uris:
            try:
                setup_drs(uri, drs_uris[uri])
            except KeyError :
                logger.info("No changes made to default config" + uri)
            except HTTPInternalServerError:
                logger.info("Update endpoint not accessed :"+ uri)
    except KeyError:
        print("No DRS uris provided")

    try:
        tes_uris = setup_dict["tes_uris"]
        for uri in tes_uris:
            try:
                setup_tes(uri, tes_uris[uri])
            except KeyError:
                logger.info("No changes made to default config for " + uri)
            except HTTPInternalServerError:
                logger.info("Update endpoint not accessed :" + uri)
    except KeyError:
        logger.info("No TES uris provided")

    return {
        "object_ids": setup_dict["object_ids"],
        "resource_requirements": setup_dict["resource_requirements"],
        "tes_uris": list(tes_uris.keys()),
        "drs_uris":list(drs_uris.keys()),
        "mode": setup_dict["mode"],
        "auth_header": setup_dict["auth_header"],
    }
