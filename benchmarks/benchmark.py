import os
import yaml

import logging
from typing import Dict

from drs_client import Client as drs_cli
from tes_client import Client as tes_cli

from TEStribute.log.logging_functions import setup_logger


# Set up logging
#log_file = os.path.abspath(
#    os.path.join(os.path.dirname(os.path.realpath(__file__)), "log", "testribute.log")
#)
#logger = setup_logger("TEStribute", log_file, logging.DEBUG)


def setup_drs(uri: 'string',objects: Dict):
    drs_client = drs_cli.Client(uri)
    drs_client.updateDatabaseObjects(False, objects)

    return "updated"


def setup_tes(uri: 'string',costs: Dict):
    tes_client = tes_cli.Client(uri)
    tes_client.updateTaskInfoConfig(costs["currency"],costs["time_unit"],costs["unit_costs"])

    return "updated"


def setup_env(config_id: str):
    path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),"benchmark_configs/"+config_id))
    setup_dict = yaml.safe_load(open(path))

    try:
        drs_uris = setup_dict["drs_uris"]
        try:
            for uri in drs_uris:
                setup_drs(uri, drs_uris[uri])
        except KeyError:
            print("No changes made to default config" + uri)
    except KeyError:
        print("No DRS uris provided")

    try:
        tes_uris = setup_dict["tes_uris"]
        try:
            for uri in tes_uris:
                setup_tes(uri, tes_uris[uri])
        except KeyError:
            print("No changes made to default config for " + uri)
    except KeyError:
        print("No TES uris provided")

    return{
        "drs_ids": setup_dict["drs_ids"],
        "resource_requirements": setup_dict["resource_requirements"],
        "tes_uris": list(tes_uris.keys()),
        "drs_uris":list(drs_uris.keys()),
        "mode": setup_dict["mode"],
        "auth_header": setup_dict["auth_header"],
    }


if __name__ == "__main__":
    setup_env("config1.yaml")

