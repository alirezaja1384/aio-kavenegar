from __future__ import annotations

from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
from types import TracebackType
from typing import Any, Protocol, TypeVar
from unittest.mock import patch

import httpx
import pytest

# Mirrors a Kavenegar success body. `entries` is a list here (as the real API
# returns for send calls), which is why this is not annotated as
# ``KavenegarResponse`` -- that TypedDict declares ``entries: dict``.
ResponsePayload = dict[str, Any]

# typing.Self is 3.11+, so a TypeVar stands in for it at the 3.10 floor.
SelfT = TypeVar("SelfT")

SUCCESS_PAYLOAD: ResponsePayload = {
    "return": {"status": 200, "message": "تایید شد"},
    "entries": [{"messageid": 2000, "status": 1}],
}

# Every public wrapper on the client and the URL segments it must hit.
ENDPOINTS: list[tuple[str, str, str]] = [
    ("sms_send", "sms", "send"),
    ("sms_sendarray", "sms", "sendarray"),
    ("sms_status", "sms", "status"),
    ("sms_statuslocalmessageid", "sms", "statuslocalmessageid"),
    ("sms_select", "sms", "select"),
    ("sms_selectoutbox", "sms", "selectoutbox"),
    ("sms_latestoutbox", "sms", "latestoutbox"),
    ("sms_countoutbox", "sms", "countoutbox"),
    ("sms_cancel", "sms", "cancel"),
    ("sms_receive", "sms", "receive"),
    ("sms_countinbox", "sms", "countinbox"),
    ("sms_countpostalcode", "sms", "countpostalcode"),
    ("sms_sendbypostalcode", "sms", "sendbypostalcode"),
    ("verify_lookup", "verify", "lookup"),
    ("call_maketts", "call", "maketts"),
    ("call_status", "call", "status"),
    ("account_info", "account", "info"),
    ("account_config", "account", "config"),
]


class RecordedPost:
    """A single captured ``AsyncClient.post`` invocation."""

    def __init__(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
        self.args = args
        self.kwargs = kwargs

    @property
    def url(self) -> str:
        return self.args[0] if self.args else self.kwargs["url"]

    @property
    def data(self) -> dict[str, Any] | None:
        return self.kwargs.get("data")

    @property
    def headers(self) -> dict[str, str] | None:
        return self.kwargs.get("headers")

    @property
    def timeout(self) -> int | None:
        return self.kwargs.get("timeout")


class Recorder:
    """Records the constructor options and post calls of the fake client."""

    def __init__(self) -> None:
        self.options: dict[str, Any] = {}
        self.posts: list[RecordedPost] = []

    @property
    def post(self) -> RecordedPost:
        """The most recent request; fails the test if none was made."""
        assert self.posts, "no request was made"
        return self.posts[-1]


@contextmanager
def fake_transport(
    payload: ResponsePayload = SUCCESS_PAYLOAD,
    *,
    raises: BaseException | None = None,
    invalid_json: bool = False,
    status_code: int = 200,
) -> Iterator[Recorder]:
    """
    Patch ``httpx.AsyncClient`` with a stub that records requests.

    :param payload: value returned by ``response.json()``
    :param raises: exception instance raised by ``post`` instead of responding
    :param invalid_json: make ``response.json()`` raise ``ValueError``
    :param status_code: HTTP response status returned by the stub
    """
    recorder = Recorder()

    class Response:
        def raise_for_status(self) -> None:
            response = httpx.Response(
                status_code,
                request=httpx.Request("POST", "https://api.kavenegar.com"),
            )
            response.raise_for_status()

        def json(self) -> ResponsePayload:
            if invalid_json:
                raise ValueError("Expecting value: line 1 column 1 (char 0)")
            return payload

    class AsyncClient:
        def __init__(self, **options: Any) -> None:
            recorder.options.update(options)

        # `typing.Self` is 3.11+ and typing_extensions is not a dependency,
        # so a TypeVar stands in for it here.
        async def __aenter__(self: SelfT) -> SelfT:  # noqa: PYI019
            return self

        async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: TracebackType | None,
        ) -> bool:
            return False

        async def post(self, *args: Any, **kwargs: Any) -> Response:
            recorder.posts.append(RecordedPost(args, kwargs))
            if raises is not None:
                raise raises
            return Response()

    with patch("aio_kavenegar.client.httpx.AsyncClient", AsyncClient):
        yield recorder


class FakeTransport(Protocol):
    """Call signature of the object handed to tests by the ``transport`` fixture."""

    def __call__(
        self,
        payload: ResponsePayload = ...,
        *,
        raises: BaseException | None = ...,
        invalid_json: bool = ...,
        status_code: int = ...,
    ) -> AbstractContextManager[Recorder]: ...


@pytest.fixture
def transport() -> FakeTransport:
    """Expose :func:`fake_transport` to tests as a fixture."""
    return fake_transport
