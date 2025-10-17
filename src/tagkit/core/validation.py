"""
Tag value validation functions.

This module provides functions to validate EXIF tag values against their
expected types before writing them to images.
"""

from typing import Union

from tagkit.core.exceptions import TagTypeError
from tagkit.core.registry import tag_registry
from tagkit.core.types import (
    TagValue,
    FloatCollection,
    IntCollection,
    Rational,
    RationalCollection,
)


def validate_tag_value(tag_id: int, value: TagValue) -> None:
    """
    Validate that a tag value matches the expected EXIF type.

    Args:
        tag_id: The EXIF tag ID
        value: The value to validate

    Raises:
        TagTypeError: If the value type does not match the expected EXIF type
    """
    exif_type = tag_registry.get_exif_type(tag_id)
    tag_name = tag_registry.resolve_tag_name(tag_id)

    # Dispatch to type-specific validators
    validators = {
        "ASCII": _validate_ascii,
        "BYTE": _validate_byte,
        "SHORT": _validate_short,
        "LONG": _validate_long,
        "RATIONAL": _validate_rational,
        "SRATIONAL": _validate_srational,
        "FLOAT": _validate_float,
        "UNDEFINED": _validate_undefined,
    }

    validator = validators.get(exif_type)
    if validator is None:
        # Unknown type - skip validation but don't fail
        return

    if not validator(value):
        raise TagTypeError(tag_name, tag_id, exif_type, value)


def _validate_ascii(value: TagValue) -> bool:
    """Validate ASCII type - expects string."""
    return isinstance(value, str)


def _validate_byte(value: TagValue) -> bool:
    """Validate BYTE type - expects int or tuple of ints."""
    if isinstance(value, int):
        return 0 <= value <= 255
    if isinstance(value, tuple):
        return all(isinstance(v, int) and 0 <= v <= 255 for v in value)
    return False


def _validate_short(value: TagValue) -> bool:
    """Validate SHORT type - expects int or tuple of ints in range 0-65535."""
    if isinstance(value, int):
        return 0 <= value <= 65535
    if isinstance(value, tuple):
        return all(isinstance(v, int) and 0 <= v <= 65535 for v in value)
    return False


def _validate_long(value: TagValue) -> bool:
    """Validate LONG type - expects int or tuple of ints in range 0-4294967295."""
    if isinstance(value, int):
        return 0 <= value <= 4294967295
    if isinstance(value, tuple):
        return all(isinstance(v, int) and 0 <= v <= 4294967295 for v in value)
    return False


def _validate_rational(value: TagValue) -> bool:
    """Validate RATIONAL type - expects (int, int) tuple or tuple of such tuples."""
    if isinstance(value, tuple) and len(value) == 2:
        # Single rational: (numerator, denominator)
        return (
            isinstance(value[0], int)
            and isinstance(value[1], int)
            and value[0] >= 0
            and value[1] >= 0
        )
    if isinstance(value, tuple):
        # Collection of rationals
        return all(
            isinstance(v, tuple)
            and len(v) == 2
            and isinstance(v[0], int)
            and isinstance(v[1], int)
            and v[0] >= 0
            and v[1] >= 0
            for v in value
        )
    return False


def _validate_srational(value: TagValue) -> bool:
    """Validate SRATIONAL type - signed rational (int, int) or tuple of such tuples."""
    if isinstance(value, tuple) and len(value) == 2:
        # Single signed rational: (numerator, denominator)
        return isinstance(value[0], int) and isinstance(value[1], int)
    if isinstance(value, tuple):
        # Collection of signed rationals
        return all(
            isinstance(v, tuple)
            and len(v) == 2
            and isinstance(v[0], int)
            and isinstance(v[1], int)
            for v in value
        )
    return False


def _validate_float(value: TagValue) -> bool:
    """Validate FLOAT type - expects float or tuple of floats."""
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, tuple):
        return all(isinstance(v, (int, float)) for v in value)
    return False


def _validate_undefined(value: TagValue) -> bool:
    """Validate UNDEFINED type - accepts bytes or any other type."""
    # UNDEFINED type is flexible - can be bytes or other types
    # We'll be permissive here
    return True
