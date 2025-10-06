import importlib.metadata

__version__ = importlib.metadata.version(__name__)

from tagkit.image import ExifImageCollection, ExifImage
from tagkit.image.exif import (
    parse_exif_datetime,
    format_exif_datetime,
    DATETIME_TAG_NAMES,
    DATETIME_TAG_PRIMARY,
    DATETIME_FORMAT,
)

__all__ = [
    "ExifImageCollection",
    "ExifImage",
    "parse_exif_datetime",
    "format_exif_datetime",
    "DATETIME_TAG_NAMES",
    "DATETIME_TAG_PRIMARY",
    "DATETIME_FORMAT",
]
