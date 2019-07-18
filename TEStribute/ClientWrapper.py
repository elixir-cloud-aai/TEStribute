from drs_client_module import check_data_objects
from tes_client_module import fetch_tasks_info

from compute_costs import sum_costs

from distance import return_distance


tes_url = "http://193.166.24.111/ga4gh/tes/v1/"
drs_url = "http://193.166.24.114/ga4gh/drs/v1"


if __name__ == "__main__":
    """
    use functions defined
    """

    print(fetch_tasks_info(tes_url, 4, 12, 8, 20))
    check_data_objects(drs_url, ["a001", "a002", "a003"])
