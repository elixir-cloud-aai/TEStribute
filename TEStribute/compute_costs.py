"""
Functions to compute costs associated with tasks
"""
from collections import defaultdict
import logging
from typing import Dict

from distance import return_distance

logger = logging.getLogger("TEStribute")


def transfer_costs(tes_url: "string", rate: Dict, drs: Dict, size: "float"):
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
        cost = round(size / 1000000000000, 7) * distance["distance"] * rate["amount"]
        accessinfo["cost"] = cost
        accessinfo["currency"] = rate["currency"]

    return sorted(drs, key=lambda i: i["cost"])


def sum_costs(data_transfer_rate: Dict, drs_objects_locations: Dict, tes_url: str) -> Dict:
    """
    :param data_transfer_rate: cost from TES
    :param drs_objects_locations: Dict contaning
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
        sum_drs = 0
        for drs_uri, object_info in drs_info.items():
            # only the one with the lowest cost is kept
            return_info[drs_id][drs_uri] = transfer_costs(
                tes_url, data_transfer_rate, object_info, obj_size[drs_id][drs_uri]
            )[0]
            sum_drs = return_info[drs_id][drs_uri]["cost"] + sum
            currency = return_info[drs_id][drs_uri]["currency"]
            # check for currency needed
        return_info[drs_id] = sorted(
            return_info[drs_id].items(), key=lambda x: x[1]["cost"]
        )
        return_info.update({"drs_costs": {"amount": sum_drs, "currency": currency}})
    return return_info
