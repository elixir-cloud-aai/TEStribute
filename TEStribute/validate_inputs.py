"""Validates and sanitizes input parameters to `rank_services()`"""
import logging
from typing import Union

from TEStribute.modes import Mode

logger = logging.getLogger("TEStribute")


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
            - None

    :return: sanitized mode which is either a value of enum `modes.Mode`, a
            float between 0 and 1 or `None`. The latter is also returned if an
            invalid value is passed.
    """
    # Check if `None`
    if mode is None:
        logger.warning("Run mode undefined. No mode value passed.")
        return None

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