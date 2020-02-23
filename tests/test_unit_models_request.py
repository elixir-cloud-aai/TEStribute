"""Unit tests for `TEStribute.models.request`"""
import pytest

from werkzeug.exceptions import Unauthorized

from TEStribute.models import Mode
from TEStribute.models.request import Request
from TEStribute.models import ResourceRequirements
from TEStribute.errors import ValidationError

# Test parameters
MODE_VALID = Mode(1)
MODE_STR_VALID = str("cost")
MODE_STR_INVALID = str("invalid mode")
MODE_INT_VALID = int(1)
MODE_INT_INVALID = int(-100)
MODE_FLOAT_VALID = float(0.5)
MODE_FLOAT_INVALID = float(-0.5)
MODE_NONE = None

# Test mock objects
res_req = ResourceRequirements(
    cpu_cores=0,
    disk_gb=0,
    execution_time_sec=0,
    ram_gb=0,
)
tes_uris = ["https://some.tes"]
object_ids = ["a001", "a002"]


def test_init():
    req = Request(
        resource_requirements=res_req,
        tes_uris=tes_uris,
    )
    assert isinstance(req, Request)


def test_init_with_auth():
    with pytest.raises(Unauthorized):
        Request(
            resource_requirements=res_req,
            tes_uris=tes_uris,
            authorization_required=True,
        )


def test_to_dict():
    req = Request(
        resource_requirements=res_req,
        tes_uris=tes_uris,
    )
    d = req.to_dict()
    assert isinstance(d, dict)


def test_validate_obj_no_drs():
    with pytest.raises(ValidationError):
        Request(
            resource_requirements=res_req,
            tes_uris=tes_uris,
            object_ids=object_ids,
        )


def test_validate_no_tes():
    with pytest.raises(ValidationError):
        Request(
            resource_requirements=res_req,
            tes_uris=[],
        )


def test_sanitize_mode_valid():
    req = Request(
        resource_requirements=res_req,
        tes_uris=tes_uris,
        mode=MODE_VALID,
    )
    assert req.mode_float == pytest.approx(float(MODE_VALID.value))


def test_sanitize_mode_str_valid():
    req = Request(
        resource_requirements=res_req,
        tes_uris=tes_uris,
        mode=MODE_STR_VALID,
    )
    assert req.mode_float == pytest.approx(float(0))


def test_sanitize_mode_str_invalid():
    with pytest.raises(ValidationError):
        Request(
            resource_requirements=res_req,
            tes_uris=tes_uris,
            mode=MODE_STR_INVALID,
        )


def test_sanitize_mode_int_valid():
    req = Request(
        resource_requirements=res_req,
        tes_uris=tes_uris,
        mode=MODE_INT_VALID,
    )
    assert req.mode_float == pytest.approx(float(1))


def test_sanitize_mode_int_invalid():
    with pytest.raises(ValidationError):
        Request(
            resource_requirements=res_req,
            tes_uris=tes_uris,
            mode=MODE_INT_INVALID,
        )


def test_sanitize_mode_float_valid():
    req = Request(
        resource_requirements=res_req,
        tes_uris=tes_uris,
        mode=MODE_FLOAT_VALID,
    )
    assert req.mode_float == pytest.approx(float(0.5))


def test_sanitize_mode_float_invalid():
    with pytest.raises(ValidationError):
        Request(
            resource_requirements=res_req,
            tes_uris=tes_uris,
            mode=MODE_FLOAT_INVALID,
        )


def test_sanitize_mode_none():
    with pytest.raises(ValidationError):
        Request(
            resource_requirements=res_req,
            tes_uris=tes_uris,
            mode=MODE_NONE,  # type: ignore
        )
