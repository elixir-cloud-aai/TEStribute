
"""
Object models for representing nested, dependent data structures.
"""
import logging
from typing import (Dict, Iterable, Mapping, Optional, Union)

from werkzeug.exceptions import Unauthorized

from TEStribute.errors import ValidationError
from TEStribute.models import (Mode, ResourceRequirements)
from TEStribute.security.process_jwt import JWT

logger = logging.getLogger("TEStribute")


class Request:
    """
    Request schema describing the endpoint's input.
    """
    def __init__(
        self,
        resource_requirements: ResourceRequirements,
        tes_uris: Iterable[str],
        object_ids: Iterable[str] = [],
        drs_uris: Iterable[str] = [],
        mode: Union[float, int, Mode, str] = 0.5,
        authorization_required: bool = False,
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
        :param object_ids: List of DRS identifiers of input files required for the
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
        if authorization_required:
            try:
                JWT.config(**jwt_config)
                jwt_obj = JWT(jwt=jwt)
                jwt_obj.validate()
            except Exception as e:
                raise Unauthorized(e.args) from e
            jwt = jwt_obj.jwt

        # Initiate instance variables
        self.jwt = jwt
        self.resource_requirements = resource_requirements
        self.tes_uris = tes_uris
        self.object_ids = object_ids
        self.drs_uris = drs_uris
        self.mode = mode
        self.mode_float: float = -1000
    

    def to_dict(self) -> Dict:
        """Return instance attributes as dictionary."""
        return {
            "resource_requirements": self.resource_requirements.to_dict(),
            "tes_uris": self.tes_uris,
            "object_ids": self.object_ids,
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
        if self.object_ids and not self.drs_uris: 
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
