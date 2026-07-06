"""Helper functions for unit3d_stats."""

from __future__ import annotations

import re

_SIZE_UNITS = {"B": 1, "KIB": 1024, "MIB": 1024**2, "GIB": 1024**3, "TIB": 1024**4}
_SIZE_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([A-Za-z]+)\s*$")

# UNIT3D renders an unbounded ratio (zero download) or an unbounded buffer
# (tracker with no ratio requirement) as this literal string.
_INFINITE_INPUTS = {"∞", "inf", "infinity"}


def parse_size(value: str) -> float:
    """
    Convert a human-readable size string like '44.95 TiB' to bytes.

    Accepts an optional space and case-insensitive IEC units (B, KiB, MiB,
    GiB, TiB). Raises ValueError for any other input, including negative
    values and the infinite marker.
    """
    match = _SIZE_RE.match(value)
    if match is None:
        msg = f"Invalid size format: {value!r}"
        raise ValueError(msg)

    number, unit = match.groups()
    factor = _SIZE_UNITS.get(unit.upper())
    if factor is None:
        msg = f"Unknown size unit {unit!r} in {value!r}"
        raise ValueError(msg)

    return float(number) * factor


def parse_ratio_numeric(value: str) -> float:
    """
    Convert a UNIT3D ratio string to a float.

    Unbounded ratio (zero download) maps to 0.
    """
    if value.strip().lower() in _INFINITE_INPUTS:
        return 0.0
    return float(value)
