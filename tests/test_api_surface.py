from __future__ import annotations

import inspect

from aio_kavenegar import (
    AIOKavenegarAPI,
    APIException,
    HTTPException,
    KavenegarResponse,
)

from .conftest import ENDPOINTS


def test_every_public_endpoint_is_covered_by_tests() -> None:
    # Guards against a new wrapper being added without a test entry.
    public = {
        name
        for name, value in vars(AIOKavenegarAPI).items()
        if not name.startswith("_") and inspect.isfunction(value)
    }

    assert public == {name for name, _, _ in ENDPOINTS}


def test_all_endpoints_are_coroutine_functions() -> None:
    for name, _, _ in ENDPOINTS:
        assert inspect.iscoroutinefunction(getattr(AIOKavenegarAPI, name)), (
            f"{name} must be async"
        )


def test_package_exports_public_names() -> None:
    import aio_kavenegar

    assert set(aio_kavenegar.__all__) == {
        "KavenegarResponse",
        "APIException",
        "HTTPException",
        "AIOKavenegarAPI",
    }
    for name in aio_kavenegar.__all__:
        assert hasattr(aio_kavenegar, name)


def test_exceptions_derive_from_exception() -> None:
    assert issubclass(APIException, Exception)
    assert issubclass(HTTPException, Exception)
    assert not issubclass(APIException, HTTPException)


def test_api_exception_stores_status_and_message() -> None:
    error = APIException(418, "I'm a teapot")

    assert error.status == 418
    assert error.message == "I'm a teapot"
    assert error.args == ("APIException[418] I'm a teapot",)


def test_kavenegar_response_typed_dict_keys() -> None:
    assert set(KavenegarResponse.__annotations__) == {"return", "entries"}


def test_class_level_defaults() -> None:
    assert AIOKavenegarAPI.version == "v1"
    assert AIOKavenegarAPI.host == "api.kavenegar.com"
    assert AIOKavenegarAPI.default_headers["Accept"] == "application/json"
