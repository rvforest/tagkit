"""
Image handling functionality for tagkit.

This module contains components for working with image files
and their EXIF metadata.
"""

from tagkit.image.collection import ExifImageCollection
from tagkit.image.exif import ExifImage

__all__ = ["ExifImageCollection", "ExifImage"]
