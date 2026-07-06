"""Sensor platform for unit3d."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfInformation

from .entity import Unit3dEntity
from .helpers import parse_ratio, parse_size

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import StateType

    from .coordinator import Unit3dDataUpdateCoordinator
    from .data import Unit3dConfigEntry

_BYTES_PER_GIBIBYTE = 1024**3


@dataclass(frozen=True, kw_only=True)
class Unit3dSensorEntityDescription(SensorEntityDescription):
    """Describes a UNIT3D sensor entity."""

    value_fn: Callable[[dict[str, Any]], StateType]


ENTITY_DESCRIPTIONS = (
    Unit3dSensorEntityDescription(
        key="group",
        translation_key="group",
        icon="mdi:account-group",
        value_fn=lambda data: str(data["group"]),
    ),
    Unit3dSensorEntityDescription(
        # No state_class: ratio can be infinite (zero download), which the
        # tracker reports as "∞" — a non-numeric state a measurement sensor
        # would reject. parse_ratio returns a float or that "∞" marker.
        key="ratio",
        translation_key="ratio",
        icon="mdi:swap-vertical",
        value_fn=lambda data: parse_ratio(data["ratio"]),
    ),
    Unit3dSensorEntityDescription(
        key="uploaded",
        translation_key="uploaded",
        icon="mdi:upload",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=2,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: parse_size(data["uploaded"]) / _BYTES_PER_GIBIBYTE,
    ),
    Unit3dSensorEntityDescription(
        key="downloaded",
        translation_key="downloaded",
        icon="mdi:download",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=2,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: parse_size(data["downloaded"]) / _BYTES_PER_GIBIBYTE,
    ),
    Unit3dSensorEntityDescription(
        key="buffer",
        translation_key="buffer",
        icon="mdi:database",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.GIBIBYTES,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: parse_size(data["buffer"]) / _BYTES_PER_GIBIBYTE,
    ),
    Unit3dSensorEntityDescription(
        key="seeding",
        translation_key="seeding",
        icon="mdi:upload-network",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: int(data["seeding"]),
    ),
    Unit3dSensorEntityDescription(
        key="leeching",
        translation_key="leeching",
        icon="mdi:download-network",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: int(data["leeching"]),
    ),
    Unit3dSensorEntityDescription(
        key="seedbonus",
        translation_key="seedbonus",
        icon="mdi:star-circle",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: float(data["seedbonus"]),
    ),
    Unit3dSensorEntityDescription(
        key="hit_and_runs",
        translation_key="hit_and_runs",
        icon="mdi:alert-circle",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: int(data["hit_and_runs"]),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: Unit3dConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        Unit3dSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class Unit3dSensor(Unit3dEntity, SensorEntity):
    """unit3d_stats Sensor class."""

    entity_description: Unit3dSensorEntityDescription

    def __init__(
        self,
        coordinator: Unit3dDataUpdateCoordinator,
        entity_description: Unit3dSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )

    @property
    def native_value(self) -> StateType:
        """Return the native value of the sensor."""
        try:
            return self.entity_description.value_fn(self.coordinator.data)
        except KeyError, ValueError, TypeError:
            return None
