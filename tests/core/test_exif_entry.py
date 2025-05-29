import base64
import pytest

from tagkit.core.tag import ExifTag
from tagkit.core.types import IfdName

# Test data
UTF8_BYTES = b"Canon"
NON_UTF8_BYTES = b"\x89PNG\r\n"
NON_UTF8_HEX = NON_UTF8_BYTES.hex()
NON_UTF8_BASE64 = base64.b64encode(NON_UTF8_BYTES).decode("ascii")


def test_exiftag_properties_ascii():
    tag_id = 271  # 'Make', type 'ASCII'
    ifd: IfdName = "IFD0"
    value = "Canon"
    entry = ExifTag(id=tag_id, value=value, ifd=ifd)
    assert entry.name == "Make"
    assert entry.exif_type == "ASCII"
    assert entry.format() == value
    d = entry.as_dict()
    assert d["id"] == tag_id
    assert d["name"] == "Make"
    assert d["value"] == value
    assert d["ifd"] == ifd


@pytest.mark.parametrize(
    "binary_format,expected_output",
    [
        ("bytes", str(NON_UTF8_BYTES)),
        ("hex", f"hex:{NON_UTF8_HEX}"),
        ("base64", f"base64:{NON_UTF8_BASE64}"),
    ],
)
def test_non_utf8_bytes_formatting(binary_format, expected_output):
    """Test non-UTF-8 bytes formatting with different binary formats."""
    entry = ExifTag(id=37510, value=NON_UTF8_BYTES, ifd="Exif")
    # Non-UTF-8 bytes should be formatted according to binary_format
    assert entry.format(binary_format=binary_format) == expected_output
    assert entry.as_dict(binary_format=binary_format)["value"] == expected_output


def test_binary_format_none():
    """Test that binary_format=None shows a placeholder for binary data."""
    entry = ExifTag(id=37510, value=NON_UTF8_BYTES, ifd="Exif")
    assert entry.format(binary_format=None) == f"<bytes: {len(NON_UTF8_BYTES)}>"
    assert (
        entry.as_dict(binary_format=None)["value"] == f"<bytes: {len(NON_UTF8_BYTES)}>"
    )


def test_invalid_binary_format():
    """Test that an invalid binary format raises a ValueError."""
    entry = ExifTag(id=271, value=b"test", ifd="IFD0")
    with pytest.raises(ValueError, match="Unsupported binary format"):
        entry.format(binary_format="invalid_format")
