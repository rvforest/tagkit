import importlib.metadata as _importlib_metadata

try:
    __version__ = _importlib_metadata.version(__name__)
except _importlib_metadata.PackageNotFoundError:
    # editable/dev installs won't have package metadata
    __version__ = "0+unknown"

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
    "__version__",
]
