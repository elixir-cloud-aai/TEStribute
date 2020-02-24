"""
Integration tests for `TEStribute`.
"""
from TEStribute import rank_services

# Test parameters
OBJECT_IDS = [
    "a001",
    "a002",
]
RESOURCE_REQUIREMENTS = {
    "cpu_cores": "2",
    "ram_gb": "5",
    "disk_gb": "25",
    "execution_time_sec": "300"
}
TES_URIS = ["http://193.166.24.111/ga4gh/tes/v1/"]
DRS_URIS = ["http://131.152.229.71/ga4gh/drs/v1/"]
MODE = "cost"


def test_testribute():
    assert rank_services(
        object_ids=OBJECT_IDS,
        resource_requirements=RESOURCE_REQUIREMENTS,
        tes_uris=TES_URIS,
        drs_uris=DRS_URIS,
        mode=MODE
    ) is not None
