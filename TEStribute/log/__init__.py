"""
Logging configuration and convenience functions.
"""
import logging
import sys
from typing import Optional

import yaml


def setup_logger(
    name: str,
    level: int = logging.INFO
) -> logging.Logger:
    """Set up logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:

        # Add stream handler for STDERR
        stream = logging.StreamHandler(sys.stderr)
        stream.setFormatter(
            logging.Formatter(
                "[%(asctime)s: %(levelname)s] %(message)s"
            )
        )
        logger.addHandler(stream)

    return logger


def log_yaml(
    header: Optional[str] = None,
    level: int = logging.DEBUG,
    logger: logging.Logger = logging.getLogger(__name__),
    **kwargs,
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
        text = yaml.safe_dump(
            kwargs,
            allow_unicode=True,
            default_flow_style=False
        ).splitlines()
        for line in text:
            logger.log(level, line)