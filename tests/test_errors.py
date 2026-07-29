from __future__ import annotations

import httpx
import pytest

from aio_kavenegar.client import AIOKavenegarAPI
from aio_kavenegar.exceptions import APIException, HTTPException

from .conftest import FakeTransport

pytestmark = pytest.mark.asyncio


async def test_non_200_status_raises_api_exception(
    transport: FakeTransport,
) -> None:
    client = AIOKavenegarAPI("api-key")
    payload = {
        "return": {"status": 411, "message": "Recipient is invalid"},
        "entries": None,
    }

    with transport(payload=payload), pytest.raises(APIException) as excinfo:
        await client.sms_send({"receptor": "bad"})

    assert excinfo.value.status == 411
    assert excinfo.value.message == "Recipient is invalid"
    assert str(excinfo.value) == "APIException[411] Recipient is invalid"


async def test_invalid_json_body_raises_http_exception(
    transport: FakeTransport,
) -> None:
    client = AIOKavenegarAPI("api-key")

    with transport(invalid_json=True), pytest.raises(HTTPException):
        await client.account_info()


async def test_gateway_error_raises_http_exception(
    transport: FakeTransport,
) -> None:
    client = AIOKavenegarAPI("api-key")

    with transport(status_code=502), pytest.raises(HTTPException) as excinfo:
        await client.account_info()

    assert "502" in str(excinfo.value)


async def test_request_error_is_wrapped_in_http_exception(
    transport: FakeTransport,
) -> None:
    client = AIOKavenegarAPI("api-key")
    failure = httpx.ConnectError("connection refused")

    with transport(raises=failure), pytest.raises(HTTPException):
        await client.account_info()


async def test_timeout_is_wrapped_in_http_exception(
    transport: FakeTransport,
) -> None:
    client = AIOKavenegarAPI("api-key")

    with (
        transport(raises=httpx.ReadTimeout("timed out")),
        pytest.raises(HTTPException),
    ):
        await client.account_info()


async def test_api_key_is_masked_in_request_error_messages(
    transport: FakeTransport,
) -> None:
    secret = "SUPERSECRETKEY123"
    client = AIOKavenegarAPI(secret)
    # httpx puts the failing URL (which embeds the key) into the message.
    failure = httpx.ConnectError(
        f"failed to connect to https://api.kavenegar.com/v1/{secret}/account/info.json"
    )

    with transport(raises=failure), pytest.raises(HTTPException) as excinfo:
        await client.account_info()

    message = str(excinfo.value)
    assert secret not in message
    assert client.apikey_mask in message


async def test_api_exception_is_not_swallowed_by_request_error_handler(
    transport: FakeTransport,
) -> None:
    # APIException is raised inside the `try` that catches httpx.RequestError;
    # it must propagate as APIException, not be converted to HTTPException.
    client = AIOKavenegarAPI("api-key")
    payload = {"return": {"status": 400, "message": "bad"}, "entries": None}

    with transport(payload), pytest.raises(APIException):
        await client.sms_send()


async def test_api_exception_chain_does_not_leak_the_key(
    transport: FakeTransport,
) -> None:
    secret = "ANOTHERSECRET99"
    client = AIOKavenegarAPI(secret)

    with (
        transport(raises=httpx.ConnectError(f"boom {secret}")),
        pytest.raises(HTTPException) as excinfo,
    ):
        await client.account_info()

    # `raise ... from None` suppresses the cause, so the original httpx error
    # (which contains the raw key) is not attached to the traceback.
    assert excinfo.value.__cause__ is None
