"""Tests for tag value validation."""

import pytest
from tagkit.core.tag import ExifTag
from tagkit.core.exceptions import TagTypeError
from tagkit.core.validation import validate_tag_value


class TestTagValueValidation:
    """Test suite for tag value validation."""

    def test_ascii_valid_string(self):
        """Test that ASCII tags accept string values."""
        # Make (271) is ASCII type
        tag = ExifTag(id=271, value="Canon", ifd="IFD0")
        assert tag.value == "Canon"

    def test_ascii_invalid_bytes(self):
        """Test that ASCII tags reject bytes values."""
        with pytest.raises(TagTypeError, match="Expected a string"):
            ExifTag(id=271, value=b"Canon", ifd="IFD0")

    def test_ascii_invalid_int(self):
        """Test that ASCII tags reject integer values."""
        with pytest.raises(TagTypeError, match="Expected a string"):
            ExifTag(id=271, value=123, ifd="IFD0")

    def test_undefined_valid_bytes(self):
        """Test that UNDEFINED tags accept bytes values."""
        # UserComment (37510) is UNDEFINED type
        tag = ExifTag(id=37510, value=b"\xff\xfe\xfd\xfc", ifd="Exif")
        assert tag.value == b"\xff\xfe\xfd\xfc"

    def test_undefined_invalid_string(self):
        """Test that UNDEFINED tags reject string values."""
        with pytest.raises(TagTypeError, match="Expected binary data"):
            ExifTag(id=37510, value="text", ifd="Exif")

    def test_byte_valid_single_int(self):
        """Test that BYTE tags accept single integer values."""
        # Compression (259) is SHORT but we'll use it to test integer validation
        # Let's find a BYTE tag - FileSource (37521) is UNDEFINED, not BYTE
        # WhitePoint (318) is RATIONAL not BYTE
        # Let's use a generic approach - testing the validation function directly
        validate_tag_value(259, "Compression", "BYTE", 6)

    def test_byte_valid_tuple_of_ints(self):
        """Test that BYTE tags accept tuple of integers."""
        validate_tag_value(259, "Test", "BYTE", (1, 2, 3))

    def test_byte_invalid_out_of_range(self):
        """Test that BYTE tags reject out-of-range values."""
        with pytest.raises(TagTypeError, match="BYTE values must be in range 0-255"):
            validate_tag_value(259, "Test", "BYTE", 256)

    def test_byte_invalid_negative(self):
        """Test that BYTE tags reject negative values."""
        with pytest.raises(TagTypeError, match="BYTE values must be in range 0-255"):
            validate_tag_value(259, "Test", "BYTE", -1)

    def test_short_valid_int(self):
        """Test that SHORT tags accept integer values."""
        # Compression (259) is SHORT type
        tag = ExifTag(id=259, value=6, ifd="IFD0")
        assert tag.value == 6

    def test_short_invalid_out_of_range(self):
        """Test that SHORT tags reject out-of-range values."""
        with pytest.raises(TagTypeError, match="SHORT values must be in range 0-65535"):
            ExifTag(id=259, value=65536, ifd="IFD0")

    def test_short_invalid_string(self):
        """Test that SHORT tags reject string values."""
        with pytest.raises(TagTypeError, match="Expected an integer"):
            ExifTag(id=259, value="6", ifd="IFD0")

    def test_long_valid_int(self):
        """Test that LONG tags accept integer values."""
        # ImageWidth (256) is LONG type
        tag = ExifTag(id=256, value=1920, ifd="IFD0")
        assert tag.value == 1920

    def test_long_invalid_out_of_range(self):
        """Test that LONG tags reject out-of-range values."""
        with pytest.raises(
            TagTypeError, match="LONG values must be in range 0-4294967295"
        ):
            ExifTag(id=256, value=4294967296, ifd="IFD0")

    def test_rational_valid_tuple(self):
        """Test that RATIONAL tags accept tuple of 2 ints."""
        # ExposureTime (33434) is RATIONAL type
        tag = ExifTag(id=33434, value=(1, 100), ifd="Exif")
        assert tag.value == (1, 100)

    def test_rational_valid_sequence(self):
        """Test that RATIONAL tags accept sequence of rationals."""
        # XResolution (282) is RATIONAL type
        tag = ExifTag(id=282, value=(72, 1), ifd="IFD0")
        assert tag.value == (72, 1)

    def test_rational_invalid_float(self):
        """Test that RATIONAL tags reject float values."""
        with pytest.raises(
            TagTypeError,
            match="Expected a rational \\(tuple of 2 ints\\) or tuple of rationals",
        ):
            ExifTag(id=33434, value=0.01, ifd="Exif")

    def test_rational_invalid_zero_denominator(self):
        """Test that RATIONAL tags reject zero denominator."""
        with pytest.raises(TagTypeError, match="denominator cannot be zero"):
            ExifTag(id=33434, value=(1, 0), ifd="Exif")

    def test_rational_invalid_negative(self):
        """Test that RATIONAL tags reject negative values."""
        with pytest.raises(TagTypeError, match="RATIONAL values must be non-negative"):
            ExifTag(id=33434, value=(-1, 100), ifd="Exif")

    def test_srational_valid_negative(self):
        """Test that SRATIONAL tags accept negative values."""
        # ExposureBiasValue (37380) is SRATIONAL type
        tag = ExifTag(id=37380, value=(-1, 3), ifd="Exif")
        assert tag.value == (-1, 3)

    def test_srational_invalid_zero_denominator(self):
        """Test that SRATIONAL tags reject zero denominator."""
        with pytest.raises(TagTypeError, match="denominator cannot be zero"):
            ExifTag(id=37380, value=(1, 0), ifd="Exif")

    def test_float_valid_float(self):
        """Test that FLOAT tags accept float values."""
        # We don't have many FLOAT tags in the registry, so we'll use validation directly
        validate_tag_value(999, "TestFloat", "FLOAT", 3.14159)

    def test_float_valid_int(self):
        """Test that FLOAT tags accept int values (which can be cast to float)."""
        validate_tag_value(999, "TestFloat", "FLOAT", 42)

    def test_float_invalid_string(self):
        """Test that FLOAT tags reject string values."""
        with pytest.raises(TagTypeError, match="Expected a float"):
            validate_tag_value(999, "TestFloat", "FLOAT", "3.14")

    def test_validate_tag_value_function(self):
        """Test the validate_tag_value function directly."""
        # Should not raise for valid values
        validate_tag_value(271, "Make", "ASCII", "Canon")
        validate_tag_value(33434, "ExposureTime", "RATIONAL", (1, 100))
        validate_tag_value(37510, "UserComment", "UNDEFINED", b"test")

        # Should raise for invalid values
        with pytest.raises(TagTypeError):
            validate_tag_value(271, "Make", "ASCII", 123)

    def test_validation_on_write_tag(self, test_images):
        """Test that validation happens when using write_tag method."""
        from tagkit import ExifImage

        exif = ExifImage(test_images / "minimal.jpg")

        # Valid write should work
        exif.write_tag("Make", "Canon")
        assert exif.tags["Make"].value == "Canon"

        # Invalid write should fail immediately (not at save time)
        with pytest.raises(TagTypeError, match="Expected a string"):
            exif.write_tag("Make", 123)


class TestValidationErrorMessages:
    """Test that validation errors have clear, helpful messages."""

    def test_ascii_error_message(self):
        """Test error message for ASCII type mismatch."""
        with pytest.raises(
            TagTypeError,
            match=r"Invalid value type for tag 'Make' \(ID: 271, Type: ASCII\)",
        ):
            ExifTag(id=271, value=123, ifd="IFD0")

    def test_rational_error_message(self):
        """Test error message for RATIONAL type mismatch."""
        with pytest.raises(
            TagTypeError,
            match=r"Invalid value type for tag 'ExposureTime' \(ID: 33434, Type: RATIONAL\)",
        ):
            ExifTag(id=33434, value=0.01, ifd="Exif")

    def test_undefined_error_message(self):
        """Test error message for UNDEFINED type mismatch."""
        with pytest.raises(
            TagTypeError,
            match=r"Invalid value type for tag 'UserComment' \(ID: 37510, Type: UNDEFINED\)",
        ):
            ExifTag(id=37510, value="text", ifd="Exif")

    def test_range_error_message(self):
        """Test error message for out-of-range values."""
        with pytest.raises(TagTypeError, match="SHORT values must be in range 0-65535"):
            ExifTag(id=259, value=70000, ifd="IFD0")


class TestValidationEdgeCases:
    """Test edge cases in validation."""

    def test_empty_string_valid(self):
        """Test that empty strings are valid for ASCII tags."""
        tag = ExifTag(id=271, value="", ifd="IFD0")
        assert tag.value == ""

    def test_empty_bytes_valid(self):
        """Test that empty bytes are valid for UNDEFINED tags."""
        tag = ExifTag(id=37510, value=b"", ifd="Exif")
        assert tag.value == b""

    def test_single_element_tuple_as_collection(self):
        """Test that single-element tuples are handled correctly."""
        # A single rational in a tuple
        tag = ExifTag(id=33434, value=(1, 100), ifd="Exif")
        assert tag.value == (1, 100)

    def test_multiple_rationals(self):
        """Test that sequences of rationals are validated correctly."""
        # GPSLatitude (2) accepts a sequence of 3 rationals
        validate_tag_value(2, "GPSLatitude", "RATIONAL", ((45, 1), (30, 1), (15, 1)))

    def test_validation_happens_at_creation(self):
        """Test that validation happens immediately at tag creation, not later."""
        # This should fail immediately
        with pytest.raises(TagTypeError):
            tag = ExifTag(id=271, value=123, ifd="IFD0")

        # The error should occur before the tag object is created
        # So we can't access any properties
