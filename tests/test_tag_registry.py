import pytest
from pathlib import Path

from tagkit.tag_registry import _ExifRegistry, tag_registry
from tagkit.exceptions import InvalidTagId, InvalidTagName
from tagkit.types import ExifType


@pytest.fixture
def sample_registry_conf():
    return {
        "Image": {
            271: {"name": "Make", "type": "ASCII"},
            272: {"name": "Model", "type": "ASCII"},
        },
        "Exif": {
            33434: {"name": "ExposureTime", "type": "RATIONAL"},
            34850: {"name": "ExposureProgram", "type": "SHORT"},
        },
        "GPS": {
            1: {"name": "GPSLatitudeRef", "type": "ASCII"},
            2: {"name": "GPSLatitude", "type": "RATIONAL"},
        },
        "Interop": {
            1: {"name": "InteropIndex", "type": "ASCII"},
        },
    }


@pytest.fixture
def registry(sample_registry_conf):
    return _ExifRegistry(sample_registry_conf)


def test_init(registry, sample_registry_conf):
    """Test registry initialization"""
    assert registry.tags == sample_registry_conf
    assert len(registry._name_to_id) == 7  # Total unique tag names
    assert len(registry._tag_ids) == 6  # Total unique tag IDs


def test_from_yaml():
    """Test loading registry from default YAML file"""
    registry = _ExifRegistry.from_yaml()
    assert len(registry.tags) > 0
    assert all(key in registry.tags for key in ["Image", "Exif", "GPS", "Interop"])


def test_from_yaml_custom_path(tmp_path):
    """Test loading registry from custom YAML file"""
    yaml_content = """
    Image:
      271:
        name: Make
        type: ASCII
    """
    yaml_path = tmp_path / "test_registry.yaml"
    yaml_path.write_text(yaml_content)
    registry = _ExifRegistry.from_yaml(yaml_path)
    assert len(registry.tags) == 1
    assert registry.tags["Image"][271]["name"] == "Make"


def test_tag_names(registry):
    """Test getting list of tag names"""
    names = registry.tag_names
    assert len(names) == 7
    assert "Make" in names
    assert "Model" in names


def test_get_ifd_by_id(registry):
    """Test getting IFD by tag ID"""
    assert registry.get_ifd(271) == "IFD0"  # Image tag -> IFD0
    assert registry.get_ifd(33434) == "Exif"  # Exif tag -> Exif
    assert registry.get_ifd(1, thumbnail=True) == "IFD1"  # Any tag with thumbnail=True -> IFD1


def test_get_ifd_by_name(registry):
    """Test getting IFD by tag name"""
    assert registry.get_ifd("Make") == "IFD0"
    assert registry.get_ifd("ExposureTime") == "Exif"
    assert registry.get_ifd("Make", thumbnail=True) == "IFD1"


def test_get_ifd_invalid_tag():
    """Test getting IFD with invalid tag"""
    with pytest.raises(InvalidTagId):
        tag_registry.get_ifd(99999)


def test_get_tag_id_by_id(registry):
    """Test getting tag ID when input is already an ID"""
    assert registry.get_tag_id(271) == 271
    assert registry.get_tag_id(33434) == 33434


def test_get_tag_id_by_name(registry):
    """Test getting tag ID from tag name"""
    assert registry.get_tag_id("Make") == 271
    assert registry.get_tag_id("ExposureTime") == 33434


def test_get_tag_id_invalid_id(registry):
    """Test getting tag ID with invalid ID"""
    with pytest.raises(InvalidTagId):
        registry.get_tag_id(99999)


def test_get_tag_id_invalid_name(registry):
    """Test getting tag ID with invalid name"""
    with pytest.raises(InvalidTagName):
        registry.get_tag_id("NonExistentTag")


def test_get_tag_name_by_name(registry):
    """Test getting tag name when input is already a name"""
    assert registry.get_tag_name("Make") == "Make"
    assert registry.get_tag_name("ExposureTime") == "ExposureTime"


def test_get_tag_name_by_id(registry):
    """Test getting tag name from ID"""
    assert registry.get_tag_name(271) == "Make"
    assert registry.get_tag_name(33434) == "ExposureTime"


def test_get_tag_name_by_id_with_ifd(registry):
    """Test getting tag name from ID with specific IFD"""
    assert registry.get_tag_name(271, ifd="IFD0") == "Make"
    assert registry.get_tag_name(33434, ifd="Exif") == "ExposureTime"


def test_get_tag_name_invalid_id(registry):
    """Test getting tag name with invalid ID"""
    with pytest.raises(InvalidTagId):
        registry.get_tag_name(99999)


def test_get_tag_name_invalid_name(registry):
    """Test getting tag name with invalid name"""
    with pytest.raises(InvalidTagName):
        registry.get_tag_name("NonExistentTag")


def test_get_exif_type_by_id(registry):
    """Test getting EXIF type by tag ID"""
    assert registry.get_exif_type(271) == "ASCII"
    assert registry.get_exif_type(33434) == "RATIONAL"
    assert registry.get_exif_type(34850) == "SHORT"


def test_get_exif_type_by_name(registry):
    """Test getting EXIF type by tag name"""
    assert registry.get_exif_type("Make") == "ASCII"
    assert registry.get_exif_type("ExposureTime") == "RATIONAL"
    assert registry.get_exif_type("ExposureProgram") == "SHORT"


def test_get_exif_type_invalid_id(registry):
    """Test getting EXIF type with invalid ID"""
    with pytest.raises(InvalidTagId):
        registry.get_exif_type(99999)


def test_get_exif_type_invalid_name(registry):
    """Test getting EXIF type with invalid name"""
    with pytest.raises(InvalidTagName):
        registry.get_exif_type("NonExistentTag") 