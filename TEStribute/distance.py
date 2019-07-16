import geopy.distance
from ip2geotools.databases.noncommercial import DbIpCity
import socket


def ReturnDistance(ip1, ip2):

    ip1 = DbIpCity.get(socket.gethostbyname(ip1), api_key="free")
    ip2 = DbIpCity.get(socket.gethostbyname(ip2), api_key="free")

    coords_1 = (ip1.latitude, ip2.longitude)
    coords_2 = (ip1.latitude, ip2.longitude)

    return {
        "source": {
            "city": ip1.city,
            "region": ip1.region,
            "country": ip1.country,
        },
        'destination': {
            'city': ip2.city,
            'region': ip2.region,
            'country': ip2.country,
        },
        'distance': geopy.distance.geodesic(coords_1, coords_2).km,
    }

