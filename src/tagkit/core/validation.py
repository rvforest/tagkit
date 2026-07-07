"""Validation helpers for EXIF-shaped tag values."""

from collections.abc import Sequence
from typing import Any, cast

from tagkit.core.exceptions import ValidationError
from tagkit.core.registry import ExifTagDefinition
from tagkit.core.types import ExifCount, ExifType, Rational, TagValue


def validate_tag_value(definition: ExifTagDefinition, value: TagValue) -> TagValue:
    """
    Validate and structurally normalize a tag value for a definition.

    The low-level write API expects EXIF-shaped values. This function only
    converts lists to tuples when the resulting shape is otherwise valid.
    """
    normalized = _normalize_sequences(value)
    errors: list[str] = []
    for exif_type in definition.allowed_types:
        try:
            return _validate_for_type(definition, normalized, exif_type)
        except ValidationError as exc:
            errors.append(str(exc))

    expected = _format_expected(definition)
    received = f"{type(value).__name__}: {value!r}"
    raise ValidationError(
        f"Invalid value for {definition.name} "
        f"(IFD {definition.ifd}, tag ID {definition.tag_id}). "
        f"Expected {expected}; received {received}. "
        f"Details: {'; '.join(errors)}"
    )


def _normalize_sequences(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_normalize_sequences(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_normalize_sequences(item) for item in value)
    return value


def _validate_for_type(
    definition: ExifTagDefinition, value: Any, exif_type: ExifType
) -> TagValue:
    if exif_type == "ASCII":
        if not isinstance(value, str):
            raise ValidationError("ASCII values must be str")
        _validate_ascii_count(definition.count, value)
        return value

    if exif_type == "UNDEFINED":
        if not isinstance(value, bytes):
            raise ValidationError("UNDEFINED values must be bytes")
        _validate_count(definition.count, len(value))
        return value

    if exif_type == "BYTE":
        return _validate_integer_value(definition.count, value, 0, 255, "BYTE")

    if exif_type == "SHORT":
        return _validate_integer_value(definition.count, value, 0, 65535, "SHORT")

    if exif_type == "LONG":
        return _validate_integer_value(definition.count, value, 0, 4294967295, "LONG")

    if exif_type == "RATIONAL":
        return _validate_rational_value(definition.count, value, signed=False)

    if exif_type == "SRATIONAL":
        return _validate_rational_value(definition.count, value, signed=True)

    if exif_type == "FLOAT":
        return _validate_float_value(definition.count, value)

    raise ValidationError(f"unsupported EXIF type {exif_type}")


def _validate_ascii_count(count: ExifCount | None, value: str) -> None:
    if count is None or count == "any":
        return
    _validate_count(count, len(value) + 1)


def _validate_integer_value(
    count: ExifCount | None, value: Any, minimum: int, maximum: int, label: str
) -> TagValue:
    if isinstance(value, bool):
        raise ValidationError(f"{label} scalar must be int")
    if isinstance(value, int):
        _validate_count(count, 1)
        _validate_integer_range(value, minimum, maximum, label)
        return value
    if _is_plain_sequence(value):
        values = tuple(value)
        _validate_count(count, len(values))
        for item in values:
            if isinstance(item, bool) or not isinstance(item, int):
                raise ValidationError(f"{label} sequences must contain only ints")
            _validate_integer_range(item, minimum, maximum, label)
        return values
    raise ValidationError(f"{label} value must be int or tuple[int, ...]")


def _validate_float_value(count: ExifCount | None, value: Any) -> TagValue:
    if isinstance(value, bool):
        raise ValidationError("FLOAT scalar must be int or float")
    if isinstance(value, (int, float)):
        _validate_count(count, 1)
        return float(value)
    if _is_plain_sequence(value):
        values = tuple(value)
        _validate_count(count, len(values))
        if any(
            isinstance(item, bool) or not isinstance(item, (int, float))
            for item in values
        ):
            raise ValidationError(
                "FLOAT sequences must contain only int or float values"
            )
        return tuple(float(item) for item in values)
    raise ValidationError("FLOAT value must be float or tuple[float, ...]")


def _validate_rational_value(
    count: ExifCount | None, value: Any, *, signed: bool
) -> TagValue:
    if _is_rational(value):
        _validate_count(count, 1)
        rational = cast(Rational, value)
        _validate_rational_components(rational, signed=signed)
        return rational
    if _is_plain_sequence(value):
        values = tuple(value)
        if not values or not all(_is_rational(item) for item in values):
            raise ValidationError("rational sequences must contain rational tuples")
        _validate_count(count, len(values))
        rationals = cast(tuple[Rational, ...], values)
        for rational in rationals:
            _validate_rational_components(rational, signed=signed)
        return rationals
    raise ValidationError(
        "rational value must be tuple[int, int] or tuple of rationals"
    )


def _validate_rational_components(rational: Rational, *, signed: bool) -> None:
    numerator, denominator = rational
    if isinstance(numerator, bool) or isinstance(denominator, bool):
        raise ValidationError("rational components must be ints")
    if not isinstance(numerator, int) or not isinstance(denominator, int):
        raise ValidationError("rational components must be ints")
    if denominator == 0:
        raise ValidationError("rational denominator must not be zero")
    if not signed and (numerator < 0 or denominator < 0):
        raise ValidationError("RATIONAL components must be non-negative")


def _validate_integer_range(value: int, minimum: int, maximum: int, label: str) -> None:
    if value < minimum or value > maximum:
        raise ValidationError(
            f"{label} value {value} outside range {minimum}..{maximum}"
        )


def _validate_count(count: ExifCount | None, actual: int) -> None:
    if count is None or count == "any":
        return
    if actual != count:
        raise ValidationError(f"count {actual} does not match expected count {count}")


def _is_rational(value: Any) -> bool:
    return (
        isinstance(value, tuple)
        and len(value) == 2
        and all(isinstance(item, int) and not isinstance(item, bool) for item in value)
    )


def _is_plain_sequence(value: Any) -> bool:
    return (
        isinstance(value, Sequence)
        and not isinstance(value, (bytes, str))
        and not _is_rational(value)
    )


def _format_expected(definition: ExifTagDefinition) -> str:
    types = " or ".join(definition.allowed_types)
    count = "unspecified" if definition.count is None else definition.count
    return f"type {types}, count {count}"
