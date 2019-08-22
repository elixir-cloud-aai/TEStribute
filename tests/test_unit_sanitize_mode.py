"""
Unit tests for IP distance calculation function
`TEStribute.validate_inputs.sanitize_mode()`.
"""
import pytest

from TEStribute.models import Mode
from TEStribute.validate_inputs import sanitize_mode

# Test parameters
MODE_VALID = Mode(1)
MODE_STR_VALID = "cost"
MODE_STR_INVALID = "invalid mode"
MODE_INT_VALID = int(1)
MODE_INT_INVALID = int(-100)
MODE_FLOAT_VALID = float(0.5)
MODE_FLOAT_INVALID = float(-0.5)
MODE_NONE = None


def test_mode_valid():
    assert sanitize_mode(
        mode=MODE_VALID
    ) == pytest.approx(float(MODE_VALID.value))


def test_mode_str_valid():
    assert sanitize_mode(
        mode=MODE_STR_VALID
    ) == pytest.approx(float(Mode[MODE_STR_VALID].value))


def test_mode_str_invalid():
    assert sanitize_mode(mode=MODE_STR_INVALID) is None


def test_mode_int_valid():
    assert sanitize_mode(
        mode=MODE_INT_VALID
    ) == pytest.approx(float(MODE_INT_VALID))


def test_mode_int_invalid():
    assert sanitize_mode(mode=MODE_INT_INVALID) is None


def test_mode_float_valid():
    assert sanitize_mode(
        mode=MODE_FLOAT_VALID
    ) == pytest.approx(MODE_FLOAT_VALID)


def test_mode_float_invalid():
    assert sanitize_mode(mode=MODE_FLOAT_INVALID) is None


def test_mode_none():
    assert sanitize_mode(mode=MODE_NONE) is None
