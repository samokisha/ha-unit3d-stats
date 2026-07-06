"""Constants for the unit3d_stats integration tests."""

from __future__ import annotations

from homeassistant.const import CONF_API_TOKEN, CONF_URL

MOCK_CONFIG = {
    CONF_URL: "https://tracker.example.com",
    CONF_API_TOKEN: "test-token",
}

MOCK_USER_RESPONSE = {
    "username": "mockuser",
    "group": "Owner",
    "uploaded": "50 GiB",
    "downloaded": "1 GiB",
    "ratio": "50",
    "buffer": "124 GiB",
    "seeding": 3,
    "leeching": 0,
    "seedbonus": "120.50",
    "hit_and_runs": 0,
}
