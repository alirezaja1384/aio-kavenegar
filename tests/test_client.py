from unittest.mock import patch

import httpx
import pytest

from aio_kavenegar.client import AIOKavenegarAPI


def test_default_url_uses_class_host():
    class CustomHostClient(AIOKavenegarAPI):
        host = "mock.kavenegar.test"

    assert CustomHostClient("api-key").base_url == "https://mock.kavenegar.test"


def test_headers_are_copied_and_merged_per_instance():
    first = AIOKavenegarAPI("api-key", headers={"Accept": "text/plain"})
    second = AIOKavenegarAPI("api-key")

    first.headers["X-Test"] = "first"

    assert first.headers["Accept"] == "text/plain"
    assert second.headers["Accept"] == "application/json"
    assert "X-Test" not in second.headers
    assert "X-Test" not in AIOKavenegarAPI.default_headers


def test_proxy_mapping_creates_async_transport_mounts():
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
async def test_proxy_mounts_are_forwarded_to_httpx():
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
