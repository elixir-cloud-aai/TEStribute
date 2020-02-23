"""
Unit tests for IP distance calculation function
`TEStribute.distance.ip_distance()`.
"""
from socket import gaierror

import pytest
from ip2geotools.errors import InvalidRequestError

from TEStribute.utils.service_calls import ip_distance

# Test parameters
IP_1 = "8.8.8.8"
IP_2 = "45.55.99.72"
IP_NA = "999.999.999.999"
IP_INVALID = "http://8.8.8.8"
DOMAIN = "https://www.google.com/"


def test_ip_distance_valid_ips():
    ret = ip_distance(IP_1, IP_2)
    assert ret["distances"][(IP_1, IP_2)] > 0


def test_ip_distance_one_arg():
    ret = ip_distance(IP_1)
    assert ret["distances"] == {}


def test_ip_distance_no_args():
    with pytest.raises(ValueError):
        ip_distance()


def test_ip_distance_ip_na():
    ret = ip_distance(IP_NA)
    assert ret == {'distances': {}}


def test_ip_distance_ip_invalid():
    ret = ip_distance(IP_INVALID)
    assert ret == {'distances': {}}


def test_ip_distance_domain():
    ret = ip_distance(DOMAIN)
    assert ret == {'distances': {}}


def test_ip_distance_same_ip():
    ret = ip_distance(IP_1, IP_1)
    assert ret['distances'] == {}


def test_ip_distance_mixed():
    ret = ip_distance(IP_1, IP_2, DOMAIN)
    print(ret)
    assert ret['distances'] == {}
