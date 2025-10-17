from datetime import datetime, timedelta
import shutil
from typing import Callable, Union

import pytest
from pathlib import Path

from tagkit import ExifImage
from tagkit.core.tag import ExifTag
from tagkit.core.exceptions import (
    DateTimeError,
    InvalidTagId,
    InvalidTagName,
    TagNotFound,
)
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
        "Copyright": "2025 John",  # Changed from bytes to str (ASCII type)
    }
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    exif.write_tags(tags)
    assert exif.tags["Artist"].value == "Jane Doe"
    assert exif.tags["Copyright"].value == "2025 John"


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


class TestGetDatetime:
    """Tests for ExifImage.get_datetime() method."""

    def test_get_all_datetimes_single_tag(self, test_images):
        """Test getting all datetimes when only one is present."""
        image_path = test_images / "datetime_software.jpg"
        exif = ExifImage(image_path)
        datetimes = exif.get_all_datetimes()
        assert len(datetimes) == 1
        assert "DateTimeOriginal" in datetimes
        assert datetimes["DateTimeOriginal"] == datetime(2025, 5, 1, 14, 30, 0)

    def test_get_all_datetimes_multiple_tags(self, test_images):
        """Test getting all datetimes when multiple are present."""
        image_path = test_images / "datetime_software.jpg"
        # First set all datetime tags
        new_dt = datetime(2025, 6, 15, 10, 30, 0)

        exif = ExifImage(image_path)
        exif.set_datetime(new_dt)
        exif.save()

        exif_verify = ExifImage(image_path)
        datetimes = exif_verify.get_all_datetimes()
        assert len(datetimes) == 3
        assert datetimes["DateTime"] == new_dt
        assert datetimes["DateTimeOriginal"] == new_dt
        assert datetimes["DateTimeDigitized"] == new_dt

    def test_get_all_datetimes_no_tags(self, test_images):
        """Test getting all datetimes when none are present."""
        image_path = test_images / "minimal.jpg"
        exif = ExifImage(image_path)
        datetimes = exif.get_all_datetimes()
        assert len(datetimes) == 0

    def test_get_datetime_specific_tag(self, test_images):
        """Test getting a specific datetime tag."""
        image_path = test_images / "datetime_software.jpg"
        exif = ExifImage(image_path)
        dt = exif.get_datetime(tag="DateTimeOriginal")
        assert dt == datetime(2025, 5, 1, 14, 30, 0)

    def test_get_datetime_missing_tag(self, test_images):
        """Test getting a nonexistent datetime tag returns None."""
        image_path = test_images / "datetime_software.jpg"
        exif = ExifImage(image_path)
        with pytest.raises(TagNotFound):
            exif.get_datetime(tag="DateTime")

    def test_get_datetime_invalid_tag_name(self, test_images):
        """Test getting a datetime from an invalid tag name"""
        image_path = test_images / "datetime_software.jpg"
        exif = ExifImage(image_path)
        with pytest.raises(InvalidTagName):
            exif.get_datetime(tag="InvalidTag")

    def test_get_datetime_from_non_datetime_tag(self, test_images):
        """Test getting a datetime from a tag that isn't a datetime"""
        image_path = test_images / "minimal.jpg"
        exif = ExifImage(image_path)
        with pytest.raises(DateTimeError):
            exif.get_datetime(tag="Make")


class TestSetDatetime:
    """Tests for ExifImage.set_datetime() method."""

    def test_set_datetime_update_all(self, test_images):
        """Test setting datetime with tags=None (updates all)."""
        image_path = test_images / "minimal.jpg"
        new_dt = datetime(2025, 6, 15, 10, 30, 0)

        exif = ExifImage(image_path)
        exif.set_datetime(new_dt, tags=None)
        datetimes = exif.get_all_datetimes()
        assert datetimes["DateTime"] == new_dt
        assert datetimes["DateTimeOriginal"] == new_dt
        assert datetimes["DateTimeDigitized"] == new_dt

    def test_set_datetime_single_new_tag(self, test_images):
        """Test setting datetime with single tag that doesn't already exist."""
        image_path = test_images / "minimal.jpg"
        new_dt = datetime(2025, 6, 15, 10, 30, 0)

        exif = ExifImage(image_path)
        exif.set_datetime(new_dt, tags=["DateTime"])

        datetimes = exif.get_all_datetimes()
        assert datetimes["DateTime"] == new_dt
        assert len(datetimes) == 1

    def test_set_datetime_single_existing_tag(self, test_images):
        """Test setting datetime with single tag that already exists."""
        image_path = test_images / "datetime_software.jpg"
        new_dt = datetime(2025, 6, 15, 10, 30, 0)

        exif = ExifImage(image_path)
        exif.set_datetime(new_dt, tags=["DateTimeOriginal"])

        datetimes = exif.get_all_datetimes()
        assert datetimes["DateTimeOriginal"] == new_dt
        assert len(datetimes) == 1

    def test_set_datetime_invalid_tag(self, test_images):
        """Test setting datetime with an invalid tag raises error."""
        image_path = test_images / "datetime_software.jpg"
        new_dt = datetime(2025, 6, 15, 10, 30, 0)

        exif = ExifImage(image_path)
        with pytest.raises(InvalidTagName):
            exif.set_datetime(new_dt, tags=["InvalidTag"])

    def test_set_datetime_non_datetime_tag(self, test_images):
        """Test setting datetime on a non-datetime tag raises error."""
        image_path = test_images / "datetime_software.jpg"
        new_dt = datetime(2025, 6, 15, 10, 30, 0)

        exif = ExifImage(image_path)
        with pytest.raises(Exception):
            exif.set_datetime(new_dt, tags=["Flash"])
            exif.save()


class TestOffsetDatetime:
    """Tests for ExifImage.offset_datetime() method."""

    def test_offset_datetime_positive(self, test_images):
        """Test offsetting datetime by a positive timedelta."""
        image_path = test_images / "datetime_software.jpg"

        exif = ExifImage(image_path)
        original_dt = exif.get_datetime()
        assert original_dt is not None

        delta = timedelta(hours=2, minutes=30)
        exif.offset_datetime(delta)

        new_dt = exif.get_datetime()
        assert new_dt == original_dt + delta

    def test_offset_datetime_negative(self, test_images):
        """Test offsetting datetime by a negative timedelta."""
        image_path = test_images / "datetime_software.jpg"

        exif = ExifImage(image_path)
        original_dt = exif.get_datetime()

        delta = timedelta(days=-1, hours=-3)
        exif.offset_datetime(delta)

        new_dt = exif.get_datetime()
        assert new_dt == original_dt + delta

    def test_offset_datetime_all_tags(self, test_images):
        """Test offsetting all datetime tags."""
        image_path = test_images / "minimal.jpg"
        base_dt = datetime(2025, 6, 15, 10, 0, 0)

        exif = ExifImage(image_path)
        exif.set_datetime(base_dt)

        delta = timedelta(hours=5)
        exif.offset_datetime(delta)

        # Verify all datetime tags are offset
        datetimes = exif.get_all_datetimes()
        expected_dt = base_dt + delta
        assert datetimes["DateTime"] == expected_dt
        assert datetimes["DateTimeOriginal"] == expected_dt
        assert datetimes["DateTimeDigitized"] == expected_dt

    def test_offset_datetime_specific_tags(self, test_images):
        """Test offsetting only specific datetime tags."""
        image_path = test_images / "minimal.jpg"
        base_dt = datetime(2025, 6, 15, 10, 0, 0)

        # Set all tags first
        exif = ExifImage(image_path)
        exif.set_datetime(base_dt)

        # Offset only DateTimeOriginal
        delta = timedelta(hours=3)
        exif.offset_datetime(delta, tags=["DateTimeOriginal"])

        # Verify only DateTimeOriginal was offset
        datetimes = exif.get_all_datetimes()
        assert datetimes["DateTimeOriginal"] == base_dt + delta
        assert datetimes["DateTime"] == base_dt
        assert datetimes["DateTimeDigitized"] == base_dt

    def test_offset_datetime_invalid_tag(self, test_images):
        """Test offsetting datetime with an invalid tag raises error."""
        image_path = test_images / "minimal.jpg"
        base_dt = datetime(2025, 6, 15, 10, 0, 0)

        exif = ExifImage(image_path)
        exif.set_datetime(base_dt)

        delta = timedelta(hours=2)
        with pytest.raises(InvalidTagName):
            exif.offset_datetime(delta, tags=["InvalidTag"])

    def test_offset_datetime_non_datetime_tag(self, test_images):
        """Test offsetting datetime on a non-datetime tag raises error."""
        image_path = test_images / "minimal.jpg"
        base_dt = datetime(2025, 6, 15, 10, 0, 0)

        exif = ExifImage(image_path)
        exif.set_datetime(base_dt)

        delta = timedelta(hours=2)
        with pytest.raises(Exception):
            exif.offset_datetime(delta, tags=["Make"])

    def test_offset_datetime_no_tags(self, test_images):
        """Test offsetting datetime when no datetime tags exist raises error."""
        image_path = test_images / "minimal.jpg"

        exif = ExifImage(image_path)
        # Ensure no datetime tags exist
        datetimes = exif.get_all_datetimes()
        assert len(datetimes) == 0

        delta = timedelta(hours=2)
        with pytest.raises(TagNotFound):
            exif.offset_datetime(delta)


class TestDatetimePrecedence:
    """Tests for datetime tag precedence logic in ExifImage.get_datetime()."""

    def test_precedence_datetime_original_first(self, test_images):
        """Test that DateTimeOriginal is preferred over other tags."""
        image_path = test_images / "minimal.jpg"

        # Set all three datetime tags with different values
        exif = ExifImage(image_path)
        exif.set_datetime(datetime(2025, 6, 20, 10, 0, 0), tags=["DateTime"])
        exif.set_datetime(datetime(2025, 6, 10, 10, 0, 0), tags=["DateTimeOriginal"])
        exif.set_datetime(datetime(2025, 6, 15, 10, 0, 0), tags=["DateTimeDigitized"])

        # get_datetime should return DateTimeOriginal
        dt = exif.get_datetime()
        assert dt == datetime(2025, 6, 10, 10, 0, 0)

    def test_precedence_datetime_digitized_second(self, test_images):
        """Test that DateTimeDigitized is preferred when DateTimeOriginal is missing."""
        image_path = test_images / "minimal.jpg"

        # Set DateTime and DateTimeDigitized but not DateTimeOriginal
        exif = ExifImage(image_path)
        exif.set_datetime(datetime(2025, 6, 20, 10, 0, 0), tags=["DateTime"])
        exif.set_datetime(datetime(2025, 6, 15, 10, 0, 0), tags=["DateTimeDigitized"])
        exif.save()

        # get_datetime should return DateTimeDigitized
        exif_verify = ExifImage(image_path)
        dt = exif_verify.get_datetime()
        assert dt == datetime(2025, 6, 15, 10, 0, 0)

    def test_precedence_datetime_last(self, test_images):
        """Test that DateTime is used as fallback."""
        image_path = test_images / "minimal.jpg"

        # Set only DateTime
        exif = ExifImage(image_path)
        exif.set_datetime(datetime(2025, 6, 20, 10, 0, 0), tags=["DateTime"])
        exif.save()

        # get_datetime should return DateTime
        exif_verify = ExifImage(image_path)
        dt = exif_verify.get_datetime()
        assert dt == datetime(2025, 6, 20, 10, 0, 0)


# Tests for read_tag and read_tags methods
@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tag_by_name(test_images, file_type):
    """Test reading a tag by name"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    value = exif.read_tag("Make")
    assert value == "TestMake"


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tag_by_id(test_images, file_type):
    """Test reading a tag by ID"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    value = exif.read_tag(271)  # Make tag
    assert value == "TestMake"


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tag_with_ifd(test_images, file_type):
    """Test reading a tag with explicit IFD"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    value = exif.read_tag(271, ifd="IFD0")
    assert value == "TestMake"


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tag_formatted(test_images, file_type):
    """Test reading a tag with formatting enabled (default)"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    value = exif.read_tag("Make", format_value=True)
    assert isinstance(value, str)
    assert value == "TestMake"


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tag_raw(test_images, file_type):
    """Test reading a tag with formatting disabled"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    value = exif.read_tag("Make", format_value=False)
    assert value == "TestMake"


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tag_missing_raises(test_images, file_type):
    """Test reading a missing tag raises KeyError by default"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    with pytest.raises(TagNotFound, match="Tag 'Artist' not found in image"):
        exif.read_tag("Artist")


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tag_invalid_tag_raises(test_images, file_type):
    """Test reading an invalid tag raises exception"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    with pytest.raises(InvalidTagName):
        exif.read_tag("NonExistentTag")


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tag_invalid_id_raises(test_images, file_type):
    """Test reading an invalid tag ID raises exception"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    with pytest.raises(InvalidTagId):
        exif.read_tag(99999)


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tags_multiple(test_images, file_type):
    """Test reading multiple tags at once"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    result = exif.read_tags(["Make", "Model"])
    assert "Make" in result
    assert "Model" in result
    assert result["Make"] == "TestMake"
    assert result["Model"] == "TestModel"


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tags_formatted(test_images, file_type):
    """Test reading multiple tags with formatting enabled (default)"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    result = exif.read_tags(["Make", "Model"], format_value=True)
    assert all(isinstance(v, str) for v in result.values())


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tags_raw(test_images, file_type):
    """Test reading multiple tags with formatting disabled"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    result = exif.read_tags(["Make", "Model"], format_value=False)
    assert "Make" in result
    assert "Model" in result


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tags_with_missing_skip(test_images, file_type):
    """Test reading multiple tags where some are missing and skip_missing is True"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    result = exif.read_tags(["Make", "Artist"], skip_missing=True)
    # Only Make should be in result (Artist doesn't exist)
    assert "Make" in result
    assert "Artist" not in result


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tags_empty_list(test_images, file_type):
    """Test reading with an empty list returns empty dict"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    result = exif.read_tags([])
    assert result == {}


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tags_with_invalid_tag(test_images, file_type):
    """Test reading multiple tags with one invalid tag raises InvalidTagName"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    with pytest.raises(InvalidTagName):
        exif.read_tags(["Make", "NonExistentTag"])


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tags_with_missing_tag(test_images, file_type):
    """Test reading multiple tags with one missing tag raises KeyError by default"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    with pytest.raises(TagNotFound, match="Tag 'DateTime' not found in image"):
        exif.read_tags(["Make", "DateTime"], skip_missing=False)


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tags_with_missing_tag_skip(test_images, file_type):
    """Test reading multiple tags with one missing tag skips the missing tag"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    result = exif.read_tags(["Make", "DateTime"], skip_missing=True)
    # Only Make should be in result
    assert "Make" in result
    assert "DateTime" not in result


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tags_by_id(test_images, file_type):
    """Test reading multiple tags by ID"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    result = exif.read_tags([271, 272])  # Make, Model
    assert "Make" in result
    assert "Model" in result


@pytest.mark.parametrize("file_type", [str, Path])
def test_read_tags_with_ifd(test_images, file_type):
    """Test reading multiple tags with explicit IFD"""
    file_path = file_type(test_images / "minimal.jpg")
    exif = ExifImage(file_path)
    result = exif.read_tags(["Make", "Model"], ifd="IFD0")
    assert "Make" in result
    assert "Model" in result


def test_read_tag_invalid_binary_entry(test_images):
    """Test that providing an invalid binary_format raises ValueError"""
    exif = ExifImage(test_images / "minimal.jpg")
    with pytest.raises(ValueError):
        exif.read_tag("Make", binary_format="invalid_format")


def test_read_tags_invalid_binary_entry(test_images):
    """Test that providing an invalid binary_format raises ValueError"""
    exif = ExifImage(test_images / "minimal.jpg")
    with pytest.raises(ValueError):
        exif.read_tags(["Make", "Model"], binary_format="invalid_format")
