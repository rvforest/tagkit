from pathlib import Path
from typing import Literal, TypedDict, Union

FilePath = Union[str, Path]

# ExifTypes
IntCollection = tuple[int, ...]
FloatCollection = tuple[float, ...]
Rational = tuple[int, int]
RationalCollection = tuple[Rational]
ExifTag = Union[
    bytes,
    float,
    int,
    str,
    FloatCollection,
    IntCollection,
    Rational,
    RationalCollection,
]
ExifIfdCollection = dict[str, dict[int, ExifTag]]
ExifType = Literal["ASCII", "BYTE", "RATIONAL", "SRATIONAL", "SHORT", "UNDEFINED"]
IfdName = Literal["IFD0", "IFD1", "Exif", "GPS", "Interop"]


class ExifTagInfo(TypedDict):
    id: int
    name: str
    val: ExifTag
