from __future__ import annotations

from typing import ClassVar
from unittest.mock import patch

import httpx
import pytest

from aio_kavenegar.client import AIOKavenegarAPI

from .conftest import FakeTransport


def test_default_url_uses_class_host() -> None:
    class CustomHostClient(AIOKavenegarAPI):
        host = "mock.kavenegar.test"

    assert CustomHostClient("api-key").base_url == "https://mock.kavenegar.test"


def test_headers_are_copied_and_merged_per_instance() -> None:
    first = AIOKavenegarAPI("api-key", headers={"Accept": "text/plain"})
    second = AIOKavenegarAPI("api-key")

    first.headers["X-Test"] = "first"

    assert first.headers["Accept"] == "text/plain"
    assert second.headers["Accept"] == "application/json"
    assert "X-Test" not in second.headers
    assert "X-Test" not in AIOKavenegarAPI.default_headers


def test_proxy_mapping_creates_async_transport_mounts() -> None:
    client = AIOKavenegarAPI(
        "api-key",
        proxies={
            "http": "http://127.0.0.1:3128",
            "https": "http://127.0.0.1:3129",
        },
    )

    assert set(client.mounts or {}) == {"http://", "https://"}
    assert all(
        isinstance(transport, httpx.AsyncHTTPTransport)
        for transport in (client.mounts or {}).values()
    )


@pytest.mark.asyncio
async def test_proxy_mounts_are_forwarded_to_httpx() -> None:
    captured_options = {}

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"return": {"status": 200}, "entries": []}

    class AsyncClient:
        def __init__(self, **options):
            captured_options.update(options)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

        async def post(self, *args, **kwargs):
            return Response()

    client = AIOKavenegarAPI("api-key", proxies={"https": "http://127.0.0.1:3129"})
    with patch("aio_kavenegar.client.httpx.AsyncClient", AsyncClient):
        await client.account_info()

    assert captured_options == {"mounts": client.mounts}


def test_apikey_is_stored_and_masked() -> None:
    client = AIOKavenegarAPI("ABCDEFGH")

    assert client._apikey == "ABCDEFGH"
    assert client.apikey_mask == "AB********GH"


def test_repr_and_str_expose_only_the_masked_key() -> None:
    secret = "SUPERSECRET"
    client = AIOKavenegarAPI(secret)

    assert secret not in repr(client)
    assert secret not in str(client)
    assert client.apikey_mask in repr(client)
    assert client.apikey_mask in str(client)


def test_http_only_proxy_mounts_http_scheme_alone() -> None:
    client = AIOKavenegarAPI("api-key", proxies={"http": "http://127.0.0.1:1"})

    assert set(client.mounts or {}) == {"http://"}


def test_https_only_proxy_mounts_https_scheme_alone() -> None:
    client = AIOKavenegarAPI("api-key", proxies={"https": "http://127.0.0.1:1"})

    assert set(client.mounts or {}) == {"https://"}


def test_empty_proxy_mapping_yields_no_mounts() -> None:
    assert AIOKavenegarAPI("api-key", proxies={}).mounts is None


def test_unknown_proxy_scheme_is_ignored() -> None:
    client = AIOKavenegarAPI("api-key", proxies={"socks5": "socks5://127.0.0.1:1"})

    assert client.mounts is None


def test_proxies_are_kept_on_the_instance() -> None:
    proxies = {"https": "http://127.0.0.1:3129"}

    assert AIOKavenegarAPI("api-key", proxies=proxies).proxies == proxies


def test_extra_headers_are_added_alongside_defaults() -> None:
    client = AIOKavenegarAPI("api-key", headers={"X-Trace": "abc"})

    assert client.headers["X-Trace"] == "abc"
    assert client.headers["charset"] == "utf-8"
    assert client.headers["Content-Type"] == ("application/x-www-form-urlencoded")


def test_subclass_can_override_default_headers() -> None:
    class JsonClient(AIOKavenegarAPI):
        default_headers: ClassVar[dict] = {"Content-Type": "application/json"}

    client = JsonClient("api-key")

    assert client.headers == {"Content-Type": "application/json"}
    assert "Accept" in AIOKavenegarAPI("api-key").headers


@pytest.mark.asyncio
async def test_subclass_version_and_host_are_used_in_the_request_url(
    transport: FakeTransport,
) -> None:
    class V2Client(AIOKavenegarAPI):
        version = "v2"
        host = "mock.kavenegar.test"

    with transport() as recorded:
        await V2Client("api-key").sms_send()

    assert recorded.post.url == ("https://mock.kavenegar.test/v2/api-key/sms/send.json")
    assert AIOKavenegarAPI.version == "v1"
