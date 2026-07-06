"""Helper functions for unit3d_stats."""

from __future__ import annotations

_SIZE_UNITS = {"B": 1, "KiB": 1024, "MiB": 1024**2, "GiB": 1024**3, "TiB": 1024**4}


def parse_size(value: str) -> float:
    """Convert a human-readable size string like '44.95 TiB' to bytes."""
    parts = value.strip().split()
    if len(parts) != 2:  # noqa: PLR2004
        msg = f"Invalid size format: {value!r}"
        raise ValueError(msg)

    number, unit = parts
    if unit not in _SIZE_UNITS:
        msg = f"Unknown size unit {unit!r} in {value!r}"
        raise ValueError(msg)

    try:
        magnitude = float(number)
    except ValueError as exception:
        msg = f"Invalid numeric value {number!r} in {value!r}"
        raise ValueError(msg) from exception

    return magnitude * _SIZE_UNITS[unit]
