"""Shared helpers for tests."""

from typing import Literal

from tagkit.core.types import IfdName

FixtureIfd = Literal["0th", "1st", "Exif", "GPS", "Interop"]

_FIXTURE_IFDS: dict[FixtureIfd, IfdName] = {
    "0th": "IFD0",
    "1st": "IFD1",
    "Exif": "Exif",
    "GPS": "GPS",
    "Interop": "Interop",
}


def fixture_ifd(ifd: FixtureIfd) -> IfdName:
    """Map fixture/piexif IFD names to tagkit IFD names."""
    return _FIXTURE_IFDS[ifd]
