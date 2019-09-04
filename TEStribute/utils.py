"""
Utitity functions for simplifications and data structure conversions.
"""
from random import choice,shuffle

from typing import Dict

from TEStribute.access_tes import fetch_tes_task_info
from TEStribute.access_drs import fetch_drs_objects_metadata


def get_valid_service_combinations(task_info: Dict, object_info: Dict) -> Dict:
    """
    Should take the similar input to the rak_services and return any random list of usable TES & DRS services

    :task_info: Dict of the form
    :object_info: Dict of form drs_uri's and drs_id's
    :return: Dict of the form
            {
              "tes_uri": [ # list of combinations for this TES
                {
                  "a001": "object_uri",
                  "a002": "object_uri",
                  "output": "object_uri",
                }, {
                  "a001": "object_uri",
                  "a002": "object_uri",
                  "output": "object_uri",
                }
              ],
              "tes_uri": [ # list of combinations for other TES
                {
                  "a001": "object_uri",
                  "a002": "object_uri",
                  "output": "object_uri",
                }, {
                  "a001": "object_uri",
                  "a002": "object_uri",
                  "output": "object_uri",
                }
              ]
            }
    """
    tes_uris = task_info["tes_uris"]
    shuffle(tes_uris)
    tes_list = fetch_tes_task_info(tes_uris, task_info["resource_requirements"])

    drs_uris = object_info["drs_uris"]
    shuffle(drs_uris)
    drs_info = fetch_drs_objects_metadata(drs_uris,object_info["drs_ids"],False)

    return_dict = {}
    for tes_uri in tes_list:
        drs_dict = {}
        for obj_id in drs_info:
            print(list(drs_info[obj_id].keys()))
            drs_dict[obj_id] = choice(list(drs_info[obj_id].keys()))
        retrun_dict[tes_uri] = drs_dict

    return return_dict


"""
SAMPLE INPUT : 

        {
            "tes_uris": [
                "http://131.152.229.70/ga4gh/tes/v1/",
                "http://193.166.24.111/ga4gh/tes/v1/",
                "http://0.0.0.9101/ga4gh/tes/v1/",
            ],
            "resource_requirements": {
                "cpu_cores": 2,
                "execution_time_min": 300,
                "preemptible": True,
                "ram_gb": 8,
                "disk_gb": 10,
                "zones": [],
            },
        },
        {
            "drs_uris": [
                "http://0.0.0.0:9101/ga4gh/drs/v1/",
                "http://193.166.24.114/ga4gh/drs/v1/",
                "http://131.152.229.71/ga4gh/drs/v1/",
            ],
            "drs_ids": [
                "a001", "a002", "a006"
            ]
        },
    )
"""
