# aio-kavenegar

An asynchronous Python client for the [Kavenegar REST API](https://kavenegar.com/rest.html). It uses `httpx` and is designed for applications built with `asyncio`.

> This is an independent, community-maintained client. It is not an official Kavenegar package and is not API-compatible with Kavenegar's official Python client.

## Requirements

- Python 3.10 or later
- A Kavenegar account and API key

Create an account through the [Kavenegar panel](https://panel.kavenegar.com/Client/Membership/Register), then obtain an API key from your account settings.

> **Identity verification:** You can use an API key for account-level operations, such as retrieving account information, before verification. Kavenegar requires identity verification before you can send SMS messages, verification messages, or voice calls.

## Installation

```bash
pip install aio-kavenegar
```

## Quick start

Send an SMS from an async function:

```python
import asyncio

from aio_kavenegar import AIOKavenegarAPI, APIException, HTTPException


async def main():
    api = AIOKavenegarAPI("YOUR_API_KEY")

    try:
        result = await api.sms_send(
            {
                "receptor": "09120000000",
                "message": "Hello from aio-kavenegar!",
                # "sender": "1000xxxx",  # optional
            }
        )
        print(result)
    except APIException as exc:
        # Kavenegar returned an application-level error.
        print(f"Kavenegar error {exc.status}: {exc.message}")
    except HTTPException as exc:
        # A transport, HTTP-status, or invalid-response error occurred.
        print(f"Request failed: {exc}")


asyncio.run(main())
```

Every API method is asynchronous and must be awaited. On a successful request, a method returns the API response's `entries` value.

## Verification / OTP

Use a Kavenegar verification template to send a one-time password:

```python
result = await api.verify_lookup(
    {
        "receptor": "09120000000",
        "template": "verify-template",
        "token": "123456",
        "type": "sms",  # or "call"
    }
)
```

Refer to Kavenegar's documentation for template setup and the complete list of supported parameters.

## Bulk SMS

`sms_sendarray` accepts Python lists, tuples, and dictionaries; the client serializes them as JSON form values where required by Kavenegar.

```python
result = await api.sms_sendarray(
    {
        "sender": ["1000xxxx", "1000xxxx"],
        "receptor": ["09120000000", "09120000001"],
        "message": ["First message", "Second message"],
    }
)
```

## Configuration

```python
api = AIOKavenegarAPI(
    "YOUR_API_KEY",
    timeout=20,  # seconds; defaults to 10
    proxies={
        "http": "http://127.0.0.1:3128",
        "https": "http://127.0.0.1:3129",
    },
    headers={"X-Request-ID": "request-123"},
)
```

Custom headers are merged with the client's default form-encoding headers. Proxy URLs may be supplied for either `http`, `https`, or both.

## Available methods

All methods accept an optional `params` dictionary unless otherwise noted. Parameter names and requirements are defined by the [Kavenegar REST API documentation](https://kavenegar.com/rest.html).

| Area | Methods |
| --- | --- |
| SMS | `sms_send`, `sms_sendarray`, `sms_status`, `sms_statuslocalmessageid`, `sms_select`, `sms_selectoutbox`, `sms_latestoutbox`, `sms_countoutbox`, `sms_cancel`, `sms_receive`, `sms_countinbox`, `sms_countpostalcode`, `sms_sendbypostalcode` |
| Verification | `verify_lookup` |
| Voice | `call_maketts`, `call_status` |
| Account | `account_info()` and `account_config` |

For example, retrieve account information without parameters:

```python
account = await api.account_info()
```

## Error handling

The package exposes two exception types:

- `APIException`: Kavenegar returned a non-success application status. Its `status` and `message` attributes contain the API error details.
- `HTTPException`: a network failure, non-success HTTP response, or invalid JSON response prevented the request from completing.

The client masks the API key in HTTP error messages and in its string representation.

## Development

Install the development dependencies, then run the tests and lint checks:

```bash
uv sync --group dev
uv run pytest
uv run ruff check .
uv run ruff format --check --line-length 88 tests
```

## Contributing

Bug reports, documentation improvements, and pull requests are welcome. Please include tests for behavior changes where practical.

## License

This project is released under the [MIT License](LICENSE.md).
