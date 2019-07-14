from drs_client_module import fetchDataObject
from tes_client_module import fetchTasksInfo

tes_url = "http://193.166.24.111/ga4gh/tes/v1/"
drs_url = "http://193.166.24.114/ga4gh/drs/v1"


if __name__ == "__main__":
    """
    use functions defined
    """
    DRS_response = fetchDataObject(drs_url, "a001")
    TES_response = fetchTasksInfo(tes_url, 4, 8, 10, True, [], 12)
    print(TES_response)
    print(DRS_response)
