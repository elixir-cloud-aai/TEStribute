"""
Functions that interact with external services.
"""
# TODO: Get rid of Bravado-dependency (and thus TES-cli and DRS-cli)
# TODO: DRS and TES clients: implement class-based solution that validates
#       responses against schemata
# TODO: DRS and TES clients: Add authorization header to service calls
from collections import defaultdict
from itertools import combinations
import logging
from typing import (Dict, Iterable, List, Optional)

from bravado.exception import HTTPNotFound
import drs_client
from forex_python.bitcoin import BtcConverter
from forex_python.converter import CurrencyRates
from geopy.distance import geodesic
from ip2geotools.databases.noncommercial import DbIpCity
from ip2geotools.errors import InvalidRequestError
from requests.exceptions import ConnectionError, HTTPError, MissingSchema
from simplejson.errors import JSONDecodeError
import tes_client

from TEStribute.errors import ResourceUnavailableError
from TEStribute.models import (
    AccessMethod,
    AccessMethodType,
    AccessUrl,
    Checksum,
    ChecksumType,
    Costs,
    Currency,
    DrsObject,
    ResourceRequirements,
    TaskInfo,
)

logger = logging.getLogger("TEStribute")


def fetch_drs_objects_metadata(
    drs_uris: Iterable[str],
    object_ids: Iterable[str],
    jwt: Optional[str] = None,
    timeout: float = 3,
    check_results: bool = True,
) -> Dict[str, Dict[str, DrsObject]]:
    """
    Returns access information for an iterable object of DRS identifiers
    available at the specified DRS instances.

    :param drs_uris: List (or other iterable object) of root URIs of DRS
            instances.
    :param object_ids: List (or other iterable object) of globally unique DRS
            identifiers.
    :param check_results: Check whether every object is available at least at
            one DRS instance and whether objects across different DRS instances
            have the same size and checksums.
    :param timeout: Time (in seconds) after which an unsuccessful connection
            attempt to the DRS should be terminated.

    :return: Dict of dicts of DRS object identifers in `object_ids` (keys outer
            dictionary) and DRS root URIs in `drs_uris` (keys inner
            dictionaries) and a dictionary containing the information defined by
            the `Object` model of the DRS specification (values inner
            dictionaries). The inner dictionary for any given DRS object will
            only contain values for DRS instances for which the object is
            available.
    """
    # Initialize results container
    result_dict = defaultdict(dict)

    # Do not continue if no input objects specified
    if not object_ids:
        return result_dict

    # Iterate over DRS instances
    for drs_uri in drs_uris:

        # Fetch object metadata at current DRS instance
        metadata = _fetch_drs_objects_metadata(
            *object_ids,
            uri=drs_uri,
            jwt=jwt,
            timeout=timeout,
        )

        # Add metadata for each object to results container, if available
        if metadata:
            for object_id in metadata:
                result_dict[object_id].update({
                    drs_uri: metadata[object_id]
                })

        # Check whether any object is unavailable
        if check_results:

            # Check availability of objects
            for object_id in object_ids:
                if object_id not in result_dict:
                    raise ResourceUnavailableError(
                        f"Services cannot be ranked. Object '{object_id}' is " \
                        f"not available at any of the specified DRS instances."
                    )

            # Check for consistency of object sizes
            for object_id, locations in result_dict.items():
                obj_sizes: List[float] = []
                for metadata in locations.values():
                    try:
                        obj_sizes.append(metadata.size)
                    except AttributeError:
                        raise ResourceUnavailableError(
                            f"Services cannot be ranked. No size information " \
                            f"for object '{object_id}' available."
                        )
                if len(set(obj_sizes)) > 1:
                    raise ResourceUnavailableError(
                        f"Services cannot be ranked. Object '{object_id}' " \
                        f"has different sizes across different DRS " \
                        f"instances: {set(obj_sizes)}"
                    )
                

            # Check for consistency of object checksums
            for object_id, locations in result_dict.items():
                object_checksums: Dict[ChecksumType, List[str]] = {}
                for metadata in locations.values():
                    try:
                        for checksum in metadata.checksums:
                            if checksum.type in object_checksums:
                                object_checksums[checksum.type].append(
                                    checksum.checksum
                                )
                            else:
                                object_checksums[checksum.type] = [
                                    checksum.checksum
                                ]
                    except AttributeError:
                        raise ResourceUnavailableError(
                            f"Services cannot be ranked. No checksum " \
                            f"available for object '{object_id}'."
                        )
                for checksum_type, checksums in object_checksums.items():
                    if len(set(checksums)) > 1:
                        raise ResourceUnavailableError(
                            f"Services cannot be ranked. Object " \
                            f"'{object_id}' has different " \
                            f"{checksum_type.value} checksums across " \
                            f"different DRS instances: {set(checksums)}"
                        )

        # Return results
    return result_dict


def _fetch_drs_objects_metadata(
    *ids: str,
    uri: str,
    jwt: Optional[str] = None,
    timeout: float = 3,
) -> Dict[str, DrsObject]:
    """
    Returns access information for an iterable object of DRS identifiers
    available at the specified DRS instance.

    :param uri: Root URI of DRS instance.
    :param ids: List (or other iterable object) of globally unique DRS
            identifiers.
    :param timeout: Time (in seconds) after which an unsuccessful connection
            attempt to the DRS should be terminated. Currently not implemented.

    :return: Dict of DRS object identifers in `ids` (keys) and a dictionary
            containing the information defined by the `Object` model of the DRS
            specification (values). Objects that are unavailable at the DRS
            instances will be omitted from the dictionary. In case of a
            connection error at any point, an empty dictionary is returned.
    """
    # Initialize results container
    objects_metadata: Dict[str, DrsObject] = {}

    # Establish connection with DRS; handle exceptions
    try:
        client = drs_client.Client(
            url=uri,
            jwt=jwt,
        )
    except TimeoutError:
        logger.warning(
            f"DRS unavailable: connection attempt to DRS '{uri}' timed out."
        )
        return {}
    except (
        ConnectionError,
        HTTPError,
        HTTPNotFound,
        JSONDecodeError,
        MissingSchema,
    ):
        logger.warning(
            f"DRS unavailable: the provided URI '{uri}' could not be " \
            f"resolved."
        )
        return {}

    # Fetch metadata for every object; handle exceptions
    for object_id in ids:
        try:
            metadata = client.getObject(
                object_id=object_id,
                timeout=timeout,
            )._as_dict()
        except HTTPNotFound:
            logger.debug(
                f"File '{object_id}' is not available on DRS '{uri}'."
            )
            continue
        except TimeoutError:
            logger.warning(
                f"DRS unavailable: connection attempt to DRS '{uri}' timed " \
                f"out."
            )
            continue

        # Generate list of AccessMethods
        access_methods: List[AccessMethod] = []
        for access_method in metadata["access_methods"]:
            access_methods.append(
                AccessMethod(
                    type=AccessMethodType(access_method["type"]),
                    access_url=AccessUrl(
                        url=access_method["access_url"]["url"],
                        headers=access_method["access_url"]["headers"],
                    ),
                    access_id=access_method["access_id"],
                    region=access_method["region"],
                )
            )
        del metadata["access_methods"]
    
        # Generate list of Checksums
        checksums: List[Checksum] = []
        for checksum in metadata["checksums"]:
            checksums.append(
                Checksum(
                    checksum=checksum["checksum"],
                    type=ChecksumType(checksum["type"]),
                )
            )
        del metadata["checksums"]

        # Generate DrsObject
        objects_metadata[object_id] = DrsObject(
            access_methods=access_methods,
            checksums=checksums,
            **metadata,
        )

    # Return object metadata
    return objects_metadata


def fetch_tes_task_info(
    tes_uris: Iterable[str],
    resource_requirements: ResourceRequirements,
    jwt: Optional[str] = None,
    timeout: float = 3,
    check_results: bool = True,
) -> Dict[str, TaskInfo]:
    """
    Given a set of resource requirements, returns queue time, cost estimates and
    related parameters at the specified TES instances.

    :param tes_uris: List (or other iterable object) of root URIs of TES
            instances.
    :param resource_requirements: Dict of compute resource requirements of the
            form defined in the `tesResources` model of the modified TES
            speficications in the `mock-TES` repository at:
            https://github.com/elixir-europe/mock-TES/blob/master/mock_tes/specs/schema.task_execution_service.d55bf88.openapi.modified.yaml
    :param check_results: Check whether the resulting dictionary contains data
            for at least one TES instance.
    :param timeout: Time (in seconds) after which an unsuccessful connection
            attempt to the DRS should be terminated.

    :return: Dict of TES URIs in `tes_uris` (keys) and a dictionary containing
             queue time and cost estimates/rates (values) as defined in the
            `tesTaskInfo` model of the modified TES specifications in the
            `mock-TES` repository: https://github.com/elixir-europe/mock-TES
    """
    # Initialize results container
    result_dict = {}

    # Iterate over TES instances
    for uri in tes_uris:

        # Fetch task info at current TES instance
        task_info = _fetch_tes_task_info(
            uri=uri,
            resource_requirements=resource_requirements,
            jwt=jwt,
            timeout=timeout,
        )

        # If available, add task info to results container
        if task_info:
            result_dict[uri] = task_info
        
    # Check whether at least one TES instance provided task info
    if check_results and not result_dict:
        raise ResourceUnavailableError(
            "Services cannot be ranked. None of the specified TES instances " \
            "provided any task info."
        )
    
    # Return results
    return result_dict


def _fetch_tes_task_info(
    uri: str,
    resource_requirements: ResourceRequirements,
    jwt: Optional[str] = None,
    timeout: float = 3,
) -> Optional[TaskInfo]:
    """
    Given a set of resource requirements, returns queue time, cost estimates and
    related parameters at the specified TES instance.

    :param uri: Root URI of TES instance.
    :param resource_requirements: Dict of compute resource requirements of the
            form defined in the `tesResources` model of the modified TES
            speficications in the `mock-TES` repository at:
            https://github.com/elixir-europe/mock-TES/blob/master/mock_tes/specs/schema.task_execution_service.d55bf88.openapi.modified.yaml
    :param timeout: Time (in seconds) after which an unsuccessful connection
            attempt to the DRS should be terminated. Currently not implemented.

    :return: Dict of queue time and cost estimates/rates as defined in the
            `tesTaskInfo` model of the modified TES specifications in the
            `mock-TES` repository: https://github.com/elixir-europe/mock-TES

    """
    # Establish connection with TES; handle exceptions
    try:
        client = tes_client.Client(
            url=uri,
            jwt=jwt
        )
    except TimeoutError:
        logger.warning(
            f"TES unavailable: connection attempt to '{uri}' timed out."
        )
        return None
    except (ConnectionError, JSONDecodeError, HTTPNotFound, MissingSchema):
        logger.warning(
            f"TES unavailable: the provided URI '{uri}' could not be " \
            f"resolved."
        )
        return None

    # Fetch task info; handle exceptions
    try:
        task_info = client.getTaskInfo(
            timeout=timeout,
            **resource_requirements.to_dict(),
        )._as_dict()
    except TimeoutError:
        logger.warning(
            f"Connection attempt to TES {uri} timed out. TES " \
            f"unavailable. Skipped."
        )
        return None

    # Generate TaskInfo object
    task_info_obj = TaskInfo(
        estimated_compute_costs=Costs(
            amount=task_info["estimated_compute_costs"]["amount"],
            currency=Currency(task_info["estimated_compute_costs"]["currency"]),
        ),
        estimated_storage_costs= Costs(
            amount=task_info["estimated_storage_costs"]["amount"],
            currency=Currency(task_info["estimated_storage_costs"]["currency"]),
        ),
        estimated_queue_time_sec=task_info["estimated_queue_time_sec"],
        unit_costs_data_transfer=Costs(
            amount=task_info["unit_costs_data_transfer"]["amount"],
            currency=Currency(task_info["unit_costs_data_transfer"]["currency"]),
        ),
    )

    # Return task info
    return task_info_obj


def fetch_exchange_rates(
    target_currency: str,
    currencies: Iterable[str],
    amount: float = 1.0,
    bitcoin_proxy: str = 'USD',
) -> Dict[str, Optional[float]]:
    """
    Given an amount and a base currency, returns the exchange rates for a set
    of currencies.
    """
    rates: Dict[str, Optional[float]] = {}
    rates_select: Dict[str, Optional[float]] = {}
    is_bitcoin: bool = False

    # Special case if base currency is BitCoin
    if target_currency == 'BTC':
        is_bitcoin = True
        target_currency = bitcoin_proxy

    # Instantiate converter
    converter = CurrencyRates()
    converter_btc = BtcConverter()
    
    # Get rates for base currency

    try:
        rates = converter.get_rates(target_currency)
    except ConnectionError:
        logger.warning(
            f"Could not connect to currency rates service. No exchange rates " \
            f"available."
        )
        return rates_select

    # Get Bitcoin rate for base currency
    try:
        rates['BTC'] = converter_btc.convert_to_btc(
            amount=amount,
            currency=bitcoin_proxy
        )
    except ConnectionError:
        logger.warning(
            f"Could not connect to currency rates service. No BitCoin " \
            f"exchange rate available."
        )
        return rates_select

    # Select rates
    for currency in currencies:
        if currency in rates:
            rates_select[currency] = rates[currency]
        else:
            rates_select[currency] = None

    # Convert to base BitCoin if BitCoin was base currency
    if is_bitcoin:
        rate_btc = rates_select['BTC']
        for currency in rates_select.keys():
            if rates_select[currency]:
                rates_select[currency] = rates_select[currency] / rate_btc

    return rates_select


def ip_distance(
    *args: str,
) -> Dict[str, Dict]:
    """
    :param *args: IP addresses of the form '8.8.8.8' without schema and
            suffixes.

    :return: A dictionary with a key for each IP address, pointing to a
            dictionary containing city, region and country information for the
            IP address, as well as a key "distances" pointing to a dictionary
            indicating the distances, in kilometers, between all pairs of IPs,
            with the tuple of IPs as the keys. IPs that cannot be located are
            skipped from the resulting dictionary.
    
    :raises ValueError: No args were passed.
    """
    if not args:
        raise ValueError("Expected at least one URI or IP address.")

    # Locate IPs
    ip_locs = {}
    for ip in args:
        try:
            ip_locs[ip] = DbIpCity.get(ip, api_key="free")
        except InvalidRequestError:
            pass

    # Compute distances
    dist = {}
    for keys in combinations(ip_locs.keys(), r=2):
        dist[(keys[0], keys[1])] = geodesic(
            (ip_locs[keys[0]].latitude, ip_locs[keys[0]].longitude),
            (ip_locs[keys[1]].latitude, ip_locs[keys[1]].longitude),
        ).km
        dist[(keys[1], keys[0])] = dist[(keys[0], keys[1])]
    
    # Prepare results
    res = {}
    for key, value in ip_locs.items():
        res[key] = {
            "city": value.city,
            "region": value.region,
            "country": value.country,
        }
    res["distances"] = dist

    # Return results
    return res