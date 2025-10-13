"""
Tag value validation using Pydantic.

This module provides validation for EXIF tag values based on their EXIF type.
Validation ensures that values conform to the EXIF specification before they
are used to create ExifTag objects.
"""

from typing import Any, Union, cast

from pydantic import BaseModel, field_validator, Field

from tagkit.core.exceptions import TagTypeError
from tagkit.core.types import (
    TagValue,
    Rational,
    RationalCollection,
    IntCollection,
    FloatCollection,
)


class TagValueValidator(BaseModel):
    """
    Validates a tag value against its expected EXIF type.

    This validator ensures that tag values conform to the EXIF specification
    before they are stored in an ExifTag object.

    Args:
        tag_id: The EXIF tag ID.
        tag_name: The human-readable tag name.
        exif_type: The EXIF data type (ASCII, BYTE, SHORT, LONG, RATIONAL, SRATIONAL, FLOAT, UNDEFINED).
        value: The tag value to validate.

    Raises:
        TagTypeError: If the value does not match the expected EXIF type.
    """

    tag_id: int
    tag_name: str
    exif_type: str
    value: TagValue

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("value")
    @classmethod
    def validate_value_type(cls, v: Any, info) -> TagValue:
        """Validate that the value matches the expected EXIF type."""
        # Get the exif_type from the validation info
        # Note: At this point, exif_type might not be in info.data yet
        # So we need to handle validation in model_validator instead
        return v

    def model_post_init(self, __context: Any) -> None:
        """Validate the value after the model is fully initialized."""
        self._validate_exif_type()

    def _validate_exif_type(self) -> None:
        """Validate that the value matches the EXIF type."""
        value = self.value
        exif_type = self.exif_type

        # ASCII: string values
        if exif_type == "ASCII":
            if not isinstance(value, str):
                raise TagTypeError(
                    self.tag_id,
                    self.tag_name,
                    exif_type,
                    value,
                    "Expected a string (str).",
                )

        # UNDEFINED: binary data
        elif exif_type == "UNDEFINED":
            if not isinstance(value, bytes):
                raise TagTypeError(
                    self.tag_id,
                    self.tag_name,
                    exif_type,
                    value,
                    "Expected binary data (bytes).",
                )

        # BYTE, SHORT, LONG: integers or sequences of integers
        elif exif_type in ("BYTE", "SHORT", "LONG"):
            if isinstance(value, int):
                self._validate_integer_range(value, exif_type)
            elif isinstance(value, tuple) and all(isinstance(x, int) for x in value):
                for val in value:
                    if isinstance(val, int):  # Type narrowing for mypy
                        self._validate_integer_range(val, exif_type)
            else:
                raise TagTypeError(
                    self.tag_id,
                    self.tag_name,
                    exif_type,
                    value,
                    f"Expected an integer or tuple of integers.",
                )

        # RATIONAL, SRATIONAL: rational numbers or sequences of rationals
        elif exif_type in ("RATIONAL", "SRATIONAL"):
            if self._is_rational(value):
                # Type narrowing - we know it's a Rational now
                rat_value = cast(Rational, value)
                self._validate_rational(rat_value, exif_type)
            elif self._is_rational_sequence(value):
                # Type narrowing - we know it's a sequence of Rationals now
                rat_seq = cast(tuple, value)
                for rat in rat_seq:
                    rat_value = cast(Rational, rat)
                    self._validate_rational(rat_value, exif_type)
            else:
                raise TagTypeError(
                    self.tag_id,
                    self.tag_name,
                    exif_type,
                    value,
                    "Expected a rational (tuple of 2 ints) or tuple of rationals.",
                )

        # FLOAT: floating point or sequences of floats
        elif exif_type == "FLOAT":
            if not isinstance(value, (float, int)):
                if not (
                    isinstance(value, tuple)
                    and all(isinstance(x, (float, int)) for x in value)
                ):
                    raise TagTypeError(
                        self.tag_id,
                        self.tag_name,
                        exif_type,
                        value,
                        "Expected a float or tuple of floats.",
                    )

        else:
            # Unknown EXIF type - should not happen with valid registry
            raise TagTypeError(
                self.tag_id,
                self.tag_name,
                exif_type,
                value,
                f"Unknown EXIF type '{exif_type}'.",
            )

    def _validate_integer_range(self, value: int, exif_type: str) -> None:
        """Validate that an integer is within the valid range for the EXIF type."""
        if exif_type == "BYTE":
            if not (0 <= value <= 255):
                raise TagTypeError(
                    self.tag_id,
                    self.tag_name,
                    exif_type,
                    value,
                    "BYTE values must be in range 0-255.",
                )
        elif exif_type == "SHORT":
            if not (0 <= value <= 65535):
                raise TagTypeError(
                    self.tag_id,
                    self.tag_name,
                    exif_type,
                    value,
                    "SHORT values must be in range 0-65535.",
                )
        elif exif_type == "LONG":
            if not (0 <= value <= 4294967295):
                raise TagTypeError(
                    self.tag_id,
                    self.tag_name,
                    exif_type,
                    value,
                    "LONG values must be in range 0-4294967295.",
                )

    def _is_rational(self, value: Any) -> bool:
        """Check if a value is a rational (tuple of 2 ints)."""
        return (
            isinstance(value, tuple)
            and len(value) == 2
            and isinstance(value[0], int)
            and isinstance(value[1], int)
        )

    def _is_rational_sequence(self, value: Any) -> bool:
        """Check if a value is a sequence of rationals."""
        if not isinstance(value, tuple) or len(value) == 0:
            return False
        # Check if all elements are rationals
        return all(self._is_rational(x) for x in value)

    def _validate_rational(self, value: Rational, exif_type: str) -> None:
        """Validate a rational value."""
        numerator, denominator = value
        if denominator == 0:
            raise TagTypeError(
                self.tag_id,
                self.tag_name,
                exif_type,
                value,
                "Rational denominator cannot be zero.",
            )

        # RATIONAL uses unsigned integers
        if exif_type == "RATIONAL":
            if numerator < 0 or denominator < 0:
                raise TagTypeError(
                    self.tag_id,
                    self.tag_name,
                    exif_type,
                    value,
                    "RATIONAL values must be non-negative.",
                )


def validate_tag_value(
    tag_id: int, tag_name: str, exif_type: str, value: TagValue
) -> None:
    """
    Validate a tag value against its EXIF type.

    Args:
        tag_id: The EXIF tag ID.
        tag_name: The human-readable tag name.
        exif_type: The EXIF data type.
        value: The tag value to validate.

    Raises:
        TagTypeError: If the value does not match the expected EXIF type.

    Example:
        >>> validate_tag_value(271, 'Make', 'ASCII', 'Canon')  # Valid
        >>> validate_tag_value(271, 'Make', 'ASCII', 123)  # Raises TagTypeError
    """
    TagValueValidator(
        tag_id=tag_id, tag_name=tag_name, exif_type=exif_type, value=value
    )
