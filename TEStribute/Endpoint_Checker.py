import tes

from typing import List, Dict

ENDPOINT_SERVICE_PATH = "v1/tasks/service-info"
TIMEOUT = 2

class Endpoint_Checker():
    """

    """
    def check_endpoint_list(self, endpoint_list: List[str], token: str=None) -> (Dict[str, str], Dict[str, str]):
        """
        Checks if endpoints are available or not
        :param endpoint_list: list of potential TES endpoints
        :param token: Authentication token
        :return: tuple of dicts with available endpoints and non-available endpoints
        """
        enpoint_data = {}
        endpoint_blacklist = {}

        for endpoint in endpoint_list:
            try:
                cli = tes.HTTPClient(endpoint, timeout=TIMEOUT, token=token)
                response = cli.get_service_info()
                enpoint_data[endpoint] = response
            except ValueError as e:
                enpoint_data[endpoint] = 200
            except Exception as e:
                endpoint_blacklist[endpoint] = "failed"

        print(endpoint_blacklist)

        return (enpoint_data, endpoint_blacklist)
