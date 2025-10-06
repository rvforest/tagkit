"""Tests for datetime operations with EXIF tags."""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tagkit.core.exceptions import DateTimeError
from tagkit import ExifImage, parse_exif_datetime, format_exif_datetime


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


class TestGetDatetime:
    """Tests for ExifImage.get_datetime() method."""

    def test_get_datetime_from_datetime_original(self, test_images):
        """Test getting datetime when DateTimeOriginal is present."""
        image_path = test_images / "datetime_software.jpg"
        exif = ExifImage(image_path)
        dt = exif.get_datetime()
        assert dt == datetime(2025, 5, 1, 14, 30, 0)

    def test_get_datetime_specific_tag(self, test_images):
        """Test getting a specific datetime tag."""
        image_path = test_images / "datetime_software.jpg"
        exif = ExifImage(image_path)
        dt = exif.get_datetime(tag="DateTimeOriginal")
        assert dt == datetime(2025, 5, 1, 14, 30, 0)

    def test_get_datetime_nonexistent_tag(self, test_images):
        """Test getting a nonexistent datetime tag returns None."""
        image_path = test_images / "datetime_software.jpg"
        exif = ExifImage(image_path)
        dt = exif.get_datetime(tag="DateTime")
        assert dt is None

    def test_get_datetime_no_datetime_tags(self, test_images):
        """Test getting datetime from image with no datetime tags."""
        image_path = test_images / "minimal.jpg"
        exif = ExifImage(image_path)
        dt = exif.get_datetime()
        assert dt is None


class TestSetDatetime:
    """Tests for ExifImage.set_datetime() method."""

    def test_set_datetime_update_all(self, test_images):
        """Test setting datetime with tags=None (updates all)."""
        image_path = test_images / "datetime_software.jpg"
        new_dt = datetime(2025, 6, 15, 10, 30, 0)

        exif = ExifImage(image_path)
        exif.set_datetime(new_dt, tags=None)
        exif.save()

        # Verify all datetime tags are updated
        exif_verify = ExifImage(image_path)
        datetimes = exif_verify.get_all_datetimes()
        assert datetimes["DateTime"] == new_dt
        assert datetimes["DateTimeOriginal"] == new_dt
        assert datetimes["DateTimeDigitized"] == new_dt

    def test_set_datetime_update_primary_only(self, test_images):
        """Test setting datetime with specific tags list."""
        image_path = test_images / "minimal.jpg"
        new_dt = datetime(2025, 6, 15, 10, 30, 0)

        exif = ExifImage(image_path)
        exif.set_datetime(new_dt, tags=["DateTimeOriginal"])
        exif.save()

        # Verify only DateTimeOriginal is set
        exif_verify = ExifImage(image_path)
        dt = exif_verify.get_datetime(tag="DateTimeOriginal")
        assert dt == new_dt

        # DateTime should not be set
        dt_other = exif_verify.get_datetime(tag="DateTime")
        assert dt_other is None


class TestGetAllDatetimes:
    """Tests for ExifImage.get_all_datetimes() method."""

    def test_get_all_datetimes_single_tag(self, test_images):
        """Test getting all datetimes when only one is present."""
        image_path = test_images / "datetime_software.jpg"
        exif = ExifImage(image_path)
        datetimes = exif.get_all_datetimes()
        assert len(datetimes) == 1
        assert "DateTimeOriginal" in datetimes
        assert datetimes["DateTimeOriginal"] == datetime(2025, 5, 1, 14, 30, 0)

    def test_get_all_datetimes_multiple_tags(self, test_images):
        """Test getting all datetimes when multiple are present."""
        image_path = test_images / "datetime_software.jpg"
        # First set all datetime tags
        new_dt = datetime(2025, 6, 15, 10, 30, 0)

        exif = ExifImage(image_path)
        exif.set_datetime(new_dt)
        exif.save()

        exif_verify = ExifImage(image_path)
        datetimes = exif_verify.get_all_datetimes()
        assert len(datetimes) == 3
        assert datetimes["DateTime"] == new_dt
        assert datetimes["DateTimeOriginal"] == new_dt
        assert datetimes["DateTimeDigitized"] == new_dt

    def test_get_all_datetimes_no_tags(self, test_images):
        """Test getting all datetimes when none are present."""
        image_path = test_images / "minimal.jpg"
        exif = ExifImage(image_path)
        datetimes = exif.get_all_datetimes()
        assert len(datetimes) == 0


class TestOffsetDatetime:
    """Tests for ExifImage.offset_datetime() method."""

    def test_offset_datetime_positive(self, test_images):
        """Test offsetting datetime by a positive timedelta."""
        image_path = test_images / "datetime_software.jpg"

        exif = ExifImage(image_path)
        original_dt = exif.get_datetime()
        assert original_dt is not None

        delta = timedelta(hours=2, minutes=30)
        exif.offset_datetime(delta)
        exif.save()

        exif_verify = ExifImage(image_path)
        new_dt = exif_verify.get_datetime()
        assert new_dt == original_dt + delta

    def test_offset_datetime_negative(self, test_images):
        """Test offsetting datetime by a negative timedelta."""
        image_path = test_images / "datetime_software.jpg"

        exif = ExifImage(image_path)
        original_dt = exif.get_datetime()
        assert original_dt is not None

        delta = timedelta(days=-1, hours=-3)
        exif.offset_datetime(delta)
        exif.save()

        exif_verify = ExifImage(image_path)
        new_dt = exif_verify.get_datetime()
        assert new_dt == original_dt + delta

    def test_offset_datetime_all_tags(self, test_images):
        """Test offsetting all datetime tags."""
        image_path = test_images / "minimal.jpg"
        base_dt = datetime(2025, 6, 15, 10, 0, 0)

        exif = ExifImage(image_path)
        exif.set_datetime(base_dt)
        exif.save()

        exif = ExifImage(image_path)
        delta = timedelta(hours=5)
        exif.offset_datetime(delta)
        exif.save()

        # Verify all datetime tags are offset
        exif_verify = ExifImage(image_path)
        datetimes = exif_verify.get_all_datetimes()
        expected_dt = base_dt + delta
        assert datetimes["DateTime"] == expected_dt
        assert datetimes["DateTimeOriginal"] == expected_dt
        assert datetimes["DateTimeDigitized"] == expected_dt

    def test_offset_datetime_specific_tags(self, test_images):
        """Test offsetting only specific datetime tags."""
        image_path = test_images / "minimal.jpg"
        base_dt = datetime(2025, 6, 15, 10, 0, 0)

        # Set all tags first
        exif = ExifImage(image_path)
        exif.set_datetime(base_dt)
        exif.save()

        # Offset only DateTimeOriginal
        exif = ExifImage(image_path)
        delta = timedelta(hours=3)
        exif.offset_datetime(delta, tags=["DateTimeOriginal"])
        exif.save()

        # Verify only DateTimeOriginal was offset
        exif_verify = ExifImage(image_path)
        datetimes = exif_verify.get_all_datetimes()
        assert datetimes["DateTimeOriginal"] == base_dt + delta
        assert datetimes["DateTime"] == base_dt
        assert datetimes["DateTimeDigitized"] == base_dt


class TestDatetimePrecedence:
    """Tests for datetime tag precedence logic in ExifImage.get_datetime()."""

    def test_precedence_datetime_original_first(self, test_images):
        """Test that DateTimeOriginal is preferred over other tags."""
        image_path = test_images / "minimal.jpg"

        # Set all three datetime tags with different values
        exif = ExifImage(image_path)
        exif.set_datetime(datetime(2025, 6, 20, 10, 0, 0), tags=["DateTime"])
        exif.set_datetime(datetime(2025, 6, 10, 10, 0, 0), tags=["DateTimeOriginal"])
        exif.set_datetime(datetime(2025, 6, 15, 10, 0, 0), tags=["DateTimeDigitized"])
        exif.save()

        # get_datetime should return DateTimeOriginal
        exif_verify = ExifImage(image_path)
        dt = exif_verify.get_datetime()
        assert dt == datetime(2025, 6, 10, 10, 0, 0)

    def test_precedence_datetime_digitized_second(self, test_images):
        """Test that DateTimeDigitized is preferred when DateTimeOriginal is missing."""
        image_path = test_images / "minimal.jpg"

        # Set DateTime and DateTimeDigitized but not DateTimeOriginal
        exif = ExifImage(image_path)
        exif.set_datetime(datetime(2025, 6, 20, 10, 0, 0), tags=["DateTime"])
        exif.set_datetime(datetime(2025, 6, 15, 10, 0, 0), tags=["DateTimeDigitized"])
        exif.save()

        # get_datetime should return DateTimeDigitized
        exif_verify = ExifImage(image_path)
        dt = exif_verify.get_datetime()
        assert dt == datetime(2025, 6, 15, 10, 0, 0)

    def test_precedence_datetime_last(self, test_images):
        """Test that DateTime is used as fallback."""
        image_path = test_images / "minimal.jpg"

        # Set only DateTime
        exif = ExifImage(image_path)
        exif.set_datetime(datetime(2025, 6, 20, 10, 0, 0), tags=["DateTime"])
        exif.save()

        # get_datetime should return DateTime
        exif_verify = ExifImage(image_path)
        dt = exif_verify.get_datetime()
        assert dt == datetime(2025, 6, 20, 10, 0, 0)
