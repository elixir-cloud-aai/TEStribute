"""
exposes the function of TESTribute i.e the task distribution function
"""
import logging
from typing import Dict

from requests.exceptions import MissingSchema

from config.parse_config import config_parser

from compute_costs import sum_costs

from drs_client_module import check_data_objects
from tes_client_module import fetch_tasks_info

#to-do :
# configure the logger
logging.basicConfig(filename='test_logging.log',level=logging.DEBUG)


def rank_tasks(task: Dict, choice: str, choice_weight: float = 0.5) -> Dict:
    """
    :param task: dict of tes_task
    :param choice: choice between cost or time for optimisation
    :param choice_weight: weightage to choice
    :return: an ordered list of TES & DRS available endpoints in
    """
    # list available DRS & TES instances
    config = config_parser()

    # determine the type of order to return
    if choice.lower() not in ["cost", "time", "randomise"]:
        raise TypeError("should be one of : cost ,time or randomise")

    #
    try:
        resources = task["resources"]
    except KeyError:
        raise KeyError("task must contain resources")

    inputs = task["inputs"]
    outputs = task["outputs"]

    tes_services = config["tes-services"]
    drs_services = config["drs-services"]

    services = {}

    """
    loop though the DRS and TES to check for active services,
    check_data_objects to ensure the DRS endpoint has the required files
    get filesize & store 
    """
    usable_drs = {}
    for name, url in drs_services.items():
        available_data = check_data_objects(url, [x['name'] for x in inputs])
        if available_data != {}:
            usable_drs[url] = available_data

    for name, tes_url in tes_services.items():
        cpu_cores = resources["cpu_cores"]
        ram_gb = resources["ram_gb"]
        disk_gb = resources["disk_gb"]
        execution_time_min = resources["execution_time_min"]

        try:
            tasks_info = fetch_tasks_info(
                tes_url, cpu_cores, ram_gb, disk_gb, execution_time_min
            )
            cost = sum_costs(tasks_info['costs_total'],tasks_info['costs_data_transfer'], usable_drs, tes_url)
            #to-do :
            # save & order costs
            logging.info(cost)
            logging.debug("Cost for the TES is :" + str(cost))
        except MissingSchema:
            logging.error("Service not active " + name + "at" + url)


if __name__ == "__main__":
    rank_tasks(
        {
            "resources": {
                "cpu_cores": 2,
                "ram_gb": 4,
                "disk_gb": 8,
                "execution_time_min": 20,
            },
            "inputs": [
                {'name':'a001', 'url':''}
            ],
            "outputs": [
                {'name':'op1', 'url':'https://summerofcode.withgoogle.com/'},
                {'name':'op2', 'url':'https://stackoverflow.com'}
            ]
        },
        "cost",
        0.23,
    )
