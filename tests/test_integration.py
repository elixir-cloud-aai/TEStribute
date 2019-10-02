"""
Integration tests for `TEStribute`.
"""
import pytest

from TEStribute import rank_services

# Test parameters
OBJECT_IDS = [
    "a001",
    "a002",
    "a003",
    "a004"
]
RESOURCE_REQUIREMENTS = {
    "cpu_cores": "2",
    "ram_gb": "5",
    "disk_gb": "25",
    "execution_time_sec": "300"
}
TES_URIS = None
MODE = "cost"


def test_testribute():
    assert rank_services(
        object_ids=OBJECT_IDS,
        resource_requirements=RESOURCE_REQUIREMENTS,
        tes_uris=TES_URIS,
        mode=MODE
    ) is not None
