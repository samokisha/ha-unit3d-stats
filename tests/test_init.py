"""Tests for the unit3d_stats integration setup and teardown."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.unit3d_stats.const import DOMAIN

from .const import MOCK_CONFIG, MOCK_USER_RESPONSE

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from pytest_homeassistant_custom_component.test_util.aiohttp import (
        AiohttpClientMocker,
    )

_USER_ENDPOINT = "https://tracker.example.com/api/user"


async def test_setup_and_unload_entry(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that a config entry loads and unloads cleanly."""
    aioclient_mock.get(_USER_ENDPOINT, json=MOCK_USER_RESPONSE)
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_entry_auth_failure(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that a 401 response during setup results in a setup error."""
    aioclient_mock.get(_USER_ENDPOINT, status=401)
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)

    assert not await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.SETUP_ERROR


async def test_update_failure_marks_entities_unavailable(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that a non-auth error on refresh degrades entities to unavailable."""
    aioclient_mock.get(_USER_ENDPOINT, json=MOCK_USER_RESPONSE)
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator = entry.runtime_data.coordinator

    aioclient_mock.clear_requests()
    aioclient_mock.get(_USER_ENDPOINT, status=500)
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert coordinator.last_update_success is False

    registry = er.async_get(hass)
    entities = er.async_entries_for_config_entry(registry, entry.entry_id)
    assert entities
    for entity in entities:
        if entity.disabled_by is not None:
            continue
        assert hass.states.get(entity.entity_id).state == "unavailable"
