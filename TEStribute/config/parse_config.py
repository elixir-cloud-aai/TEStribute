"""
YAML config parser
"""
import os
import logging
from typing import Dict
import yaml


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
    except (FileNotFoundError, PermissionError) as e:
        logging.error(
            (
                "Config file not found. Ensure that default config file is "
                "available and accessible at '{default_path}'."
                " Execution aborted. "
                "Original error message: {type}: {msg}"
            ).format(default_path=default_path, type=type(e).__name__, msg=e)
        )
    return config
