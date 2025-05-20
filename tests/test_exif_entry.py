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


def test_exifentry_properties_bytes():
    tag_id = 271  # 'Make', type 'ASCII'
    ifd: IfdName = "IFD0"
    value = b"Canon"
    entry = ExifEntry(id=tag_id, value=value, ifd=ifd)
    # Should decode as utf-8
    assert entry.format() == "Canon"

    # Now with non-utf8 bytes
    value = b"\xff\xfe\xfd\xfc"
    entry = ExifEntry(id=tag_id, value=value, ifd=ifd)
    expected_b64 = base64.b64encode(value).decode("ascii")
    assert entry.format() == expected_b64
