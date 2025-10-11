"""Utility functions for working with EXIF datetime values."""

from __future__ import annotations

from datetime import datetime

from tagkit.core.exceptions import DateTimeError
from tagkit.core.types import TagValue

DATETIME_FORMAT = "%Y:%m:%d %H:%M:%S"


def parse_exif_datetime(datetime_str: TagValue) -> datetime:
    """Convert an EXIF datetime string into a :class:`datetime` instance.

    Args:
        datetime_str: EXIF datetime string in the format ``"YYYY:MM:DD HH:MM:SS"``.

    Returns:
        Parsed datetime object.

    Raises:
        DateTimeError: If ``datetime_str`` is not a valid EXIF datetime string.
    """
    if not isinstance(datetime_str, str):
        raise DateTimeError(datetime_str)

    try:
        return datetime.strptime(datetime_str, DATETIME_FORMAT)
    except ValueError as exc:
        raise DateTimeError(f"Invalid EXIF datetime format: {datetime_str}") from exc


def format_exif_datetime(dt: datetime) -> str:
    """Format a :class:`datetime` object as an EXIF datetime string.

    Args:
        dt: Datetime object to format.

    Returns:
        EXIF datetime string in the format ``"YYYY:MM:DD HH:MM:SS"``.
    """
    return dt.strftime(DATETIME_FORMAT)
