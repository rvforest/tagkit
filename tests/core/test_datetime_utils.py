"""Tests for the datetime utility helpers."""

from datetime import datetime

import pytest

from tagkit.core.datetime_utils import format_exif_datetime, parse_exif_datetime
from tagkit.core.exceptions import DateTimeError


class TestParseFormatDatetime:
    """Tests for datetime parsing and formatting functions."""

    def test_parse_exif_datetime(self):
        """Test parsing EXIF datetime strings."""
        dt = parse_exif_datetime("2025:05:01 14:30:00")
        assert dt == datetime(2025, 5, 1, 14, 30, 0)

    def test_parse_exif_datetime_invalid(self):
        """Test parsing invalid EXIF datetime strings."""
        with pytest.raises(DateTimeError, match="Invalid EXIF datetime format"):
            parse_exif_datetime("invalid")

        with pytest.raises(DateTimeError, match="Invalid EXIF datetime format"):
            parse_exif_datetime("2025-05-01 14:30:00")  # Wrong separator

    def test_format_exif_datetime(self):
        """Test formatting datetime objects as EXIF strings."""
        dt = datetime(2025, 5, 1, 14, 30, 0)
        formatted = format_exif_datetime(dt)
        assert formatted == "2025:05:01 14:30:00"

    def test_parse_and_format_roundtrip(self):
        """Test that parsing and formatting are inverse operations."""
        original = "2025:05:01 14:30:00"
        dt = parse_exif_datetime(original)
        formatted = format_exif_datetime(dt)
        assert formatted == original

    def test_invalid_type(self):
        """Test that non-string input raises DateTimeError."""
        with pytest.raises(DateTimeError):
            parse_exif_datetime(12345)  # Not a string
