import random

from typing import List

class Random_LB():
    def __init__(self):
        random.seed()

    def order_endpoints(self, endpoint_list: List[str]) -> List[str]:
        """
        Orders endpoints randomly
        :param endpoint_list: list of available endpoints
        :return: randomized list of endpoints
        """
        return random.shuffle(endpoint_list)
