"""Constants for unit3d_stats."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "unit3d_stats"
ATTRIBUTION = "Data provided by the UNIT3D private tracker statistics API"

CONF_UPDATE_INTERVAL = "update_interval"
DEFAULT_UPDATE_INTERVAL_MINUTES = 60
