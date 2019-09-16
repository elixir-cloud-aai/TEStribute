"""
Object models for representing nested, dependent data structures.
"""
import enum
from typing import (Iterable, Optional, Mapping, Union)


# TODO: Implement classes that represent the following data structures:
# - "task_info" => better: make use of TES `tesTaskInfo` model with `bravado`
# - "object_info" => better: make use of DRS `Object` model with `bravado`

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


class DrsIds:
    """
    DRS IDs of objects required by the task.
    """
    def __init__(
        self,
        items: Iterable[str] = [],
    ) -> None:
        self.items = items


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


class DrsUris:
    """
    URIs of known DRS instances that objects may be read from or written to.
    """
    def __init__(
        self,
        items: Iterable[str] = [],
    ) -> None:
        self.items = items


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


class TesUris:
    """
    URIs of known TES instances that the task may be computed on.
    """
    def __init__(
        self,
        items: Iterable[str],
    ) -> None:
        self.items = items


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
        tes_uris: TesUris,
        drs_ids: DrsIds = DrsIds(),
        drs_uris: DrsUris = DrsUris(),
        mode: Optional[Union[float, int, Mode, str]] = Mode(0.5),
    ) -> None:
        self.resource_requirements = resource_requirements
        self.tes_uris = tes_uris
        self.drs_ids = drs_ids
        self.drs_uris = drs_uris
        self.mode = mode
    
    def validate(
        self,
        defaults: Mapping,
    ) -> None:
        pass


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
        self.access_uris: access_uris
        self.cost_estimate: cost_estimate
        self.rank: rank
        self.time_estimate: time_estimate


class Response:
    """
    Response schema describing the endpoint's output.
    """
    def __init__(
        self,
        service_combinations = Iterable[ServiceCombination],
        warnings = Iterable[str]

    ) -> None:
        self.service_combinations: service_combinations
        self.warnings: warnings


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

