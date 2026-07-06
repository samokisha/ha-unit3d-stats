"""Tests for the unit3d_stats config flow."""

from __future__ import annotations

from typing import TYPE_CHECKING

import aiohttp
from homeassistant import config_entries
from homeassistant.const import CONF_API_TOKEN, CONF_URL
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.unit3d_stats.const import (
    CONF_ALLOW_INSECURE,
    CONF_UPDATE_INTERVAL,
    DOMAIN,
)

from .const import MOCK_CONFIG, MOCK_USER_RESPONSE

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.test_util.aiohttp import (
        AiohttpClientMocker,
    )

_USER_ENDPOINT = "https://tracker.example.com/api/user"


async def test_full_user_flow_creates_entry(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that valid credentials create a config entry."""
    aioclient_mock.get(_USER_ENDPOINT, json=MOCK_USER_RESPONSE)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        MOCK_CONFIG,
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "mockuser (tracker.example.com)"
    assert result["data"] == MOCK_CONFIG
    assert result["result"].unique_id == "tracker-example-com-mockuser"


async def test_user_flow_invalid_auth_shows_error(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that a 401 response shows an auth form error."""
    aioclient_mock.get(_USER_ENDPOINT, status=401)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        MOCK_CONFIG,
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "auth"}


async def test_user_flow_connection_error_shows_error(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that a connection error shows a connection form error."""
    aioclient_mock.get(_USER_ENDPOINT, exc=aiohttp.ClientError)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        MOCK_CONFIG,
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "connection"}


async def test_user_flow_duplicate_entry_aborts(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that a duplicate unique ID aborts as already configured."""
    aioclient_mock.get(_USER_ENDPOINT, json=MOCK_USER_RESPONSE)
    MockConfigEntry(
        domain=DOMAIN,
        unique_id="tracker-example-com-mockuser",
        data=MOCK_CONFIG,
    ).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        MOCK_CONFIG,
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_user_flow_rejects_public_http_without_optin(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that a public plain-http URL is rejected before any request is made."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_URL: "http://tracker.example.com", CONF_API_TOKEN: "test-token"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "insecure_http"}
    assert aioclient_mock.call_count == 0


async def test_local_http_is_allowed(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that a plain-http URL to a private LAN address is allowed without opt-in."""
    aioclient_mock.get("http://192.168.1.50/api/user", json=MOCK_USER_RESPONSE)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_URL: "http://192.168.1.50", CONF_API_TOKEN: "test-token"},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_public_http_with_optin_is_allowed(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that a public plain-http URL is allowed when the user opts in."""
    aioclient_mock.get("http://tracker.example.com/api/user", json=MOCK_USER_RESPONSE)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_URL: "http://tracker.example.com",
            CONF_API_TOKEN: "test-token",
            CONF_ALLOW_INSECURE: True,
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert CONF_ALLOW_INSECURE not in result["data"]
    assert result["data"] == {
        CONF_URL: "http://tracker.example.com",
        CONF_API_TOKEN: "test-token",
    }


async def test_malformed_url_rejected(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that a URL with an unsupported scheme or no host is rejected."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_URL: "ftp://x", CONF_API_TOKEN: "test-token"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_url"}
    assert aioclient_mock.call_count == 0


async def test_tailscale_cgnat_http_is_allowed(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that plain-http to a Tailscale CGNAT address is allowed without opt-in."""
    aioclient_mock.get("http://100.101.102.103/api/user", json=MOCK_USER_RESPONSE)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_URL: "http://100.101.102.103", CONF_API_TOKEN: "test-token"},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_reauth_flow_updates_token(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that reauth with a valid new token updates and reloads the entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="tracker-example-com-mockuser",
        data=MOCK_CONFIG,
    )
    entry.add_to_hass(hass)

    result = await entry.start_reauth_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    aioclient_mock.get(_USER_ENDPOINT, json=MOCK_USER_RESPONSE)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"api_token": "new-token"},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert entry.data["api_token"] == "new-token"


async def test_reauth_flow_rejects_different_account(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that a token for a different account aborts reauth."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="tracker-example-com-mockuser",
        data=MOCK_CONFIG,
    )
    entry.add_to_hass(hass)

    result = await entry.start_reauth_flow(hass)
    aioclient_mock.get(
        _USER_ENDPOINT,
        json={**MOCK_USER_RESPONSE, "username": "someone-else"},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"api_token": "other-account-token"},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "wrong_account"
    assert entry.data[CONF_API_TOKEN] == MOCK_CONFIG[CONF_API_TOKEN]


async def test_options_flow_updates_interval(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that the options flow stores a new update interval."""
    aioclient_mock.get(_USER_ENDPOINT, json=MOCK_USER_RESPONSE)
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CONF_UPDATE_INTERVAL: 30},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_UPDATE_INTERVAL] == 30
