import importlib.metadata

__version__ = importlib.metadata.version(__name__)

from tagkit.core.datetime_utils import (
    DATETIME_FORMAT,
    format_exif_datetime,
    parse_exif_datetime,
)
from tagkit.image import ExifImageCollection, ExifImage
from tagkit.image.exif import (
    DATETIME_TAG_NAMES,
    DATETIME_TAG_PRIMARY,
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
