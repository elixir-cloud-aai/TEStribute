import unittest

from TEStribute.Endpoint_Checker import Endpoint_Checker


class Test_Endpoint_Checker(unittest.TestCase):
    def test_check_endpoint_list(self):
        endpoint_list = ["https://csc-tesk.c03.k8s-popup.csc.fi", "https://tes.tsi.ebi.ac.uk", "https://tes-dev.tsi.ebi.ac.uk"]
        checker = Endpoint_Checker()
        checker.check_endpoint_list(endpoint_list)
