"""
Convenience functions for logging.
"""
import logging
from logging import (getLogger, Logger)
from typing import Any, Dict, List, Union, Set, Tuple

import yaml

logger = logging.getLogger("TEStribute")


def log_yaml(
    header: Union[None, str] = None,
    level: int = logging.DEBUG,
    logger: Logger = getLogger(__name__),
    **kwargs: Any,
) -> None:
    """
        Logs each of a number of keyword arguments with the indicated logging
        level in YAML format. Dictionaries and iterable objects are logged
        recursively.

        :param header: If not `None`, the header is logged before any of the
                keyword arguments are processed.
        :param level: Logging level.
        :param logger: The logger to be used.
        :param separator: If not `None`, the separator is logged after every
                keyword argument.

        :return: None.
    """
    # Log header
    if header is not None:
        logger.log(level, header)

    # Log value
    if kwargs:
        text = yaml.dump(
            kwargs,
            allow_unicode=True,
            default_flow_style=False
        ).splitlines()
        for line in text:
            logger.log(level, line)
