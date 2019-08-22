"""
Utitity functions for simplications and data structure conversions.
"""
from typing import Dict


def get_valid_service_combinations(
    task_info: Dict,
    object_info: Dict,
) -> Dict:
    """
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
    return {}
