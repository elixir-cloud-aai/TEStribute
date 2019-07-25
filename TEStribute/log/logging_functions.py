"""
to accomodate for configuration of logging
"""
import logging


def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] [%(filename)s:%(lineno)s - %(funcName)5s()] %(message)s"
        )
    )
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
