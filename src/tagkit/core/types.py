"""
Type definitions for tagkit.

This module contains type definitions used throughout the tagkit package.
"""

from pathlib import Path
from typing import Literal, TypedDict, Union

FilePath = Union[str, Path]

# EXIF specifies ASCII, but UTF-8 is commonly used for text values.
STR_ENCODING = "utf-8"

# ExifTypes
IntCollection = tuple[int, ...]
FloatCollection = tuple[float, ...]
Rational = tuple[int, int]
Rational2 = tuple[Rational, Rational]
Rational3 = tuple[Rational, Rational, Rational]
Rational4 = tuple[Rational, Rational, Rational, Rational]
RationalCollection = tuple[Rational, ...]
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
ExifType = Literal[
    "ASCII",
    "BYTE",
    "FLOAT",
    "LONG",
    "RATIONAL",
    "SHORT",
    "SRATIONAL",
    "UNDEFINED",
]
ExifCount = Union[int, tuple[int, ...], Literal["any"]]
IfdName = Literal["IFD0", "IFD1", "Exif", "GPS", "Interop"]
TagNamespace = Literal["Image", "Exif", "GPS", "Interop"]

# Supported directory vocabulary by tag family. The first IFD is tagkit's default.
NAMESPACE_IFDS: dict[TagNamespace, tuple[IfdName, ...]] = {
    "Image": ("IFD0", "IFD1"),
    "Exif": ("Exif",),
    "GPS": ("GPS",),
    "Interop": ("Interop",),
}


class TagValueInfo(TypedDict):
    """Information about an EXIF tag."""

    id: int
    name: str
    val: TagValue
