from typing import List, Dict

from TEStribute.Task_Stat_LB import Task_Stat_LB
from TEStribute.Endpoint_Checker import Endpoint_Checker
from TEStribute.LB_Algorithms import LB_Algorithms
from TEStribute.Random_LB import Random_LB


class TEStribute_Interface:
    def __init__(self):
        """
        Interface to order a list of TES endpoints by LB criteria.
        Available Algorithms can be found in :func:`TEStribute.LB_Algorithms.LB_Algorithms`
        """
        self.endpoint_checker = Endpoint_Checker()
        self.random_lb = Random_LB()
        self.task_stat_lb = Task_Stat_LB()

    def order_endpoint_list(self, tes_json: dict, endpoints: List[str], access_token: str=None, method: LB_Algorithms=LB_Algorithms.TASK_STAT) -> List[str]:
        """

        :param tes_json: TES object in json as dict
        :param endpoints: list of TES endpoints
        :param access_token: access token to be used when using authenticated TES endpoints
        :param method: method to use for LB
        :return: ordered list of endpoints with most best one first
        """
        checked_endpoints = self.endpoint_checker.check_endpoint_list(endpoints, token=access_token)
        final_endpoints = checked_endpoints[0].keys()

        if len(final_endpoints) == 0:
            raise ValueError('Not valid endpoints could be found')


        if method is LB_Algorithms.RANDOM:
            ordered_list = self.random_lb.order_endpoints(final_endpoints)
        elif method is LB_Algorithms.TASK_STAT:
            ordered_list = self.task_stat_lb.order_endpoints(final_endpoints, token=access_token)
        else:
            raise ValueError('Method type specified in method parameter not found')

        return ordered_list