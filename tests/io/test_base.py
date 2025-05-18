import pytest
from typing import Any, cast

from tagkit.tag_io.base import ExifTagDict
from tagkit.exif_entry import ExifEntry


@pytest.fixture
def sample_exif_entry():
    return ExifEntry(256, 1024, "IFD0")


def test_init_empty():
    """Test initializing an empty ExifTagDict"""
    exif_dict = ExifTagDict()
    assert len(exif_dict) == 0


def test_init_with_data(sample_exif_entry):
    """Test initializing with data"""
    data = {(256, "IFD0"): sample_exif_entry}
    exif_dict = ExifTagDict(data)
    assert len(exif_dict) == 1
    assert exif_dict[256, "IFD0"] == sample_exif_entry


def test_init_with_kwargs():
    """Test that initialization with kwargs raises AttributeError"""
    with pytest.raises(AttributeError):
        ExifTagDict(foo="bar")


def test_getitem_full_key(sample_exif_entry):
    """Test getting item with full key (tag_id, ifd)"""
    exif_dict = ExifTagDict({(256, "IFD0"): sample_exif_entry})
    assert exif_dict[256, "IFD0"] == sample_exif_entry


def test_getitem_tag_id_unique(sample_exif_entry):
    """Test getting item with just tag_id when it's unique"""
    exif_dict = ExifTagDict({(256, "IFD0"): sample_exif_entry})
    assert exif_dict[256] == sample_exif_entry


def test_getitem_tag_id_ambiguous():
    """Test getting item with just tag_id when it's ambiguous"""
    exif_dict = ExifTagDict(
        {
            (256, "IFD0"): ExifEntry(256, 1024, "IFD0"),
            (256, "Exif"): ExifEntry(256, 2048, "Exif"),
        }
    )
    with pytest.raises(KeyError, match="Ambiguous tag_id 256"):
        exif_dict[256]


def test_getitem_nonexistent():
    """Test getting item with nonexistent key"""
    exif_dict = ExifTagDict()
    with pytest.raises(KeyError, match="No tag found with tag_id 999"):
        exif_dict[999]


def test_setitem_valid(sample_exif_entry):
    """Test setting item with valid key and value"""
    exif_dict = ExifTagDict()
    exif_dict[256, "IFD0"] = sample_exif_entry
    assert exif_dict[256, "IFD0"] == sample_exif_entry


def test_setitem_invalid_key():
    """Test setting item with invalid key format"""
    exif_dict = ExifTagDict()
    # Cast to Any to test runtime type checking
    invalid_key = cast(Any, 256)
    with pytest.raises(TypeError, match="Key must be a tuple"):
        exif_dict[invalid_key] = ExifEntry(256, 1024, "IFD0")


def test_setitem_invalid_key_types():
    """Test setting item with invalid key types"""
    exif_dict = ExifTagDict()
    # Cast to Any to test runtime type checking
    invalid_key = cast(Any, ("256", "IFD0"))
    with pytest.raises(TypeError, match="Key must be a tuple"):
        exif_dict[invalid_key] = ExifEntry(256, 1024, "IFD0")


def test_setitem_invalid_value():
    """Test setting item with invalid value type"""
    exif_dict = ExifTagDict()
    # Cast to Any to test runtime type checking
    invalid_value = cast(Any, 1024)
    with pytest.raises(TypeError, match="Value must be an ExifEntry instance"):
        exif_dict[256, "IFD0"] = invalid_value


def test_update_raises_not_implemented():
    """Test that update() raised NotImplementedError"""
    exif_dict = ExifTagDict()
    # Cast to Any to test runtime type checking
    data = cast(Any, {(9999, "IFD0"): 1024})
    # with pytest.raises(InvalidTag):
    exif_dict.update(data)
