"""Custom types for unit3d_stats."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import Unit3dApiClient
    from .coordinator import Unit3dDataUpdateCoordinator


type Unit3dConfigEntry = ConfigEntry[Unit3dData]


@dataclass
class Unit3dData:
    """Data for the UNIT3D integration."""

    client: Unit3dApiClient
    coordinator: Unit3dDataUpdateCoordinator
    integration: Integration
