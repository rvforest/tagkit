import pytest
from tagkit.tag_io.piexif_io import (
    _conform_ifd_names,
    _tag_is_ascii,
    PiexifBackend,
    tagkit_to_piexif_ifd_map,
)
from tagkit.core.tag import ExifTag
from tagkit.core.types import IfdName
from unittest.mock import patch, MagicMock


def test_conform_ifd_names():
    # Only keys in tagkit_to_piexif_ifd_map should be present
    piexif_tags = {"0th": {1: "a"}, "Exif": {2: "b"}, "Other": {3: "c"}}
    result = _conform_ifd_names(piexif_tags)  # type: ignore
    assert "IFD0" in result
    assert "Exif" in result
    assert "Other" not in result
    assert result["IFD0"] == {1: "a"}
    assert result["Exif"] == {2: "b"}


def test_tag_is_ascii():
    # 271 is 'Make', which is ASCII in the registry
    assert _tag_is_ascii(271) is True
    entry = ExifTag(271, "Canon", "IFD0")
    assert _tag_is_ascii(entry) is True
    # 33434 is 'ExposureTime', which is RATIONAL
    assert _tag_is_ascii(33434) is False


def test_load_tags_and_save_tags():
    backend = PiexifBackend()
    fake_path = "fake.jpg"
    fake_raw = {"0th": {271: b"Canon"}, "Exif": {33434: 123.0}}
    # Patch piexif.load, piexif.dump, piexif.insert
    with (
        patch("piexif.load", return_value=fake_raw) as mock_load,
        patch("piexif.dump", return_value=b"bytes") as mock_dump,
        patch("piexif.insert") as mock_insert,
    ):
        tags = backend.load_tags(fake_path)
        # Should decode ASCII bytes
        assert tags[(271, "IFD0")].value == "Canon"
        # Should keep non-ASCII as is
        assert tags[(33434, "Exif")].value == 123.0
        # Now test save_tags
        tags_list = [tags[(271, "IFD0")], tags[(33434, "Exif")]]
        # ExifTagDict is iterable over keys, not values, so we need to pass the dict
        backend.save_tags(fake_path, tags)
        mock_dump.assert_called()
        mock_insert.assert_called_with(b"bytes", fake_path)
