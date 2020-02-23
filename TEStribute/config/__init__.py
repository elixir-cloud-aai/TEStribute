"""
YAML config parser
"""
import os
import logging
from typing import Dict
import yaml

logger = logging.getLogger("TEStribute")


def config_parser(
    default_path: str = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "config.yaml"
        )
    )
) -> Dict:
    """
    :param default_path: path to config file
    :return: dict from yaml config
    """
    try:
        with open(default_path) as f:
            config = yaml.safe_load(f)
            if not isinstance(config, dict):
                logger.error(
                    f"Config file '{default_path}' not of key -> value type."
                    "Execution aborted. "
                )
                raise TypeError
            logger.debug("Config loaded from" + default_path)
    except (FileNotFoundError, PermissionError) as e:
        logger.error(
            "Config file not found. Ensure that default config file is "
            f"available and accessible at '{default_path}'."
            "Execution aborted. "
            f"Original error message: {type(e).__name__}: {e}"
        )
        raise
    return config
