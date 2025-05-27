import importlib.metadata

__version__ = importlib.metadata.version(__name__)

from tagkit.image import ExifImageCollection, ExifImage

__all__ = ["ExifImageCollection", "ExifImage"]
