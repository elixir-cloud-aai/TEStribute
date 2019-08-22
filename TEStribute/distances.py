"""
Functions dealing with the calculation of the distance between IP addresses
"""
import logging
import socket
from typing import Dict, List

from geopy.distance import geodesic
from ip2geotools.databases.noncommercial import DbIpCity
from ip2geotools.errors import InvalidRequestError
from urllib.parse import urlparse

logger = logging.getLogger("TEStribute")


def estimate_distances(
    combinations: Dict,
) -> Dict:
    """
    """
    return {}


def ip_distance(url1: str, url2: str) -> Dict:
    """
    :param ip1: string ip/url
    :param ip2: string ip/url

    :return: a dict containing the locations of both input addresses &
    the physical distance between them in km's
    """
    # Convert domains to IPs
    try:
        ip1 = socket.gethostbyname(urlparse(url1).netloc)
        ip2 = socket.gethostbyname(urlparse(url2).netloc)
    except socket.gaierror:
        raise

    # Locate IPs
    try:
        ip1_loc = DbIpCity.get(ip1, api_key="free")
        ip2_loc = DbIpCity.get(ip2, api_key="free")
    except InvalidRequestError:
        raise

    # Prepare, log and return results
    ret = {
        "source": {
            "city": ip1_loc.city,
            "region": ip1_loc.region,
            "country": ip1_loc.country
        },
        "destination": {
            "city": ip2_loc.city,
            "region": ip2_loc.region,
            "country": ip2_loc.country
        },
        "distance": geodesic(
            (ip1_loc.latitude, ip1_loc.longitude),
            (ip2_loc.latitude, ip2_loc.longitude),
        ).km,
    }
    logger.debug(
        "Distance calculation between {url1} and {url2}: {ret}".format(
            url1=url1,
            url2=url2,
            ret=ret
        )
    )
    return ret
