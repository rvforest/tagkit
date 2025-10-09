"""Tests for the datetime utility helpers."""

from datetime import datetime

import pytest

from tagkit.core.datetime_utils import format_exif_datetime, parse_exif_datetime
from tagkit.core.exceptions import DateTimeError


def test_parse_exif_datetime_valid() -> None:
    datetime_str = "2025:06:15 10:30:45"

    result = parse_exif_datetime(datetime_str)

    assert result == datetime(2025, 6, 15, 10, 30, 45)


def test_parse_exif_datetime_invalid() -> None:
    with pytest.raises(DateTimeError):
        parse_exif_datetime("2025-06-15 10:30:45")


def test_format_exif_datetime_round_trip() -> None:
    dt = datetime(2025, 6, 15, 10, 30, 45)

    formatted = format_exif_datetime(dt)

    assert formatted == "2025:06:15 10:30:45"
    assert parse_exif_datetime(formatted) == dt
