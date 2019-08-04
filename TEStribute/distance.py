"""
Functions dealing with the calculation of the distance between IP addresses
"""
import logging
import socket
import time
from typing import Dict

from geopy.distance import geodesic
from ip2geotools.databases.noncommercial import DbIpCity
from urllib.parse import urlparse

logger = logging.getLogger("TEStribute")

def return_distance(ip1: str, ip2: str) -> Dict:
    """
    :param ip1: string ip/url
    :param ip2: string ip/url

    :return: a dict containing the locations of both input addresses &
    the physical distance between them in km's
    """
    start = time.time()

    # TODO: except error for localhost
    ip1 = DbIpCity.get(socket.gethostbyname(urlparse(ip1).netloc), api_key="free")
    ip2 = DbIpCity.get(socket.gethostbyname(urlparse(ip2).netloc), api_key="free")

    coords_1 = (ip1.latitude, ip1.longitude)
    coords_2 = (ip2.latitude, ip2.longitude)

    response = {
        "source": {"city": ip1.city, "region": ip1.region, "country": ip1.country},
        "destination": {"city": ip2.city, "region": ip2.region, "country": ip2.country},
        "distance": geodesic(coords_1, coords_2).km,
    }

    end = time.time()

    # TODO:
    #  fix logger output
    #logger.debug(
    #    str(response) + "time taken for calculation :" + str(end - start) + " seconds"
    # )

    return response
