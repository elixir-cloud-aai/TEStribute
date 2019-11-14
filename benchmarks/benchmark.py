#!/usr/bin/env python3

"""
Module to setup TES and DRS instances as mentioned in config yaml file
"""
import logging
import os
import sys
from typing import (Dict, List)
import yaml

from bravado.exception import HTTPInternalServerError
import hiyapyco

from drs_client import Client as drs_cli
from tes_client import Client as tes_cli

from TEStribute.log import log_yaml
from TEStribute.log import setup_logger
from TEStribute import rank_services

logger = setup_logger("TEStribute_benchmarks", logging.DEBUG)


def setup_drs(uri: str, objects: Dict):
    """
    :param uri: sting uri for the service to be updated
    :param objects: list of objects that the db should be populated with
    """
    drs_client = drs_cli(uri)
    drs_client.updateDatabaseObjects(
        objects=objects,
        clear_db=True
    )


def setup_tes(uri: str, costs: Dict):
    """
    :param uri: sting uri for the service to be updated
    :param costs: values that the config should be populated with
    """
    tes_client = tes_cli(uri)
    tes_client.updateTaskInfoConfig(
        costs["currency"],
        costs["unit_costs"]
    )


def setup_env(benchmarks: List[str]):
    """
    :param config_id: id of file in the benchmarks folder according to which the config's of services should be setup
    :return: Dict that can be passed as input to the TEStribute.rank_server() directly
    """

    # Load benchmark
    names = " ".join(benchmarks)
    logger.info(f"Running benchmark: {names}")
    paths = []
    for benchmark in benchmarks:
        paths.append(
            os.path.abspath(
                os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    "benchmarks",
                    str(benchmark),
                )
            )
        )
    setup_dict = hiyapyco.load(
        paths,
        method=hiyapyco.METHOD_MERGE,
        usedefaultyamlloader=True,
        failonmissingfiles=True,
    )
    logger.debug(f"Benchmark config loaded.")

    # Setup DRS instances
    # TODO: Validate successful update
    try:
        for uri, values in setup_dict["drs_uris"].items():
            try:
                logger.debug(f"Configuring DRS instance '{uri}'...")
                setup_drs(uri, values)
            except HTTPInternalServerError:
                logger.warning(
                    f"Update endpoint at service '{uri}' could not be accessed."
                )
            except Exception:
                logger.warning(
                    f"No changes made to default config for service '{uri}'."
                )
    except KeyError:
        logger.warning(
            "No DRS URIs provided. No changed made to default configs."
        )

    # Setup TES instances
    # TODO: Validate successful update
    try:
        for uri, values in setup_dict["tes_uris"].items():
            try:
                logger.debug(f"Configuring TES instance '{uri}'...")
                setup_tes(uri, values)
            except HTTPInternalServerError:
                logger.warning(
                    f"Update endpoint at service '{uri}' could not be accessed."
                )
            except Exception:
                logger.warning(
                    f"No changes made to default config for service '{uri}'."
                )
    except KeyError:
        logger.warning(
            "No DRS URIs provided. No changed made to default configs."
        )

    return {
        "object_ids": setup_dict["object_ids"],
        "resource_requirements": setup_dict["resource_requirements"],
        "tes_uris": list(setup_dict["tes_uris"].keys()),
        "drs_uris": list(setup_dict["drs_uris"].keys()),
        "mode": setup_dict["mode"],
        "jwt": setup_dict["jwt"],
    }


if __name__ == "__main__":
    benchmarks = sys.argv[1:]
    params = setup_env(benchmarks=benchmarks)
    # TODO: alternatively use HTTP service
    rank_services(**params)
