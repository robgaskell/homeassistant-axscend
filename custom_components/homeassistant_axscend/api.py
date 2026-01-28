"""Axscend API Client."""

from __future__ import annotations

import socket
from typing import Any

import aiohttp
import async_timeout

from .const import API_BASE_URL, API_TIMEOUT, API_USER_AGENT, LOGGER


class AxscendApiClientError(Exception):
    """Exception to indicate a general API error."""


class AxscendApiClientCommunicationError(
    AxscendApiClientError,
):
    """Exception to indicate a communication error."""


class AxscendApiClientAuthenticationError(
    AxscendApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise AxscendApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class AxscendApiClient:
    """Axscend API Client."""

    def __init__(
        self,
        api_token: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Axscend API Client."""
        self._api_token = api_token
        self._session = session

    async def async_get_asset(self, asset_id: str) -> Any:
        """Get asset data with location from the API."""
        return await self._api_wrapper(
            method="get",
            url=f"{API_BASE_URL}/assets/{asset_id}",
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            if headers is None:
                headers = {}
            headers["Authorization"] = f"Bearer {self._api_token}"
            headers["User-Agent"] = f"{API_USER_AGENT}"

            async with async_timeout.timeout(API_TIMEOUT):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise AxscendApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise AxscendApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise AxscendApiClientError(
                msg,
            ) from exception
