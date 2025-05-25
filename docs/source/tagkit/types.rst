tagkit.types
============

The ``tagkit.types`` module defines type aliases and data structures used throughout tagkit for EXIF data handling.

**Usage Example:**

.. code-block:: python

   from tagkit.types import FilePath
   # Use FilePath in your type hints

.. autosummary::
   :toctree: _autosummary

   .. FilePath
   .. IntCollection
   .. FloatCollection
   .. Rational
   .. RationalCollection
   .. ExifTag
   .. ExifIfdCollection
   .. ExifType
   .. IfdName
   ExifTagInfo

.. automodule:: tagkit.types
   :members:
   :undoc-members:
   :show-inheritance:

This module defines type aliases and data structures used throughout tagkit for EXIF data handling.

Type Aliases
------------

- **FilePath**: ``Union[str, Path]`` — Represents a file path as a string or Path object.
- **IntCollection**: ``tuple[int, ...]`` — A tuple of integers.
- **FloatCollection**: ``tuple[float, ...]`` — A tuple of floats.
- **Rational**: ``tuple[int, int]`` — A tuple representing a rational number (numerator, denominator).
- **RationalCollection**: ``tuple[Rational]`` — A tuple of rational numbers.
- **ExifTag**: ``Union[bytes, float, int, str, FloatCollection, IntCollection, Rational, RationalCollection]`` — Represents possible EXIF tag value types.
- **ExifIfdCollection**: ``dict[str, dict[int, ExifTag]]`` — Mapping from IFD name to tag ID to EXIF tag value.
- **ExifType**: ``Literal["ASCII", "BYTE", "RATIONAL", "SRATIONAL", "SHORT", "UNDEFINED"]`` — EXIF type names.
- **IfdName**: ``Literal["IFD0", "IFD1", "Exif", "GPS", "Interop"]`` — EXIF IFD names.

TypedDicts
----------

- **ExifTagInfo**: ``{ id: int, name: str, val: ExifTag }`` — Information about an EXIF tag.
