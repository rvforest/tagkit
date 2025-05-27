"""
Type definitions for tagkit.

This module contains type definitions used throughout the tagkit package.
"""

from pathlib import Path
from typing import Literal, TypedDict, Union

FilePath = Union[str, Path]

# ExifTypes
IntCollection = tuple[int, ...]
FloatCollection = tuple[float, ...]
Rational = tuple[int, int]
RationalCollection = tuple[Rational]
TagValue = Union[
    bytes,
    float,
    int,
    str,
    FloatCollection,
    IntCollection,
    Rational,
    RationalCollection,
]
ExifIfdCollection = dict[str, dict[int, TagValue]]
ExifType = Literal["ASCII", "BYTE", "RATIONAL", "SRATIONAL", "SHORT", "UNDEFINED"]
IfdName = Literal["IFD0", "IFD1", "Exif", "GPS", "Interop"]


class TagValueInfo(TypedDict):
    """Information about an EXIF tag."""

    id: int
    name: str
    val: TagValue
