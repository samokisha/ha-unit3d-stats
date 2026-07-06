"""DataUpdateCoordinator for unit3d_stats."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    Unit3dApiClientAuthenticationError,
    Unit3dApiClientError,
)

if TYPE_CHECKING:
    from .data import Unit3dConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class Unit3dDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: Unit3dConfigEntry

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_user()
        except Unit3dApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except Unit3dApiClientError as exception:
            raise UpdateFailed(exception) from exception
