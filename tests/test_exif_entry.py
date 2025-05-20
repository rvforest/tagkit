import base64
import pytest

from tagkit.exif_entry import ExifEntry
from tagkit.types import IfdName

# Test data
UTF8_BYTES = b'Canon'
NON_UTF8_BYTES = b'\x89PNG\r\n'
NON_UTF8_HEX = NON_UTF8_BYTES.hex()
NON_UTF8_BASE64 = base64.b64encode(NON_UTF8_BYTES).decode('ascii')


def test_exifentry_properties_ascii():
    tag_id = 271  # 'Make', type 'ASCII'
    ifd: IfdName = "IFD0"
    value = "Canon"
    entry = ExifEntry(id=tag_id, value=value, ifd=ifd)
    assert entry.name == "Make"
    assert entry.exif_type == "ASCII"
    assert entry.format() == value
    d = entry.to_dict()
    assert d["id"] == tag_id
    assert d["name"] == "Make"
    assert d["value"] == value
    assert d["ifd"] == ifd


@pytest.mark.parametrize("binary_format,expected_output", [
    ("bytes", str(NON_UTF8_BYTES)),
    ("hex", f"hex:{NON_UTF8_HEX}"),
    ("base64", f"base64:{NON_UTF8_BASE64}"),
])
def test_non_utf8_bytes_formatting(binary_format, expected_output):
    """Test non-UTF-8 bytes formatting with different binary formats."""
    entry = ExifEntry(id=37510, value=NON_UTF8_BYTES, ifd="Exif")
    # Non-UTF-8 bytes should be formatted according to binary_format
    assert entry.format(binary_format=binary_format) == expected_output
    assert entry.to_dict(binary_format=binary_format)["value"] == expected_output


def test_render_bytes_false():
    """Test that render_bytes=False shows a placeholder for binary data."""
    entry = ExifEntry(id=37510, value=NON_UTF8_BYTES, ifd="Exif")
    assert entry.format(render_bytes=False) == f"<bytes: {len(NON_UTF8_BYTES)}>"
    assert entry.to_dict(render_bytes=False)["value"] == f"<bytes: {len(NON_UTF8_BYTES)}>"


def test_invalid_binary_format():
    """Test that an invalid binary format raises a ValueError."""
    entry = ExifEntry(id=271, value=b'test', ifd="IFD0")
    with pytest.raises(ValueError, match="Unsupported binary format"):
        entry.format(binary_format="invalid_format")
