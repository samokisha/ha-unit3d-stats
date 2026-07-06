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

    group_state = hass.states.get(entity_id_by_key["group"])
    assert group_state is not None
    assert group_state.state == MOCK_USER_RESPONSE["group"]


def _entity_id_by_key(hass: HomeAssistant, entry: MockConfigEntry) -> dict[str, str]:
    """Map each sensor key to its entity id via the entity registry."""
    registry = er.async_get(hass)
    return {
        entity.unique_id.removeprefix(f"{entry.entry_id}_"): entity.entity_id
        for entity in er.async_entries_for_config_entry(registry, entry.entry_id)
    }


async def test_infinite_ratio_numeric_is_zero(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that an unbounded ratio maps the numeric sensor to 0, not unknown."""
    aioclient_mock.get(_USER_ENDPOINT, json={**MOCK_USER_RESPONSE, "ratio": "∞"})
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    ratio_state = hass.states.get(_entity_id_by_key(hass, entry)["ratio"])
    assert ratio_state is not None
    assert float(ratio_state.state) == 0


async def test_ratio_display_disabled_by_default(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that the ratio_display sensor exists but is disabled by default."""
    aioclient_mock.get(_USER_ENDPOINT, json=MOCK_USER_RESPONSE)
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = _entity_id_by_key(hass, entry)["ratio_display"]
    entity_entry = registry.async_get(entity_id)
    assert entity_entry is not None
    assert entity_entry.disabled_by is not None
    assert hass.states.get(entity_id) is None


async def test_ratio_display_shows_marker_when_enabled(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that ratio_display mirrors the tracker's infinite marker when enabled."""
    infinite_response = {**MOCK_USER_RESPONSE, "ratio": "∞"}
    aioclient_mock.get(_USER_ENDPOINT, json=infinite_response)
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = _entity_id_by_key(hass, entry)["ratio_display"]
    registry.async_update_entity(entity_id, disabled_by=None)

    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    ratio_display_state = hass.states.get(entity_id)
    assert ratio_display_state is not None
    assert ratio_display_state.state == "∞"


async def test_non_numeric_field_becomes_unknown(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
) -> None:
    """Test that a malformed numeric field degrades to unknown, not a crash."""
    aioclient_mock.get(
        _USER_ENDPOINT,
        json={**MOCK_USER_RESPONSE, "seedbonus": "not-a-number"},
    )
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entity_ids = _entity_id_by_key(hass, entry)
    seedbonus_state = hass.states.get(entity_ids["seedbonus"])
    assert seedbonus_state is not None
    assert seedbonus_state.state == "unknown"
    # Other sensors are unaffected by one malformed field.
    assert hass.states.get(entity_ids["seeding"]).state == "3"
