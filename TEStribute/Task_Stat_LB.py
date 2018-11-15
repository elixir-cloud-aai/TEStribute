import collections
import tes
import pprint

from typing import List

TIMEOUT = 2
RUNNING_TASK_PATH = "v1/tasks"
ACTIVE_STATE = ["QUEUED", "INITIALIZING", "RUNNING"]

class Task_Stat_LB():
    def __init__(self):
        pass

    def order_endpoints(self, endpoints: List[str], token: str=None) -> List[str]:
        """
        Creates a ordered list of endpoints based on active tasks on node. This is just a naive implementation since there
        is currently no way to get the actual resource usage and availability from a given TES endpoint
        :param endpoints:
        :param token:
        :return:
        """
        endpoint_stats = {}
        for endpoint in endpoints:
            endpoint_stats[endpoint] = 0

            cli = tes.HTTPClient(endpoint, timeout=TIMEOUT, token=token)
            response = cli.list_tasks()
            for task in response.tasks:
                if task.state in ACTIVE_STATE:
                    endpoint_stats[endpoint] = endpoint_stats[endpoint] + 1
        ordered_endpoints = collections.OrderedDict(sorted(endpoint_stats.items(), key=lambda x: x[1]))
        sorted_list = list(ordered_endpoints.keys())

        return sorted_list

