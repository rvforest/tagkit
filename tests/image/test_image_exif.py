import shutil
from typing import Callable, Union

import pytest
from pathlib import Path

from tagkit import ExifImage
from tagkit.core.tag import ExifTag
from tagkit.core.exceptions import InvalidTagId, InvalidTagName
from tagkit.core.types import TagValue


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
    """Test removing a tag that exists in registry but not in the image does not raise."""
    exif = ExifImage(test_images / "minimal.jpg")
    # Artist tag (315) is a valid tag but doesn't exist in the minimal.jpg test image
    exif.delete_tag("Artist")  # Should not raise
    assert "Artist" not in exif.tags


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


@pytest.mark.parametrize("file_type", [str, Path])
def test_write_tags_multiple_tags(test_images, file_type: Callable):
    """Test writing multiple tags at once with both str and Path file_path types."""
    tags: dict[Union[str, int], TagValue] = {
        "Artist": "Jane Doe",
        "Copyright": b"2025 John",
    }
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    exif.write_tags(tags)
    assert exif.tags["Artist"].value == "Jane Doe"
    assert exif.tags["Copyright"].value == b"2025 John"


@pytest.mark.parametrize("file_type", [str, Path])
def test_write_tags_empty_dict(test_images, file_type):
    """Test writing with an empty dict does nothing and does not error (str/Path)"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    exif.write_tags({})
    # Should not raise, tags remain unchanged
    assert "Make" in exif.tags


@pytest.mark.parametrize("file_type", [str, Path])
def test_write_tags_invalid_tag(test_images, file_type):
    """Test writing with an invalid tag raises ValueError (str/Path)"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    with pytest.raises(Exception):
        exif.write_tags({"NonExistentTag": "foo"})


@pytest.mark.parametrize("file_type", [str, Path])
def test_delete_tags_multiple_tags(test_images, file_type):
    """Test deleting multiple tags at once (str/Path)"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    exif.write_tags({"Artist": "Jane Doe", "Copyright": "2025 John"})
    exif.delete_tags(["Artist", "Copyright"])
    assert "Artist" not in exif.tags
    assert "Copyright" not in exif.tags


@pytest.mark.parametrize("file_type", [str, Path])
def test_delete_tags_empty_list(test_images, file_type):
    """Test deleting with an empty list does nothing and does not error (str/Path)"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    exif.delete_tags([])
    # Should not raise, tags remain unchanged
    assert "Make" in exif.tags


@pytest.mark.parametrize("file_type", [str, Path])
def test_delete_tags_partial_missing(test_images, file_type):
    """Test deleting tags where some do not exist raises InvalidTagName for unknown tag name (str/Path)"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    exif.write_tag("Artist", "Jane Doe")
    with pytest.raises(InvalidTagName):
        exif.delete_tags(["Artist", "NonExistentTag"])


class TestExifImageIntegration:
    def test_write_tag_and_persist(self, test_images, tmp_path):
        """Integration: write_tag persists value after save and reload."""
        src = test_images / "minimal.jpg"
        dst = tmp_path / "minimal.jpg"
        shutil.copy(src, dst)
        exif = ExifImage(dst)
        exif.write_tag("Make", "IntegrationTest")
        exif.save()

        # Reload and check
        reloaded = ExifImage(dst)
        assert reloaded.tags["Make"].value == "IntegrationTest"

    def test_delete_tag_and_persist(self, test_images, tmp_path):
        """Integration: delete_tag removes value after save and reload."""
        src = test_images / "minimal.jpg"
        dst = tmp_path / "minimal.jpg"
        shutil.copy(src, dst)
        exif = ExifImage(dst)
        # Ensure tag exists
        assert "Make" in exif.tags
        exif.delete_tag("Make")
        exif.save()
        # Reload and check
        reloaded = ExifImage(dst)
        assert "Make" not in reloaded.tags

    def test_write_tag_creates_backup(self, test_images, tmp_path):
        """Integration: save(create_backup=True) creates a backup file after write_tag."""
        import shutil

        src = test_images / "minimal.jpg"
        dst = tmp_path / "minimal.jpg"
        shutil.copy(src, dst)
        exif = ExifImage(dst)
        exif.write_tag("Make", "BackupTest")
        exif.save(create_backup=True)
        backup = dst.parent / (dst.name + ".bak")
        assert backup.exists()
        # The backup should not have the new value
        exif_bak = ExifImage(backup)
        assert exif_bak.tags["Make"].value != "BackupTest"

    def test_delete_tag_creates_backup(self, test_images, tmp_path):
        """Integration: save(create_backup=True) creates a backup file after delete_tag."""
        import shutil

        src = test_images / "minimal.jpg"
        dst = tmp_path / "minimal.jpg"
        shutil.copy(src, dst)
        exif = ExifImage(dst)
        exif.delete_tag("Make")
        exif.save(create_backup=True)
        backup = dst.parent / (dst.name + ".bak")
        assert backup.exists()
        # The backup should still have the tag
        exif_bak = ExifImage(backup)
        assert "Make" in exif_bak.tags

    def test_write_tags_and_persist(self, test_images: Path, tmp_path):
        """Integration: write_tags persists values after save and reload."""
        from typing import Union
        from tagkit.core.types import TagValue

        src = test_images / "minimal.jpg"
        dst = tmp_path / "minimal.jpg"
        shutil.copy(src, dst)
        tags: dict[Union[str, int], TagValue] = {
            "Artist": "Jane Doe",
            "Copyright": "2025 John",
        }
        exif = ExifImage(dst)
        exif.write_tags(tags)
        exif.save()
        reloaded = ExifImage(dst)
        assert reloaded.tags["Artist"].value == "Jane Doe"
        assert reloaded.tags["Copyright"].value == "2025 John"

    def test_delete_tags_and_persist(self, test_images, tmp_path):
        """Integration: delete_tags removes values after save and reload."""
        src = test_images / "minimal.jpg"
        dst = tmp_path / "minimal.jpg"
        shutil.copy(src, dst)
        exif = ExifImage(dst)
        exif.write_tags({"Artist": "Jane Doe", "Copyright": "2025 John"})
        exif.save()
        exif.delete_tags(["Artist", "Copyright"])
        exif.save()
        reloaded = ExifImage(dst)
        assert "Artist" not in reloaded.tags
        assert "Copyright" not in reloaded.tags
