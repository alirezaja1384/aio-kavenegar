from __future__ import annotations

import pytest

from aio_kavenegar.client import AIOKavenegarAPI

from .conftest import ENDPOINTS, FakeTransport

pytestmark = pytest.mark.asyncio

DOCUMENTED_OBJECT_ENTRIES = {
    "account_info": {
        "remaincredit": 1500000,
        "expiredate": 13548889,
        "type": "master",
    },
    "account_config": {"debugmode": "enabled", "defaultsender": "10004346"},
    "call_maketts": {
        "messageid": 8792343,
        "status": 5,
        "receptor": "09121234567",
    },
}


@pytest.mark.parametrize("name, action, method", ENDPOINTS)
async def test_endpoint_targets_expected_url(
    transport: FakeTransport, name: str, action: str, method: str
) -> None:
    client = AIOKavenegarAPI("api-key")

    # Create a client using the provided API key. The `name` parameter is
    # parametrized and maps to one of the client methods (e.g. `account_info`).
    # Use the FakeTransport context manager to capture the outgoing request
    # produced by the invoked method.
    with transport() as recorded:
        await getattr(client, name)()

    assert recorded.post.url == (
        f"https://api.kavenegar.com/v1/api-key/{action}/{method}.json"
    )


@pytest.mark.parametrize("name, action, method", ENDPOINTS)
async def test_endpoint_returns_entries(
    transport: FakeTransport, name: str, action: str, method: str
) -> None:
    client = AIOKavenegarAPI("api-key")
    entries = DOCUMENTED_OBJECT_ENTRIES.get(name, [{"messageid": 2000, "status": 1}])

    # Provide a fake payload which simulates a successful API response
    # (HTTP-level success is simulated by the transport, and the payload
    # contains a `return.status` of 200). The client should parse and
    # return the `entries` object from the payload.
    with transport(payload={"return": {"status": 200}, "entries": entries}):
        assert await getattr(client, name)() == entries


@pytest.mark.parametrize(
    ("name", "params", "expected_data"),
    [
        ("sms_send", {"receptor": "09121234567", "message": "test"}, None),
        ("sms_send", {"receptor": "09121234567,09121234562", "message": "test"}, None),
        (
            "sms_sendarray",
            {
                "sender": ["10004346", "10004347"],
                "receptor": ["09121234567", "09121234568"],
                "message": ["first", "second"],
            },
            {
                "sender": '["10004346", "10004347"]',
                "receptor": '["09121234567", "09121234568"]',
                "message": '["first", "second"]',
            },
        ),
        ("sms_status", {"messageid": "85463238"}, None),
        ("sms_statuslocalmessageid", {"localid": "450"}, None),
        ("sms_select", {"messageid": "30034577"}, None),
        ("sms_selectoutbox", {"startdate": 1409533200}, None),
        ("sms_latestoutbox", {"pagesize": 200}, None),
        ("sms_countoutbox", {"startdate": 1409533200}, None),
        ("sms_cancel", {"messageid": "31031212"}, None),
        ("sms_receive", {"linenumber": "3000202030", "isread": 0}, None),
        ("sms_countinbox", {"startdate": 1409533200}, None),
        (
            "verify_lookup",
            {
                "receptor": "09121234567",
                "token": "852596",
                "template": "login",
            },
            None,
        ),
        ("call_maketts", {"receptor": "09121234567", "message": "test"}, None),
        ("account_config", {"debugmode": "enabled"}, None),
    ],
)
async def test_endpoints_forward_documented_params_as_form_data(
    transport: FakeTransport,
    name: str,
    params: dict,
    expected_data: dict | None,
) -> None:
    client = AIOKavenegarAPI("api-key")

    # Call the client method with `params=` to mirror how consumers will
    # pass data. The FakeTransport records the form data (`post.data`) that
    # the client sends; for some endpoints (e.g. `sms_sendarray`) lists are
    # expected to be JSON-encoded strings, which is represented by
    # `expected_data` being non-None.
    with transport() as recorded:
        await getattr(client, name)(params=params)

    # If `expected_data` is None the params should be forwarded unchanged;
    # otherwise the recorded form-data should match the JSON-encoded mapping.
    assert recorded.post.data == (params if expected_data is None else expected_data)


async def test_account_info_takes_no_params(transport: FakeTransport) -> None:
    client = AIOKavenegarAPI("api-key")

    # `account_info` is an endpoint that does not accept request parameters;
    # ensure the client sends an empty form payload.
    with transport() as recorded:
        await client.account_info()

    assert recorded.post.data == {}
