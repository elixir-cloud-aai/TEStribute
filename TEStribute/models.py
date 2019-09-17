"""
Object models for representing nested, dependent data structures.
"""
import enum
import logging
from typing import (Any, Dict, Iterable, Mapping, Optional, Union)

from TEStribute.errors import (ValidationError)

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
        resource_requirements: ResourceRequirements = None,
        tes_uris: Optional[TesUris] = None,
        drs_ids: Optional[DrsIds] = None,
        drs_uris: Optional[DrsUris] = None,
        mode: Optional[Union[float, int, Mode, str]] = None,
    ) -> None:
        """
        :param resource_requirements: Dictionary of resources required for the
                task; of the form described in the `tesResources` model of the
                _modified_ GA4GH Task Execution Service schema as described here:
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
        self.resource_requirements = resource_requirements
        self.tes_uris = tes_uris
        self.drs_ids = drs_ids
        self.drs_uris = drs_uris
        self.mode = mode
    

    def to_dict(self) -> Dict:
        """Return instance attributes as dictionary."""
        return {
            "resource_requirements": self.resource_requirements,
            "tes_uris": self.tes_uris,
            "drs_ids": self.drs_ids,
            "drs_uris": self.drs_uris,
            "mode": self.mode,
        }


    def validate(
        self,
        defaults: Optional[Mapping],
    ) -> None:
        """
        Sets defaults, validates and sanitizes instance attributes.

        :param defaults: Dictionary of default values.
        """
        # Set defaults if values are missing
        if defaults is not None:
            self.set_defaults(defaults=defaults)

        # Sanitize run mode
        try:
            self.sanitize_mode()
        except ValidationError:
            raise

        # Check for invalid parameters
        for key, value in self.to_dict().items():
            if value is None:
                raise ValidationError(f"Parameter '{key}' is invalid.")

        # If DRS objects have been passed, at least one DRS instance has to be
        # available
        if self.drs_ids and not self.drs_uris: 
            raise ValidationError(
                "No services for accesing input objects defined."
            )

        # At least one TES instance has to be available
        if not self.tes_uris:
            raise ValidationError("No TES instance has been specified.")


    def set_defaults(
        self,
        defaults: Mapping,
    ) -> None:
        """
        Replaces any unset values for `**kwargs` with values from a mapping of
        default values.

        :param defaults: Dictionary of default values for the keys in `**kwargs`
        :param **kwargs: Arbitrary set of objects to be replaced with default
                values if undefined. Keys are used to look up default values in the
                `defaults` dictionary. Objects whose keys are not available in the
                `defaults` dictionary will be skipped with a warning.
        """
        # Iterate over defaults
        for key, value in sorted(defaults.items()):

            # Check whether value is already set
            try:
                attr_val = getattr(self, name=key)
            except AttributeError:
                logger.warn(
                    f"Object has no attribute {key}. Skipped."
                )
                continue

            # Set default value            
            if attr_val is None:
                setattr(self, name=key, value=value)
                logger.debug(
                    f"No value for attribute '{key}' defined. Default value " \
                    f"'{value}' set."
                )


    def sanitize_mode(
        self,
        mode: Union[float, int, Mode, None, str] = None
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
        e = f"Run mode undefined. Invalid mode value passed: {mode}"

        # Check if mode is `Mode` instance
        if isinstance(self.mode, Mode):
            self.mode = float(self.mode.value)

        # Check if mode is `Mode` key
        elif isinstance(self.mode, str):
            try:
                self.mode = float(Mode[mode].value)
            except KeyError:
                raise ValidationError(e)

        # Check if mode is `Mode` value
        elif isinstance(self.mode, int):
            try:
                self.mode = float(Mode(mode).value)
            except ValueError:
                raise ValidationError(e)

        # Check if mode is allowed float
        elif isinstance(self.mode, float):
            if self.mode < 0 or self.mode > 1:
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

