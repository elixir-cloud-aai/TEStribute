"""Validates and sanitizes input parameters to `rank_services()`"""
import collections.abc
import logging
from typing import (Any, Dict, List, Tuple, Union)

from TEStribute.modes import Mode

logger = logging.getLogger("TEStribute")


def validate_input_parameters(
    defaults: Union[Dict, None] = None,
    drs_ids: Union[List, None] = None,
    drs_uris: Union[List, None] = None,
    mode: Union[float, int, Mode, None, str] = None,
    resource_requirements: Union[Dict, None] = None,
    tes_uris: Union[List, None] = None,
) -> Tuple[Union[List, None], Union[List, None], float, Dict, List]:
    """
    Sets defaults, validates and sanitizes input parameters to
    `rank_services()` function.

    :param defaults: Dictionary of default values for the other parameters.
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
    :param resource_requirements: Dictionary of resources required for the
            task; of the form described in the `tesResources` model of the
            _modified_ GA4GH Task Execution Service schema as described here:
            https://github.com/elixir-europe/mock-TES/blob/master/mock_tes/specs/schema.task_execution_service.d55bf88.openapi.modified.yaml
            Note that the `preemptible` and `zones` properties are currently
            not used.
    :param tes_uris: List of root URIs to known TES instances.

    :return: Tuple of the form:
            (
                drs_ids,
                drs_uris,
                mode,
                resource_requirements,
                tes_uris
            )
    """
    # Set required parameters
    resource_requirements_keys= [
            "cpu_cores",
            "ram_gb",
            "disk_gb",
            "execution_time_min",
    ]

    # Set defaults if values are missing
    if defaults is not None:
        replaced_values = set_defaults(
            defaults=defaults,
            drs_ids=drs_ids,
            drs_uris=drs_uris,
            mode=mode,
            resource_requirements=resource_requirements,
            tes_uris=tes_uris,
        )
        drs_ids = replaced_values["drs_ids"]
        drs_uris = replaced_values["drs_uris"]
        mode = replaced_values["mode"]
        resource_requirements = replaced_values["resource_requirements"]
        tes_uris = replaced_values["tes_uris"]

    # Sanitize run mode
    mode = sanitize_mode(mode=mode)

    ## Ascertain availability of required parameters

    # Initialize error flag
    error = False

    # Check DRS identifiers
    # Empty list is set to `None`
    if drs_ids is not None:
        if isinstance(drs_ids, collections.abc.Iterable):
            for item in drs_ids:
                if not isinstance(item, str):
                    error = True
                    logger.error(
                        (
                            "Parameter 'drs_ids' contains the following item that"
                            "is not a string: {item}"
                        ).format(item=item)
                    )
            # Set empty list to None
            if not drs_ids:
                drs_ids = None
        else:
            error = True
            logger.error("Parameter 'drs_ids' is not an iterable object.")

    # Check DRS instances
    # Empty list is set to `None`, unless there are DRS identifiers
    if drs_uris is not None:
        if isinstance(drs_uris, collections.abc.Iterable):
            for item in drs_uris:
                if not isinstance(item, str):
                    error = True
                    logger.error(
                        (
                            "Parameter 'drs_uris' contains the following item "
                            "that is not a string: {item}"
                        ).format(item=item)
                    )
            if not drs_uris:
                # If DRS objects are required, at least one DRS instance has
                # to be available
                if drs_ids is not None:
                    error = True
                    logger.error(
                        (
                            "Parameter 'drs_uris' is empty, but parameter "
                            "'drs_ids' is not empty."
                        )
                    )
                # Set empty list to None
                else:
                    drs_uris = None
        else:
            error = True
            logger.error("Parameter 'drs_uris' is not an iterable object.")
    else:
        # If DRS objects are required, at least one DRS instance has
        # to be available
        if drs_ids is not None:
            error = True
            logger.error(
                (
                    "Parameter 'drs_uris' is not defined, but paramter "
                    "'drs_ids' is not empty."
                )
            )

    # Check run mode
    if mode is None:
        error = True
        logger.error("Parameter 'mode' is invalid.")
        raise ValueError

    # Check resource requirements
    if isinstance(resource_requirements, dict):
        resource_requirements = dict(resource_requirements)
        for key in resource_requirements_keys:
            if not key in resource_requirements:
                error =True
                logger.error(
                    (
                        "Parameter 'resource_requirements' does not contain "
                        "the following required key: {key}"
                    ).format(key=key)
                )
    else:
        error = True
        logger.error("Parameter 'resource_requirements' is not a dictionary.")
        raise ValueError

    # Check TES instances
    if isinstance(tes_uris, list):
        tes_uris = list(tes_uris)
        for item in tes_uris:
            if not isinstance(item, str):
                error = True
                logger.error(
                    (
                        "Parameter 'tes_uris' contains the following item that"
                        "is not a string: {item}"
                    ).format(item=item)
                )
        if not tes_uris:
            error = True
            logger.error("Parameter 'tes_uris' is empty.")
    else:
        error = True
        logger.error("Parameter 'tes_uris' is not an iterable object.")
        raise ValueError
    
    # Raise ValueError if required parameters are missing/invalid 
    if error:
        raise ValueError
    
    # Return sanitizied/validated parameters
    return (
        drs_ids,
        drs_uris,
        mode,
        resource_requirements,
        tes_uris
    )


def set_defaults(
    defaults: Dict,
    **kwargs: Any,
) -> Dict:
    """
    Returns `**kwargs` with any undefined values being substituted with values
    from a dictionary of default values.

    :param defaults: Dictionary of default values for the keys in `**kwargs`
    :param **kwargs: Arbitrary set of objects to be replaced with default
            values if undefined. Keys are used to look up default values in the
            `defaults` dictionary. Objects whose keys are not available in the
            `defaults` dictionary will be skipped with a warning.
    :return: Dictionary corresponding to `**kwargs`, with updated values
    """
    return_dict = {}
    for name, value in sorted(kwargs.items()):
        if value is not None:
            logger.debug(
                (
                    "Object '{name}' is not undefined. No default value set."
                ).format(name=name)
            )
        elif not name in defaults:
            logger.warning(
                (
                    "No default value available for object '{name}'."
                ).format(name=name)
            )
        else:
            logger.debug(
                (
                    "No value for object '{name}' is defined. Default value set."
                ).format(name=name)
            )
            value = defaults[name]
        return_dict[name] = value
    return return_dict


def sanitize_mode(
    mode: Union[float, int, Mode, None, str] = None
) -> Union[float, None]:
    """
    Validates, sanitizes and returns run mode.

    :param mode: either
            - a `modes.Mode` enumeration member or value
            - one of strings 'cost', 'time' or 'random'
            - one of integers -1, 0, 1
            - a float between 0 and 1

    :return: sanitized mode which is either a value of enum `modes.Mode`, or a
            float between 0 and 1. `None` is returned if an invalid value is
            passed.
    """
    # Check if `Mode` instance
    if isinstance(mode, Mode):
        return float(mode.value)

    # Check if `Mode` key
    if isinstance(mode, str):
        try:
            return float(Mode[mode].value)
        except KeyError:
            logger.warning(
                    (
                        "Run mode undefined. Invalid mode value passed: {mode}"
                    ).format(mode=mode)
                )
            return None

    # Check if `Mode` value
    if isinstance(mode, int):
        try:
            return float(Mode(mode).value)
        except ValueError:
            logger.warning(
                    (
                        "Run mode undefined. Invalid mode value passed: {mode}"
                    ).format(mode=mode)
                )
            return None

    # Check if allowed float
    if isinstance(mode, float):
        if mode < 0 or mode > 1:
            logger.warning(
                    (
                        "Run mode undefined. Invalid mode value passed: {mode}"
                    ).format(mode=mode)
                )
            return None
        else:
            return mode