from __future__ import annotations

import pytest

from aio_kavenegar.client import DEFAULT_TIMEOUT, AIOKavenegarAPI

from .conftest import FakeTransport

pytestmark = pytest.mark.asyncio


async def test_request_url_contains_key_action_method_and_version(
    transport: FakeTransport,
) -> None:
    client = AIOKavenegarAPI("api-key")

    with transport() as recorded:
        await client.sms_send({"receptor": "0912"})

    assert recorded.post.url == "https://api.kavenegar.com/v1/api-key/sms/send.json"


async def test_success_response_returns_entries_only(
    transport: FakeTransport,
) -> None:
    client = AIOKavenegarAPI("api-key")

    with transport() as recorded:
        entries = await client.sms_send()

    assert entries == [{"messageid": 2000, "status": 1}]
    assert recorded.post.data == {}


async def test_params_are_json_encoded_before_being_sent(
    transport: FakeTransport,
) -> None:
    client = AIOKavenegarAPI("api-key")

    with transport() as recorded:
        await client.sms_sendarray({"sender": ["30002626", "30002627"]})

    assert recorded.post.data == {"sender": '["30002626", "30002627"]'}


async def test_instance_headers_and_default_timeout_are_sent(
    transport: FakeTransport,
) -> None:
    client = AIOKavenegarAPI("api-key")

    with transport() as recorded:
        await client.account_info()

    assert recorded.post.headers == client.headers
    assert recorded.post.timeout == DEFAULT_TIMEOUT


async def test_custom_timeout_overrides_the_default(
    transport: FakeTransport,
) -> None:
    client = AIOKavenegarAPI("api-key", timeout=42)

    with transport() as recorded:
        await client.account_info()

    assert recorded.post.timeout == 42


async def test_zero_timeout_falls_back_to_default(
    transport: FakeTransport,
) -> None:
    # `timeout or DEFAULT_TIMEOUT` treats 0 as unset.
    client = AIOKavenegarAPI("api-key", timeout=0)

    with transport() as recorded:
        await client.account_info()

    assert recorded.post.timeout == DEFAULT_TIMEOUT


async def test_no_proxies_means_mounts_is_none(
    transport: FakeTransport,
) -> None:
    client = AIOKavenegarAPI("api-key")

    with transport() as recorded:
        await client.account_info()

    assert client.mounts is None
    assert recorded.options == {"mounts": None}


async def test_default_params_are_not_shared_between_calls(
    transport: FakeTransport,
) -> None:
    # `params: dict = {}` is a mutable default; guard against leakage.
    client = AIOKavenegarAPI("api-key")

    with transport() as recorded:
        await client.sms_send({"receptor": "0912"})
        await client.sms_send()

    assert recorded.posts[0].data == {"receptor": "0912"}
    assert recorded.posts[1].data == {}
