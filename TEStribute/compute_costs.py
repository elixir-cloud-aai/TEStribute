"""
Functions to compute costs associated with tasks
"""
import logging
from typing import Dict

from distance import return_distance


def transfer_costs(rate: Dict, drs: Dict, tes_url="string"):
    """
    :return: Transfer costs for data (either to or from the DRS)
    """
    # rate is per km per GB
    distance = 0  # km
    size = 0  # bytes

    # to-do :
    #  implement such that different data objects from different drs
    #  based on the weightage we get to cost & time as input
    for obj_id, info in drs.items():
        location_info = return_distance(
            info["access_methods"][0]["access_url"]["url"], tes_url
        )
        distance = distance + location_info["distance"]
        size = size + info["size"]
    cost = float(size << 30) * distance * rate["amount"]
    return {cost, rate["currency"]}


def sum_costs(
        total_costs, data_transfer_rate: Dict, drs_data: Dict, tes_url: str
        )-> Dict:
    """
    :param total_costs:
    :param data_transfre_rate: cost from TES
    :param drs_data:
    :param tes_url: url of the TES service w.r.t which drs is being computed
    :return:
    """
    # get logger
    logger = logging.getLogger("TES_logger")

    drs_costs = {}
    for drs_url, object_info in drs_data.items():
        drs_costs[drs_url] = transfer_costs(data_transfer_rate, object_info, tes_url)

    # to-do :
    #  check for currency
    response = drs_costs
    response["tes_costs"] = total_costs
    logger.debug("costs for tes_url " + tes_url + "are :"+str(response))
    return response
