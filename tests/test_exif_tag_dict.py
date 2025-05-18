import pytest
from tagkit.tag_io.base import ExifTagDict
from tagkit.exif_entry import ExifEntry


def test_exif_tagdict_update_notimplemented():
    d = ExifTagDict()
    # Should not raise with no arguments
    d.update()
    # Should not raise with a dict as the only argument
    d2 = ExifTagDict()
    d2[(271, "IFD0")] = ExifEntry(271, "Canon", "IFD0")
    d.update(d2)
    # Should raise NotImplementedError with kwargs
    with pytest.raises(NotImplementedError):
        d.update({}, foo=1)
    # Should raise NotImplementedError with more than one positional argument
    with pytest.raises(NotImplementedError):
        d.update({}, {})


def test_tuple_key_set_and_get():
    d = ExifTagDict()
    entry = ExifEntry(271, "Canon", "IFD0")
    d[(271, "IFD0")] = entry
    assert d[(271, "IFD0")] is entry


def test_int_key_get_unique():
    d = ExifTagDict()
    entry = ExifEntry(271, "Canon", "IFD0")
    d[(271, "IFD0")] = entry
    assert d[271] is entry


def test_int_key_get_ambiguous():
    d = ExifTagDict()
    d[(271, "IFD0")] = ExifEntry(271, "Canon", "IFD0")
    d[(271, "Exif")] = ExifEntry(271, "Canon", "Exif")
    with pytest.raises(KeyError):
        _ = d[271]


def test_int_key_get_not_found():
    d = ExifTagDict()
    with pytest.raises(KeyError):
        _ = d[999]


def test_setitem_invalid_key_type():
    d = ExifTagDict()
    with pytest.raises(TypeError):
        d[271] = ExifEntry(271, "Canon", "IFD0")  # type: ignore
    with pytest.raises(TypeError):
        d[(271, 123)] = ExifEntry(271, "Canon", "IFD0")  # type: ignore
    with pytest.raises(TypeError):
        d[(271, "IFD0", "extra")] = ExifEntry(271, "Canon", "IFD0")  # type: ignore


def test_setitem_invalid_value_type():
    d = ExifTagDict()
    with pytest.raises(TypeError):
        d[(271, "IFD0")] = "not an ExifEntry"  # type: ignore
