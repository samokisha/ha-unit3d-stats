"""Tests for the unit3d_stats sensor platform."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
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

_EXPECTED_VALUES = {
    "ratio": 50.0,
    "uploaded": 50.0,
    "downloaded": 1.0,
    "buffer": 124.0,
    "seeding": 3,
    "leeching": 0,
    "seedbonus": 120.5,
    "hit_and_runs": 0,
}


async def test_sensor_states_reflect_user_response(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that every sensor exposes the value derived from the API response."""
    aioclient_mock.get(_USER_ENDPOINT, json=MOCK_USER_RESPONSE)
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id_by_key = {
        entity.unique_id.removeprefix(f"{entry.entry_id}_"): entity.entity_id
        for entity in er.async_entries_for_config_entry(registry, entry.entry_id)
    }

    for key, expected_value in _EXPECTED_VALUES.items():
        entity_id = entity_id_by_key[key]
        state = hass.states.get(entity_id)
        assert state is not None
        assert float(state.state) == pytest.approx(expected_value)
