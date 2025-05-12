import pytest

from tagkit.image_exif import ImageExifData
from tagkit.exif_entry import ExifEntry
from tagkit.exceptions import InvalidTagId, InvalidTagName

def test_init_with_backup(test_images):
    """Test initialization with backup enabled"""
    exif = ImageExifData(test_images / "minimal.jpg", create_backup_on_mod=True)
    assert exif.create_backup is True

def test_get_tag_by_id(test_images):
    """Test getting a tag by its ID"""
    exif = ImageExifData(test_images / "minimal.jpg")
    tag = exif.get_tag(271)  # Make tag
    assert isinstance(tag, ExifEntry)
    assert tag.value == "TestMake"

def test_get_tag_by_name(test_images):
    """Test getting a tag by its name"""
    exif = ImageExifData(test_images / "minimal.jpg")
    tag = exif.get_tag("Make")
    assert isinstance(tag, ExifEntry)
    assert tag.value == "TestMake"

def test_get_tag_with_ifd(test_images):
    """Test getting a tag with explicit IFD"""
    exif = ImageExifData(test_images / "minimal.jpg")
    tag = exif.get_tag(271, ifd="IFD0")
    assert isinstance(tag, ExifEntry)
    assert tag.value == "TestMake"

def test_get_tag_with_thumbnail(test_images):
    """Test getting a tag with thumbnail flag"""
    exif = ImageExifData(test_images / "minimal.jpg")
    exif.set_tag(271, "foo", thumbnail=True)
    tag = exif.get_tag(271, thumbnail=True)
    assert isinstance(tag, ExifEntry)
    assert tag.value == "foo"

def test_get_tag_invalid_id(test_images):
    """Test getting a tag with invalid ID"""
    exif = ImageExifData(test_images / "minimal.jpg")
    with pytest.raises(InvalidTagId):
        exif.get_tag(99999)

def test_get_tag_invalid_name(test_images):
    """Test getting a tag with invalid name"""
    exif = ImageExifData(test_images / "minimal.jpg")
    with pytest.raises(InvalidTagName):
        exif.get_tag("NonExistentTag")

def test_get_tags_no_filter(test_images):
    """Test getting all tags without filter"""
    exif = ImageExifData(test_images / "minimal.jpg")
    tags = exif.get_tags()
    assert len(tags) > 0
    assert all(isinstance(tag, ExifEntry) for tag in tags.values())

def test_get_tags_with_filter(test_images):
    """Test getting tags with ID filter"""
    exif = ImageExifData(test_images / "minimal.jpg")
    tags = exif.get_tags(tag_filter=[271])  # Make tag
    assert len(tags) == 1
    assert 271 in tags
    assert tags[271].value == "TestMake"

def test_get_tags_with_name_filter(test_images):
    """Test getting tags with name filter"""
    exif = ImageExifData(test_images / "minimal.jpg")
    tags = exif.get_tags(tag_filter=["Make"])
    assert len(tags) == 1
    assert 271 in tags
    assert tags[271].value == "TestMake"

def test_get_tags_with_thumbnail(test_images):
    """Test getting tags with thumbnail flag"""
    exif = ImageExifData(test_images / "minimal.jpg")
    tags = exif.get_tags(thumbnail=True)
    # All returned tags should be from IFD0
    assert all(tag.ifd == "IFD0" for tag in tags.values())

def test_set_tag_by_id(test_images):
    """Test setting a tag by ID"""
    exif = ImageExifData(test_images / "minimal.jpg")
    exif.set_tag(271, "NewMake")
    tag = exif.get_tag(271)
    assert tag.value == "NewMake"

def test_set_tag_by_name(test_images):
    """Test setting a tag by name"""
    exif = ImageExifData(test_images / "minimal.jpg")
    exif.set_tag("Make", "NewMake")
    tag = exif.get_tag("Make")
    assert tag.value == "NewMake"

def test_set_tag_with_backup(test_images):
    """Test setting a tag with backup enabled"""
    test_file = test_images / "minimal.jpg"
    exif = ImageExifData(test_file, create_backup_on_mod=True)
    exif.set_tag(271, "NewMake")
    assert (test_file.parent / (test_file.name + ".bak")).exists()

def test_set_tag_with_ifd(test_images):
    """Test setting a tag with explicit IFD"""
    exif = ImageExifData(test_images / "minimal.jpg")
    exif.set_tag(271, "NewMake", ifd="IFD0")
    tag = exif.get_tag(271)
    assert tag.value == "NewMake"

def test_set_tag_with_thumbnail(test_images):
    """Test setting a tag with thumbnail flag"""
    exif = ImageExifData(test_images / "minimal.jpg")
    exif.set_tag(271, "NewMake", thumbnail=True)
    tag = exif.get_tag(271, thumbnail=True)
    assert tag.value == "NewMake"

def test_remove_tag_by_id(test_images):
    """Test removing a tag by ID"""
    exif = ImageExifData(test_images / "minimal.jpg")
    exif.remove_tag(271)
    with pytest.raises(KeyError):
        exif.get_tag(271)

def test_remove_tag_by_name(test_images):
    """Test removing a tag by name"""
    exif = ImageExifData(test_images / "minimal.jpg")
    exif.remove_tag("Make")
    with pytest.raises(KeyError):
        exif.get_tag("Make")

def test_remove_tag_with_backup(test_images):
    """Test removing a tag with backup enabled"""
    test_file = test_images / "minimal.jpg"
    exif = ImageExifData(test_file, create_backup_on_mod=True)
    exif.remove_tag(271)
    assert (test_file.parent / (test_file.name + ".bak")).exists()

def test_remove_tag_with_ifd(test_images):
    """Test removing a tag with explicit IFD"""
    exif = ImageExifData(test_images / "minimal.jpg")
    exif.remove_tag(271, ifd="IFD0")
    with pytest.raises(KeyError):
        exif.get_tag(271)

def test_remove_tag_with_thumbnail(test_images):
    """Test removing a tag with thumbnail flag"""
    exif = ImageExifData(test_images / "minimal.jpg")
    exif.set_tag(271, "NewMake", thumbnail=True)
    exif.remove_tag(271, thumbnail=True)
    with pytest.raises(KeyError):
        exif.get_tag(271, thumbnail=True)

def test_remove_nonexistent_tag(test_images):
    """Test removing a tag that doesn't exist"""
    exif = ImageExifData(test_images / "minimal.jpg")
    with pytest.raises(InvalidTagId):
        exif.remove_tag(99999) 