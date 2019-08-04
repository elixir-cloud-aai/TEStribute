"""
Functions to compute costs associated with tasks
"""
from collections import defaultdict
import logging
from typing import Dict

from distance import return_distance

logger = logging.getLogger("TEStribute")


def transfer_costs(total_cost, tes_url: "string", rate: Dict, drs: Dict, size: "float"):
    """
    :param tes_url: string of the tes uri endpoint
    :param rate: Dict rate in format {"rate":,"currency:} rate in units per 1000 km
    :param drs: Dict of access methods
    :param size: Size of the drs object
    :return: Ordered dict of costs for the object according to cost
    """
    # considering more than one "access_methods" are provided
    for accessinfo in drs:
        distance = return_distance(accessinfo["url"], tes_url)
        cost = float(size << 30) * distance["distance"] * rate["amount"]
        accessinfo["cost"] = {cost, rate["currency"]}
        if rate["currency"] == total_cost["currency"]:
            accessinfo["total_cost"] = total_cost["amount"] + cost
        # TODO:
        # implement the else
    return accessinfo


def sum_costs(
    total_costs, data_transfer_rate: Dict, drs_objects_locations: Dict, tes_url: str
) -> Dict:
    """
    :param total_costs: the total cost according to computational cost requirements given to the TES endpoint
    :param data_transfer_rate: cost from TES
    :param drs_data: Dict contaning
    :param tes_url: url of the TES service w.r.t which drs is being computed

    :return:
    """
    obj_size = defaultdict(dict)
    drs_info = defaultdict(dict)
    for obj_id, drs_uris in drs_objects_locations.items():
        # TO-DO:
        # consider the access method headers as well as checksums before cost estimation
        for drs_uri, access_info in drs_uris.items():
            # TO-DO:
            # look into checksums here & headers too for DRS services
            drs_info[obj_id][drs_uri] = [
                access_url["access_url"] for access_url in access_info["access_methods"]
            ]
            obj_size[obj_id][drs_uri] = access_info["size"]

    return_info = defaultdict(dict)
    for drs_id, drs_info in drs_info.items():
        for drs_uri, object_info in drs_info.items():
            return_info[drs_id][drs_uri] = transfer_costs(
                total_costs,
                tes_url,
                data_transfer_rate,
                object_info,
                obj_size[drs_id][drs_uri],
            )
    return return_info
