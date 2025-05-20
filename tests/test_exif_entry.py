import base64

from tagkit.exif_entry import ExifEntry
from tagkit.types import IfdName


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


def test_exifentry_properties_bytes_utf8():
    """Test that UTF-8 decodable bytes are properly formatted."""
    tag_id = 271  # 'Make', type 'ASCII'
    ifd: IfdName = "IFD0"
    value = b"Canon"
    entry = ExifEntry(id=tag_id, value=value, ifd=ifd)
    assert entry.format() == "Canon"
    assert entry.format(render_bytes=True) == "Canon"
    assert entry.format(render_bytes=False) == "Canon"


def test_exifentry_properties_non_utf8_bytes():
    """Test that non-UTF-8 bytes are properly formatted with base64 or placeholder."""
    tag_id = 271  # 'Make', type 'ASCII'
    ifd: IfdName = "IFD0"
    value = b"\xff\xfe\xfd\xfc"
    entry = ExifEntry(id=tag_id, value=value, ifd=ifd)
    expected_b64 = base64.b64encode(value).decode("ascii")
    assert entry.format(render_bytes=True) == expected_b64
    assert entry.format(render_bytes=False) == "<bytes>"
