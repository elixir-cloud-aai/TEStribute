"""
Unit tests for IP distance calculation function
`TEStribute.validate_inputs.sanitize_mode()`.
"""
import pytest

from TEStribute.models import Mode
from TEStribute.models.request import Request
from TEStribute.models import ResourceRequirements
from TEStribute.errors import ValidationError

# Test parameters
MODE_VALID = Mode(1)
MODE_STR_VALID = "cost"
MODE_STR_INVALID = "invalid mode"
MODE_INT_VALID = int(1)
MODE_INT_INVALID = int(-100)
MODE_FLOAT_VALID = float(0.5)
MODE_FLOAT_INVALID = float(-0.5)
MODE_NONE = None

# Test mock objects
res_req = ResourceRequirements(
    cpu_cores = 0,
    disk_gb =0,
    execution_time_sec = 0,
    ram_gb = 0,
)
tes_uri = []


def test_mode_valid():
    req = Request(
        res_req, 
        tes_uri,
        mode=MODE_VALID)
    #assert req.sanitize_mode() == pytest.approx(float(MODE_VALID.value))
    assert req.sanitize_mode() == None


def test_mode_str_valid():
    req = Request(
        res_req, 
        tes_uri,
        mode=MODE_STR_VALID)
    assert req.sanitize_mode() ==  None


def test_mode_str_invalid():
    with pytest.raises(ValidationError):
        req = Request(
            res_req, 
            tes_uri,
            mode=MODE_STR_INVALID)
        req.sanitize_mode() 


def test_mode_int_valid():
    req = Request(
        res_req, 
        tes_uri,
        mode=MODE_INT_VALID) 
    assert req.sanitize_mode() == None


def test_mode_int_invalid():
    with pytest.raises(ValidationError):
        req = Request(
            res_req, 
            tes_uri,
            mode=MODE_INT_INVALID) 
        req.sanitize_mode()


def test_mode_float_valid():
    req = Request(
        res_req, 
        tes_uri,
        mode=MODE_FLOAT_VALID) 
    assert req.sanitize_mode() == None


def test_mode_float_invalid():
    with pytest.raises(ValidationError):
        req = Request(
            res_req, 
            tes_uri,
            mode=MODE_FLOAT_INVALID) 
        req.sanitize_mode()


# def test_mode_none():
#     req = Request(
#         res_req, 
#         tes_uri,
#         mode=MODE_NONE) 
#     assert req.sanitize_mode() is None
