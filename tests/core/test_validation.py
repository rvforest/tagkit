"""Tests for EXIF value shapes that depend on the declared type."""

import pytest

from tagkit.core.exceptions import ValidationError
from tagkit.core.registry import ExifTagDefinition
from tagkit.core.validation import validate_tag_value


@pytest.mark.parametrize("exif_type", ["BYTE", "SHORT", "LONG", "FLOAT"])
@pytest.mark.parametrize("sequence_type", [tuple, list])
def test_two_integer_components_follow_declared_type(exif_type, sequence_type):
    definition = ExifTagDefinition(
        namespace="Image",
        tag_id=530,
        name="TwoComponents",
        allowed_types=(exif_type,),
        allowed_ifds=("IFD0",),
        count=2,
    )

    result = validate_tag_value(definition, sequence_type([2, 2]))

    assert result == (2, 2)
    assert isinstance(result, tuple)
    expected_type = float if exif_type == "FLOAT" else int
    assert all(type(component) is expected_type for component in result)


@pytest.mark.parametrize(
    "exif_type, value",
    [
        ("BYTE", (0, 256)),
        ("SHORT", (0, 65536)),
        ("LONG", (0, 4294967296)),
        ("BYTE", (-1, 0)),
        ("SHORT", (1, True)),
        ("LONG", (1, 2.0)),
        ("FLOAT", (1, True)),
        ("FLOAT", (1, "2")),
    ],
)
def test_two_component_sequences_still_validate_each_item(exif_type, value):
    definition = ExifTagDefinition(
        namespace="Image",
        tag_id=530,
        name="TwoComponents",
        allowed_types=(exif_type,),
        allowed_ifds=("IFD0",),
        count=2,
    )

    with pytest.raises(ValidationError):
        validate_tag_value(definition, value)


@pytest.mark.parametrize("count", [3, "any", None])
def test_ascii_count_uses_encoded_bytes_and_terminator(count):
    definition = ExifTagDefinition(
        namespace="Image",
        tag_id=271,
        name="TextField",
        allowed_types=("ASCII",),
        allowed_ifds=("IFD0",),
        count=count,
    )

    assert validate_tag_value(definition, "é") == "é"


def test_ascii_count_rejects_multibyte_value_with_too_many_bytes():
    definition = ExifTagDefinition(
        namespace="GPS",
        tag_id=1,
        name="GPSLatitudeRef",
        allowed_types=("ASCII",),
        allowed_ifds=("GPS",),
        count=2,
    )

    with pytest.raises(
        ValidationError, match="count 3 does not match expected count 2"
    ):
        validate_tag_value(definition, "é")
