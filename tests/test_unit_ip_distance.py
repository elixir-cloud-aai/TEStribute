"""
Unit tests for IP distance calculation function
`TEStribute.distance.ip_distance()`.
"""
from socket import gaierror

import pytest
from ip2geotools.errors import InvalidRequestError

from TEStribute.distance import ip_distance

# Test parameters
IP4_1 = "https://8.8.8.8"
IP4_2 = "https://4.4.4.4/some/subdomain"
IP4_NA = "https://999.999.999.999"
IP4_INVALID = "8.8.8.8"
DOMAIN_1 = "https://www.google.com/"
DOMAIN_2 = "https://www.python.org/some/subdomain"
DOMAIN_NA = "https://doesntexist.to/"
DOMAIN_INVALID = "some_string"


def test_distance_valid_ips():
    ret = ip_distance(url1=IP4_1, url2=IP4_2)
    assert ret["distance"] is not None


def test_distance_same_ips():
    ret = ip_distance(url1=IP4_1, url2=IP4_1)
    assert ret["distance"] == 0


def test_distance_unavailable_ip():
    with pytest.raises(gaierror):
        assert ip_distance(url1=IP4_NA, url2=IP4_1)


def test_distance_invalid_ip():
    with pytest.raises(InvalidRequestError):
        assert ip_distance(url1=IP4_INVALID, url2=IP4_1)


def test_distance_valid_domains():
    ret = ip_distance(url1=DOMAIN_1, url2=DOMAIN_2)
    assert ret["distance"] is not None


def test_distance_same_domains():
    ret = ip_distance(url1=DOMAIN_1, url2=DOMAIN_1)
    assert ret["distance"] == 0


def test_distance_unavailable_domain():
    with pytest.raises(gaierror):
        assert ip_distance(url1=DOMAIN_NA, url2=DOMAIN_1)


def test_distance_invalid_domain():
    with pytest.raises(InvalidRequestError):
        assert ip_distance(url1=DOMAIN_INVALID, url2=DOMAIN_1)
