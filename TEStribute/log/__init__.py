"""
Configure logger.
"""
import logging
import sys
from typing import Union

def setup_logger(
    name: str,
    log_file: str,
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

        # Add file handler
        fl = logging.FileHandler(log_file)
        fl.setFormatter(
            logging.Formatter(
                 "[%(asctime)s: %(levelname)s] [%(filename)s:%(lineno)s - %(funcName)5s()] %(message)s"
            )
        )
        logger.addHandler(fl)

    return logger
