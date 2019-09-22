"""
Basic models for representing nested, dependent data structures.
"""
import enum
from typing import (Dict, Iterable)


class AccessMethodType(enum.Enum):
    """
    Enumerator class for access method types.
    """
    s3 = 's3'
    gs = 'gs'
    ftp = 'ftp'
    gsiftp = 'gsiftp'
    globus = 'globus'
    htsget = 'htsget'
    https = 'https'
    file = 'file'


class ChecksumType(enum.Enum):
    """
    Enumerator class for checksum types.
    """
    md5 = 'md5'
    etag = 'etag'
    sha256 = 'sha256'
    sha512 = 'sha512'


class Currency(enum.Enum):
    """
    Enumerator class for supported currencies.
    """
    ARBITRARY = "ARBITRARY"
    BTC = "BTC"
    EUR = "EUR"
    USD = "USD"


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
    SECONDS = "SECONDS"
    MINUTES = "MINUTES"
    HOURS = "HOURS"


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


    def to_dict(self) -> Dict:
        """Return instance attributes as dictionary."""
        _excluded_keys = set(AccessUris.__dict__.keys())
        return dict(
            (key, value) for (key, value) in self.__dict__.items()
                if key not in _excluded_keys
        )


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


    def to_dict(self) -> Dict:
        """Return instance attributes as dictionary."""
        return {
            "url": self.url,
            "headers": self.headers,
        }


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


    def to_dict(self) -> Dict:
        """Return instance attributes as dictionary."""
        return {
            "type": self.type.value,
            "access_url": self.access_url.to_dict(),
            "access_id": self.access_id,
            "region": self.region,
        }


class Checksum:
    def __init__(
        self,
        checksum: str,
        type: ChecksumType = ChecksumType.md5,
    ) -> None:
        self.checksum = checksum
        self.type = type


    def to_dict(self) -> Dict:
        """Return instance attributes as dictionary."""
        return {
            "checksum": self.checksum,
            "type": self.type.value,
        }


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


    def to_dict(self) -> Dict:
        """Return instance attributes as dictionary."""
        return {
            "amount": self.amount,
            "currency": self.currency.value,
        }


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


    def to_dict(self) -> Dict:
        """Return instance attributes as dictionary."""
        return {
            "id": self.id,
            "size": self.size,
            "created": self.created,
            "checksums": [c.to_dict() for c in self.checksums],
            "access_methods": [m.to_dict() for m in self.access_methods],
            "name": self.name,
            "updated": self.updated,
            "version": self.version,
            "mime_type": self.mime_type,
            "description": self.description,
            "aliases": self.aliases,
        }

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


    def to_dict(self) -> Dict:
        """Return instance attributes as dictionary."""
        return {
            "duration": self.duration,
            "unit": self.unit.value,
        }


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


    def to_dict(self) -> Dict:
        """Return instance attributes as dictionary."""
        return {
            "cpu_cores": self.cpu_cores,
            "disk_gb": self.disk_gb,
            "execution_time_min": self.execution_time_min,
            "ram_gb": self.ram_gb,
            "preemptible": self.preemptible,
            "zones": self.zones,
        }


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


    def to_dict(self) -> Dict:
        """Return instance attributes as dictionary."""
        return {
            "access_uris": self.access_uris.to_dict(),
            "cost_estimate": self.cost_estimate.to_dict(),
            "rank": self.rank,
            "time_estimate": self.time_estimate.to_dict(),
        }


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


    def to_dict(self) -> Dict:
        """Return instance attributes as dictionary."""
        return {
            "costs_total": self.costs_total.to_dict(),
            "costs_cpu_usage": self.costs_cpu_usage.to_dict(),
            "costs_memory_consumption": self.costs_memory_consumption.to_dict(),
            "costs_data_storage": self.costs_data_storage.to_dict(),
            "costs_data_transfer": self.costs_data_transfer.to_dict(),
            "queue_time": self.queue_time.to_dict(),
        }


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
