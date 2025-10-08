import importlib.metadata as _importlib_metadata

try:
    __version__ = _importlib_metadata.version(__name__)
except _importlib_metadata.PackageNotFoundError:
    # editable/dev installs won't have package metadata
    __version__ = "0+unknown"

from tagkit.image import ExifImageCollection, ExifImage

__all__ = ["ExifImageCollection", "ExifImage", "__version__"]
