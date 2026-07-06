"""Tests for the unit3d_stats helper functions."""

from __future__ import annotations

import pytest

from custom_components.unit3d_stats.helpers import parse_size


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("0 B", 0),
        ("1 B", 1),
        ("512 B", 512),
        ("1 KiB", 1024),
        ("1.5 KiB", 1536),
        ("1 MiB", 1024**2),
        ("2.5 MiB", 2.5 * 1024**2),
        ("1 GiB", 1024**3),
        ("50 GiB", 50 * 1024**3),
        ("112.87 GiB", 112.87 * 1024**3),
        ("1 TiB", 1024**4),
        ("44.95 TiB", 44.95 * 1024**4),
    ],
)
def test_parse_size_valid(value: str, expected: float) -> None:
    """Test parsing well-formed size strings for every supported unit."""
    assert parse_size(value) == pytest.approx(expected)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "garbage",
        "123",
        "123 PiB",
        "GiB",
        "1.2.3 GiB",
        "1 GiB extra",
    ],
)
def test_parse_size_invalid(value: str) -> None:
    """Test that malformed or unknown size strings raise ValueError."""
    with pytest.raises(ValueError, match=r".+"):
        parse_size(value)
