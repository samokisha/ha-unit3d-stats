"""UNIT3D API Client."""

from __future__ import annotations

import asyncio
import functools
import json
import os
import socket
from pathlib import Path
from typing import Any

import aiohttp
import async_timeout

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "user_response.json"


def is_mock_enabled() -> bool:
    """Return whether the mock API mode is enabled via the UNIT3D_MOCK env var."""
    return os.environ.get("UNIT3D_MOCK") == "1"


class Unit3dApiClientError(Exception):
    """Exception to indicate a general API error."""


class Unit3dApiClientCommunicationError(
    Unit3dApiClientError,
):
    """Exception to indicate a communication error."""


class Unit3dApiClientAuthenticationError(
    Unit3dApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise Unit3dApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class Unit3dApiClient:
    """UNIT3D API Client."""

    def __init__(
        self,
        base_url: str,
        api_token: str,
        session: aiohttp.ClientSession,
        *,
        use_mock: bool = False,
    ) -> None:
        """UNIT3D API Client."""
        self._base_url = base_url.rstrip("/")
        self._api_token = api_token
        self._session = session
        self._use_mock = use_mock

    async def async_get_user(self) -> dict[str, Any]:
        """Get the current user's profile data from the API."""
        if self._use_mock:
            return await self._async_get_mock_user()

        return await self._api_wrapper(
            method="get",
            url=f"{self._base_url}/api/user",
            headers={
                "Authorization": f"Bearer {self._api_token}",
                "Accept": "application/json",
            },
        )

    async def _async_get_mock_user(self) -> dict[str, Any]:
        """Read the mock user response from the bundled fixture."""
        loop = asyncio.get_running_loop()
        content = await loop.run_in_executor(
            None,
            functools.partial(_FIXTURE_PATH.read_text, encoding="utf-8"),
        )
        return json.loads(content)

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    # Never follow redirects: the API is a fixed endpoint and a
                    # redirect could forward the bearer token to another host.
                    allow_redirects=False,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise Unit3dApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise Unit3dApiClientCommunicationError(
                msg,
            ) from exception
        except Unit3dApiClientError:
            raise
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise Unit3dApiClientError(
                msg,
            ) from exception
