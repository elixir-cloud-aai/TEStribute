"""
Object models for representing nested, dependent data structures.
"""
import enum
import logging
from random import choice
from typing import (Dict, Iterable, Mapping, Optional, Union)

from werkzeug.exceptions import Unauthorized

from TEStribute.errors import (ResourceUnavailableError, ValidationError)
from TEStribute.security.process_jwt import JWT
from TEStribute.utils.service_calls import (
    fetch_drs_objects_metadata,
    fetch_tes_task_info,
)

logger = logging.getLogger("TEStribute")


class AccessMethodType(enum.Enum):
    """
    Enumerator class for access method types.
    """
    s3 = 1
    gs = 2
    ftp = 3
    gsiftp = 4
    globus = 5
    htsget = 6
    https = 7
    file = 8


class ChecksumType(enum.Enum):
    """
    Enumerator class for checksum types.
    """
    md5 = 1
    etag = 2
    sha256 = 3
    sha512 = 4


class Currency(enum.Enum):
    """
    Enumerator class for supported currencies.
    """
    ARBITRARY = "arbitrary"
    BTC = "Bitcoin"
    EUR = "Euro"
    USD = "US Dollar"


class Mode(enum.Enum):
    """
    Enumerator class for different TEStribute run modes.
    """
    random = -1
    cost = 0
    time = 1


class TimeUnit(enum.Enum):
    """
    Enumerator class for units of time.
    """
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"


class AccessUris:
    """
    Access URIs for a TES instance and, if available, a task's input objects.
    """
    def __init__(
        self,
        tes_uri: str,
        **kwargs: str,
    ) -> None:
        self.tes_uri = tes_uri
        for k, v in kwargs.items():
            setattr(self, k, v)


class AccessUrl:
    """
    A URL that can be used to fetch the actual object bytes.
    """
    def __init__(
        self,
        url: str,
        headers: Iterable[str] = [],
    ) -> None:
        self.url = url
        self.headers = headers


class AccessMethod:
    """
    A method describing how an object can be accessed.
    """
    def __init__(
        self,
        type: AccessMethodType,
        access_url: AccessUrl = AccessUrl(url=''),
        access_id: str = '',
        region: str = '',
    ) -> None:
        self.type = type
        self.access_url = access_url
        self.access_id = access_id
        self.region = region


class Checksum:
    def __init__(
        self,
        checksum: str,
        type: ChecksumType = ChecksumType.md5,
    ) -> None:
        self.checksum = checksum,
        self.type = type,


class Costs:
    """
    Describes costs with a given value and currency.
    """
    def __init__(
        self,
        amount: float,
        currency: Currency,
    ) -> None:
        self.amount = amount
        self.currency = currency


class DrsObject:
    """
    Schema describing DRS object metadata and access methods.
    """
    def __init__(
        self,
        id: str,
        size: int,
        created: str,
        checksums: Iterable[Checksum],
        access_methods: Iterable[AccessMethod],
        name: str = '',
        updated: str = '',
        version: str = '',
        mime_type: str = '',
        description: str = '',
        aliases: Iterable[str] = [],
    ) -> None:
        self.id = id
        self.size = size
        self.created = created
        self.checksums = checksums
        self.access_methods = access_methods
        self.name = name
        self.updated = updated
        self.version = version
        self.mime_type = mime_type
        self.description = description
        self.aliases = aliases


class Duration:
    """
    Desctibes a duration with a given value and unit.
    """
    def __init__(
        self,
        duration: int,
        unit: TimeUnit,
    ) -> None:
        self.duration = duration
        self.unit = unit


class Error:
    """
    An individual error message.
    """
    def __init__(
        self,
        message: str,
        reason: str,
    ) -> None:
        self.message = message
        self.reason = reason


class ResourceRequirements:
    """
    Resources requested by a task.
    """
    def __init__(
        self,
        cpu_cores: int,
        disk_gb: float,
        execution_time_min: int,
        ram_gb: float,
        preemptible: bool = True,
        zones: Iterable[str] = [],
    ) -> None:
        self.cpu_cores = cpu_cores
        self.disk_gb = disk_gb
        self.execution_time_min = execution_time_min
        self.ram_gb = ram_gb
        self.preemptible = preemptible
        self.zones = zones


class ErrorResponse:
    """
    A response object for detailed error messages.
    """
    def __init__(
        self,
        code: int,
        errors: Iterable[Error],
        message: str,
    ) -> None:
        self.code = code
        self.errors = errors
        self.message = message


class Request:
    """
    Request schema describing the endpoint's input.
    """
    def __init__(
        self,
        resource_requirements: ResourceRequirements,
        tes_uris: Iterable[str],
        drs_ids: Iterable[str] = [],
        drs_uris: Iterable[str] = [],
        mode: Union[float, int, Mode, str] = 0.5,
        jwt: Optional[str] = None,
        jwt_config: Mapping = {},
    ) -> None:
        """
        :param resource_requirements: Mapping of resources required for the
                task; of the form described in the `tesResources` model of the
                _modified_ GA4GH Task Execution Service schema as described
                here:
                https://github.com/elixir-europe/mock-TES/blob/master/mock_tes/specs/schema.task_execution_service.d55bf88.openapi.modified.yaml
                Note that the `preemptible` and `zones` properties are currently
                not used.
        :param tes_uris: List of root URIs to known TES instances.
        :param drs_ids: List of DRS identifiers of input files required for the
                task. Can be derived from `inputs` property of the `tesTask`
                model of the GA4GH Task Execution Service schema described here:
                https://github.com/ga4gh/task-execution-schemas/blob/develop/openapi/task_execution.swagger.yaml
        :param drs_uris: List of root URIs to known DRS instances.
        :param mode: Either a `mode.Mode` enumeration object, one of its members
                'cost', 'time' or 'random', or one of its values 0, 1, -1,
                respetively. Depending on the mode, services are rank-ordered by
                increasing cost or time, or are randomized for testing/control
                purposes; it is also possible to pass a float between 0 and 1;
                in that case, the value determines the weight between cost (0)
                and time (1) optimization.
        """
        # Validate JWT
        try:
            JWT.config(**jwt_config)
            jwt_obj = JWT(jwt=jwt)
            jwt_obj.validate()
        except Exception as e:
            raise Unauthorized(e.args) from e

        # Initiate instance variables
        self.jwt = jwt_obj.jwt
        self.resource_requirements = resource_requirements
        self.tes_uris = tes_uris
        self.drs_ids = drs_ids
        self.drs_uris = drs_uris
        self.mode = mode
        self.mode_float: float = -1000
    

    def to_dict(self) -> Dict:
        """Return instance attributes as dictionary."""
        return {
            "resource_requirements": self.resource_requirements,
            "tes_uris": self.tes_uris,
            "drs_ids": self.drs_ids,
            "drs_uris": self.drs_uris,
            "mode": self.mode,
            "mode_float": self.mode_float,
        }


    def validate(self) -> None:
        """
        Validates and sanitizes instance attributes.
        """
        # Sanitize run mode
        try:
            self.sanitize_mode()
        except ValidationError:
            raise

        # Check for invalid parameters
        for key, value in self.to_dict().items():
            if value is None:
                raise ValidationError(
                    f"Invalid '{key}' value passed: '{value}'."
                )

        # If DRS objects have been passed, at least one DRS instance has to be
        # available
        if self.drs_ids and not self.drs_uris: 
            raise ValidationError(
                "No services for accesing input objects defined."
            )

        # At least one TES instance has to be available
        if not self.tes_uris:
            raise ValidationError("No TES instance has been specified.")


    def sanitize_mode(
        self,
    ) -> None:
        """
        Validates/sanitizes run mode.

        :param mode: Either
                - a `models.Mode` enumeration member or value
                - one of strings 'cost', 'time' or 'random'
                - one of integers -1, 0, 1
                - a float between 0 and 1

        :raises TEStribute.errors.ValidationError: Invalid mode set.
        """
        # Set error message
        e = f"Invalid 'mode' value passed: '{self.mode}'."

        # Check if mode is `Mode` instance
        if isinstance(self.mode, Mode):
            self.mode_float = float(self.mode.value)

        # Check if mode is `Mode` key
        elif isinstance(self.mode, str):
            try:
                self.mode_float = float(Mode[self.mode].value)
            except KeyError:
                raise ValidationError(e)

        # Check if mode is `Mode` value
        elif isinstance(self.mode, int):
            try:
                self.mode_float = float(Mode(self.mode).value)
            except ValueError:
                raise ValidationError(e)

        # Check if mode is allowed float
        elif isinstance(self.mode, float):
            if 0 <= self.mode <= 1:
                self.mode_float = self.mode
            else:
                raise ValidationError(e)
        
        # Raise ValidationError if mode is of any other type
        else:
            raise ValidationError(e)


class ServiceCombination:
    """
    A combination of TES and input DRS object access URIs together with 
    cost/time estimates and a rank.
    """
    def __init__(
        self,
        access_uris: AccessUris,
        cost_estimate: Costs,
        rank: int,
        time_estimate: Duration,
    ) -> None:
        self.access_uris = access_uris
        self.cost_estimate = cost_estimate
        self.rank = rank
        self.time_estimate = time_estimate


class Response:
    """
    Response schema describing the endpoint's output.
    """
    def __init__(
        self,
        request = Request,
        timeout = float,
    ) -> None:
        # TODO: Constructor needs to generate object conforming to valid
        #       Response schema, but no values need to be computed yet

        # Compile response object
        self.service_combinations: Iterable[ServiceCombination]
        self.warnings: Iterable[str] = []


    # TODO: Implement instance methods to compute all required data for response
    # - compute distances
    # - filter service combinations
    # - compute cost estimates
    # - compute time estimates
    # - calculate ranks
    # - randomize ranks

    @staticmethod
    def get_valid_service_combinations(
        resource_requirements: ResourceRequirements,
        tes_uris: Iterable[str],
        drs_ids: Iterable[str] = [],
        drs_uris: Iterable[str] = [],
        timeout: float = 3.0,
        jtw: Optional[str] = None,
    ) -> Dict:
        """
        Should take the similar input to the rak_services and return any random list of usable TES & DRS services

        :task_info: Dict of the form
        :object_info: Dict of form drs_uri's and drs_id's
        :return: Dict of the form
                {
                    "tes_uri": [ # list of combinations for this TES
                        {
                            "a001": "object_uri",
                            "a002": "object_uri",
                            "output": "object_uri",
                        }, {
                            "a001": "object_uri",
                            "a002": "object_uri",
                            "output": "object_uri",
                        }
                    ],
                    "tes_uri": [ # list of combinations for other TES
                        {
                            "a001": "object_uri",
                            "a002": "object_uri",
                            "output": "object_uri",
                        }, {
                            "a001": "object_uri",
                            "a002": "object_uri",
                            "output": "object_uri",
                        }
                    ]
                }
        """
        # Get TES task info for resource requirements
        try:
            tes_task_info = fetch_tes_task_info(
                tes_uris=tes_uris,
                resource_requirements=resource_requirements,
                timeout=timeout
            )
        except ResourceUnavailableError:
            raise

        # Get metadata for DRS input objects
        try:
            drs_object_info = fetch_drs_objects_metadata(
                drs_uris=drs_uris,
                drs_ids=drs_ids,
                timeout=timeout
            )
        except ResourceUnavailableError:
            raise

        # Compile service combinations
        return_dict = {}
        for tes_uri in tes_task_info:
            drs_dict = {}
            for obj_id in drs_object_info:
                drs_dict[obj_id] = choice(list(drs_object_info[obj_id].keys()))
            return_dict[tes_uri] = drs_dict

        return return_dict


#def estimate_costs(
#    task_info: Dict,
#    object_info: Dict,
#    distances: Dict,
#) -> Dict:
#    """
#    """
#    #############################
#    tes_info_drs = {}
#    for uri, info in task_info.items():
#        # TODO : here the older values of each drs object's cost are overwitten
#        #  fix the updation, though the normal dicts are NOT overwritten
#        tes_info_drs.update({uri: sum_costs(
#            total_tes_costs=task_info[uri]["costs_total"],
#            data_transfer_rate=info["costs_data_transfer"],
#            drs_objects_locations=object_info,
#            tes_url=uri)
#        })
#    return tes_info_drs
#    #############################
#
#
#def transfer_costs(tes_url: str, rate: Dict, drs: Dict, size: float):
#    """
#    :param tes_url: string of the tes uri endpoint
#    :param rate: Dict rate in format {"rate":,"currency:} rate in units per 1000 km
#    :param drs: Dict of access methods
#    :param size: Size of the drs object
#    :return: Ordered dict of costs for the object according to cost
#    """
#    # considering more than one "access_methods" are provided
#    for accessinfo in drs:
#        distance = ip_distance(accessinfo["url"], tes_url)
#        cost = round(size / 1000000000000, 7) * distance["distance"] * rate["amount"]
#        accessinfo["cost"] = cost
#        accessinfo["currency"] = rate["currency"]
#
#    return sorted(drs, key=lambda i: i["cost"])
#
#
#def sum_costs(total_tes_costs: Dict, data_transfer_rate: Dict, drs_objects_locations: Dict, tes_url: str) -> Dict:
#    """
#    :param data_transfer_rate: cost from TES
#    :param drs_objects_locations: Dict contaning the response from the fetch_tasks_info
#    :param tes_url: url of the TES service w.r.t which drs is being computed
#    :return:
#    """
#
#    obj_size = defaultdict(dict)
#    drs_info = defaultdict(dict)
#    for obj_id, drs_uris in drs_objects_locations.items():
#        # TO-DO:
#        # consider the access method headers as well as checksums before cost estimation
#        for drs_uri, access_info in drs_uris.items():
#            # TO-DO:
#            # look into checksums here & headers too for DRS services
#            drs_info[obj_id][drs_uri] = [
#                access_url["access_url"] for access_url in access_info["access_methods"]
#            ]
#            obj_size[obj_id][drs_uri] = access_info["size"]
#
#    return_info = defaultdict(dict)
#    sum_drs = 0
#    currency = None
#    total_cost = None
#    for drs_id, drs_info in drs_info.items():
#        for drs_uri, object_info in drs_info.items():
#            # only the one with the lowest cost is kept
#            return_info[drs_id][drs_uri] = transfer_costs(
#                tes_url, data_transfer_rate, object_info, obj_size[drs_id][drs_uri]
#            )[0]
#
#        # return only cheapest drs
#        return_info[drs_id] = sorted(
#            return_info[drs_id].items(), key=lambda x: x[1]["cost"]
#        )[0]
#
#        sum_drs = return_info[drs_id][1]["cost"] + sum_drs
#        currency = return_info[drs_id][1]["currency"]
#
#        if currency == total_tes_costs["currency"]:
#            total_cost = total_tes_costs["amount"] + sum_drs
#        else:
#            raise ValueError
#
#    if currency is not None and total_cost is not None:
#
#        # to fix overwriting of elemets in the loop it is called from
#        # return_info = dict(return_info)
#        return_info.update({
#            "drs_costs": {"amount": sum_drs, "currency": currency},
#            "total_costs": total_cost,
#            "currency": currency
#        })
#
#        return return_info
#
#    else:
#        raise ValueError
#
#
#def estimate_times(
#    task_info: Dict,
#    object_info: Dict,
#    distances: Dict,
#) -> Dict:
#    """
#    """
#    return {}
#
#
#def randomize(
#    uris: Iterable,
#    object_info: Dict,
#) -> Dict:
#    """
#    """
#    return {}
#
#
#def cost_time(
#    costs: Dict,
#    times: Dict,
#    weight: float,
#) -> Dict:
#    """
#    """
#    return {}


class TaskInfo:
    """
    Schema to represent a task's estimated estimated queue time and total 
    incurred costs.
    """
    def __init__(
        self,
        costs_total: Costs,
        costs_cpu_usage: Costs,
        costs_memory_consumption: Costs,
        costs_data_storage: Costs,
        costs_data_transfer: Costs,
        queue_time: Duration,
    ) -> None:
        self.costs_total = costs_total
        self.costs_cpu_usage = costs_cpu_usage
        self.costs_memory_consumption = costs_memory_consumption
        self.costs_data_storage = costs_data_storage
        self.costs_data_transfer = costs_data_transfer
        self.queue_time = queue_time

