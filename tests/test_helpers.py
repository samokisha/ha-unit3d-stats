"""Tests for the unit3d_stats helper functions."""

from __future__ import annotations

import pytest

from custom_components.unit3d_stats.helpers import parse_ratio_numeric, parse_size


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
        # Tolerant parsing: missing space, extra spaces, case-insensitive unit.
        ("44.95TiB", 44.95 * 1024**4),
        ("  50   GiB  ", 50 * 1024**3),
        ("1 gib", 1024**3),
        ("2 TIB", 2 * 1024**4),
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
        "-5 GiB",  # negative sizes are rejected
        "1,5 GiB",  # comma decimal separator is not supported
        "∞",  # the infinite marker is not a size
    ],
)
def test_parse_size_invalid(value: str) -> None:
    """Test that malformed or unknown size strings raise ValueError."""
    with pytest.raises(ValueError, match=r".+"):
        parse_size(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("50", 50.0),
        ("407.82", 407.82),
        ("0", 0.0),
    ],
)
def test_parse_ratio_numeric_finite(value: str, expected: float) -> None:
    """Test that a finite ratio string is parsed to a float."""
    assert parse_ratio_numeric(value) == pytest.approx(expected)


@pytest.mark.parametrize("value", ["∞", "inf", "Inf", "Infinity", " ∞ "])
def test_parse_ratio_numeric_infinite_is_zero(value: str) -> None:
    """Test that an unbounded ratio maps to 0.0."""
    assert parse_ratio_numeric(value) == 0.0


def test_parse_ratio_numeric_invalid_raises() -> None:
    """Test that a non-numeric, non-infinite ratio raises ValueError."""
    with pytest.raises(ValueError, match=r".+"):
        parse_ratio_numeric("garbage")
