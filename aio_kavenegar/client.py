import json

from typing import Dict, Literal, Mapping, Optional

import httpx

from aio_kavenegar.exceptions import APIException, HTTPException
from aio_kavenegar.types import KavenegarResponse

# Default requests timeout in seconds.
DEFAULT_TIMEOUT: int = 10
ProxyConfiguration = Optional[Mapping[str, str]]


class AIOKavenegarAPI:
    """
    https://kavenegar.com/rest.html
    """

    version = "v1"
    host = "api.kavenegar.com"
    default_headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "charset": "utf-8",
    }

    def __init__(
        self,
        apikey: str,
        timeout: Optional[int] = None,
        proxies: ProxyConfiguration = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        """
        :param str apikey: Kavenegar API Key
        :param int timeout: request timeout, default is 10
        :param dict headers: headers used when requesting Kavenegar resources, default:
            {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "charset": "utf-8",
            }
        :param proxies: Dictionary mapping protocol to proxy URL:
            {
                'http': 'http://192.168.1.10:3128',
                'https': 'http://192.168.1.10:3129',
            }
        """
        self.apikey: str = apikey
        self.apikey_mask: str = f"{apikey[:2]}********{apikey[-2:]}"
        self.timeout: int = timeout or DEFAULT_TIMEOUT
        self.headers: Dict[str, str] = {
            **type(self).default_headers,
            **(headers or {}),
        }
        self.proxies = proxies

        mounts: Dict[str, httpx.AsyncBaseTransport] = {}
        if proxies:
            if http_proxy := proxies.get("http"):
                mounts["http://"] = httpx.AsyncHTTPTransport(proxy=http_proxy)
            if https_proxy := proxies.get("https"):
                mounts["https://"] = httpx.AsyncHTTPTransport(
                    proxy=https_proxy
                )
        self.mounts: Optional[Dict[str, httpx.AsyncBaseTransport]] = (
            mounts or None
        )

    @property
    def base_url(self) -> str:
        return f"https://{self.host}"

    def __repr__(self) -> str:
        return "kavenegar.AIOKavenegarAPI({!r})".format(self.apikey_mask)

    def __str__(self) -> str:
        return "kavenegar.AIOKavenegarAPI({!s})".format(self.apikey_mask)

    def _parse_params_to_json(self, params: dict) -> dict:
        """
        Ensure that iterable or mapping parameters are encoded as JSON strings.

        Some Kavenegar endpoints expect array- or object-like values to be
        provided as JSON strings when sent as form data. Without this
        conversion, form encoding will turn a list like
        `sender=["30002626","30002627"]` into repeated keys:
        `sender=30002626&sender=30002627`, which the API does not accept.

        This helper converts values that are `dict`, `list`, or `tuple`
        into their JSON representation, leaving other values unchanged.

        Example:
        Input params: {"sender": ["30002626", "30002627"]}
        Output params: {"sender": "[\"30002626\", \"30002627\"]"}
        """
        formatted_params: dict = {}
        for key, value in params.items():
            if isinstance(value, (dict, list, tuple)):
                formatted_params[key] = json.dumps(value)
            else:
                formatted_params[key] = value
        return formatted_params

    async def _request(
        self,
        action: Literal["sms", "verify", "call", "account"],
        method: str,
        params: dict = {},
    ) -> dict:
        params: dict = self._parse_params_to_json(params)
        url = f"{self.base_url}/{self.version}/{self.apikey}/{action}/{method}.json"

        try:
            async with httpx.AsyncClient(mounts=self.mounts) as client:
                http_response = await client.post(
                    url,
                    headers=self.headers,
                    data=params,
                    timeout=self.timeout,
                )

                try:
                    response: KavenegarResponse = http_response.json()

                    if response["return"]["status"] == 200:
                        return response["entries"]
                    else:
                        raise APIException(
                            f'APIException[{response["return"]["status"]}] {response["return"]["message"]}'
                        )
                except ValueError as e:
                    raise HTTPException(e) from e

        except httpx.RequestError as e:
            message = str(e).replace(self.apikey, self.apikey_mask)
            raise HTTPException(message) from None

    async def sms_send(self, params: dict = {}) -> KavenegarResponse:
        return await self._request("sms", "send", params)

    async def sms_sendarray(self, params: dict = {}) -> KavenegarResponse:
        return await self._request("sms", "sendarray", params)

    async def sms_status(self, params: dict = {}) -> KavenegarResponse:
        return await self._request("sms", "status", params)

    async def sms_statuslocalmessageid(
        self, params: dict = {}
    ) -> KavenegarResponse:
        return await self._request("sms", "statuslocalmessageid", params)

    async def sms_select(self, params: dict = {}) -> KavenegarResponse:
        return await self._request("sms", "select", params)

    async def sms_selectoutbox(self, params: dict = {}) -> KavenegarResponse:
        return await self._request("sms", "selectoutbox", params)

    async def sms_latestoutbox(self, params: dict = {}) -> KavenegarResponse:
        return await self._request("sms", "latestoutbox", params)

    async def sms_countoutbox(self, params: dict = {}) -> KavenegarResponse:
        return await self._request("sms", "countoutbox", params)

    async def sms_cancel(self, params: dict = {}) -> KavenegarResponse:
        return await self._request("sms", "cancel", params)

    async def sms_receive(self, params: dict = {}) -> KavenegarResponse:
        return await self._request("sms", "receive", params)

    async def sms_countinbox(self, params: dict = {}) -> KavenegarResponse:
        return await self._request("sms", "countinbox", params)

    async def sms_countpostalcode(
        self, params: dict = {}
    ) -> KavenegarResponse:
        return await self._request("sms", "countpostalcode", params)

    async def sms_sendbypostalcode(
        self, params: dict = {}
    ) -> KavenegarResponse:
        return await self._request("sms", "sendbypostalcode", params)

    async def verify_lookup(self, params: dict = {}) -> KavenegarResponse:
        return await self._request("verify", "lookup", params)

    async def call_maketts(self, params: dict = {}) -> KavenegarResponse:
        return await self._request("call", "maketts", params)

    async def call_status(self, params: dict = {}) -> KavenegarResponse:
        return await self._request("call", "status", params)

    async def account_info(self) -> KavenegarResponse:
        return await self._request("account", "info")

    async def account_config(self, params: dict = {}) -> KavenegarResponse:
        return await self._request("account", "config", params)
