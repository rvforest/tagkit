import pytest

from tagkit import ExifImage
from tagkit.core.tag import ExifTag
from tagkit.core.exceptions import InvalidTagId, InvalidTagName


def test_tags_property_access(test_images):
    """Test accessing tags through the property"""
    exif = ExifImage(test_images / "minimal.jpg")
    tags = exif.tags
    assert len(tags) > 0
    assert all(isinstance(tag, ExifTag) for tag in tags.values())
    assert "Make" in tags
    assert tags["Make"].value == "TestMake"


def test_tags_property_with_filter(test_images):
    """Test tags property with tag filter"""
    exif = ExifImage(test_images / "minimal.jpg", tag_filter=["Make"])
    tags = exif.tags
    assert len(tags) == 1
    assert "Make" in tags
    assert tags["Make"].value == "TestMake"


def test_tags_property_with_ifd(test_images):
    """Test tags property with IFD filter"""
    exif = ExifImage(test_images / "minimal.jpg", ifd="IFD0")
    tags = exif.tags
    # All returned tags should be from IFD0
    assert all(tag.ifd == "IFD0" for tag in tags.values())


def test_tags_property_with_thumbnail(test_images):
    """Test tags property with thumbnail flag"""
    exif = ExifImage(test_images / "minimal.jpg", thumbnail=True)
    # This test assumes there are thumbnail tags in the test image
    # If not, we should at least verify the property returns a dict
    assert isinstance(exif.tags, dict)


def test_len_method(test_images):
    """Test the __len__ method"""
    exif = ExifImage(test_images / "minimal.jpg")
    assert len(exif) == len(exif.tags)

    # With filter
    filtered_exif = ExifImage(test_images / "minimal.jpg", tag_filter=["Make"])
    assert len(filtered_exif) == 1


def test_set_tag_by_id(test_images):
    """Test setting a tag by ID"""
    exif = ExifImage(test_images / "minimal.jpg")
    exif.write_tag(271, "NewMake")
    assert exif.tags["Make"].value == "NewMake"


def test_set_tag_by_name(test_images):
    """Test setting a tag by name"""
    exif = ExifImage(test_images / "minimal.jpg")
    exif.write_tag("Make", "NewMake")
    assert exif.tags["Make"].value == "NewMake"


def test_set_tag_with_ifd(test_images):
    """Test setting a tag with explicit IFD"""
    exif = ExifImage(test_images / "minimal.jpg")
    exif.write_tag(271, "NewMake", ifd="IFD0")
    assert exif.tags["Make"].value == "NewMake"


def test_remove_tag_by_id(test_images):
    """Test removing a tag by ID"""
    exif = ExifImage(test_images / "minimal.jpg")
    # Verify tag exists first
    assert "Make" in exif.tags
    # Remove it
    exif.delete_tag(271)
    # Verify it's gone
    assert "Make" not in exif.tags


def test_remove_tag_by_name(test_images):
    """Test removing a tag by name"""
    exif = ExifImage(test_images / "minimal.jpg")
    # Verify tag exists first
    assert "Make" in exif.tags
    # Remove it
    exif.delete_tag("Make")
    # Verify it's gone
    assert "Make" not in exif.tags


def test_remove_tag_with_ifd(test_images):
    """Test removing a tag with explicit IFD"""
    exif = ExifImage(test_images / "minimal.jpg")
    # Verify tag exists first
    assert "Make" in exif.tags
    # Remove it with explicit IFD
    exif.delete_tag(271, ifd="IFD0")
    # Verify it's gone
    assert "Make" not in exif.tags


def test_remove_nonexistent_tag(test_images):
    """Test removing a tag that doesn't exist in the registry"""
    exif = ExifImage(test_images / "minimal.jpg")
    with pytest.raises(InvalidTagId):
        exif.delete_tag(99999)


def test_remove_missing_tag(test_images):
    """Test removing a tag that exists in registry but not in the image"""
    exif = ExifImage(test_images / "minimal.jpg")
    # Artist tag (315) is a valid tag but doesn't exist in the minimal.jpg test image
    with pytest.raises(KeyError, match="Tag 'Artist' not found"):
        exif.delete_tag("Artist")


def test_as_dict_method(test_images):
    """Test the as_dict method"""
    exif = ExifImage(test_images / "minimal.jpg")
    dict_data = exif.as_dict()
    assert isinstance(dict_data, dict)
    # The result should contain tag names as keys
    assert any(isinstance(key, str) for key in dict_data.keys())
    # Each tag should be represented as a dict
    assert all(isinstance(value, dict) for value in dict_data.values())


def test_as_dict_with_binary_format(test_images):
    """Test the as_dict method with binary format option"""
    exif = ExifImage(test_images / "minimal.jpg")
    dict_data = exif.as_dict(binary_format="hex")
    assert isinstance(dict_data, dict)


def test_save_creates_backup(test_images, tmp_path):
    """Test that save(create_backup=True) creates a backup file."""
    import shutil

    test_file = tmp_path / "minimal.jpg"
    # Copy the test image to a temp location to avoid modifying the original
    shutil.copy(test_images / "minimal.jpg", test_file)
    exif = ExifImage(test_file)
    exif.write_tag("Make", "BackupTest")
    exif.save(create_backup=True)
    assert (test_file.parent / (test_file.name + ".bak")).exists()
