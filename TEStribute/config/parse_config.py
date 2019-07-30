"""
YAML config parser
"""
import os
import logging
from typing import Any, Dict
import yaml

logger = logging.getLogger("TESTribute_logger")

def config_parser(
    default_path: str = os.path.abspath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yaml")
    )
) -> Dict:
    """
    :param default_path: path to config file
    :return: dict from yaml config
    """
    try:
        with open(default_path) as f:
            config = yaml.safe_load(f)
            logger.debug("Config loaded from" + default_path)
    except (FileNotFoundError, PermissionError) as error:
        logger.error(
            (
                "Config file not found. Ensure that default config file is "
                "available and accessible at '{default_path}'."
                "Execution aborted. "
                "Original error message: {type}: {msg}"
            ).format(default_path=default_path, type=type(error).__name__, msg=error)
        )
    return config


def set_defaults(
    defaults: Dict,
    **kwargs: Any,
) -> Any:
    """
    Returns `**kwargs` with any undefined values being substitute with values
    from a dictionary of default values.

    :param defaults: Dictionary of default values for the keys in `**kwargs`
    :param **kwargs: Arbitrary set of objects to be replaced with default
            values if undefined. Keys are used to look up default values in the
            `defaults` dictionary. Objects whose keys are not available in the
            `defaults` dictionary will be skipped with a warning.
    :return: list of objects in `**kwargs`, sorted by keys  in alphabetical
            order
    """
    return_values = []
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
        return_values.append(value) 
    return return_values