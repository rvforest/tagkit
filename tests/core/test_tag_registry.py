import pytest
from pathlib import Path
from tagkit.core.registry import ExifRegistry, tag_registry
from tagkit.core.exceptions import AmbiguousTagKey, InvalidTagId, InvalidTagName
from tagkit.core.types import ExifType


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
    return ExifRegistry(sample_registry_conf)


def test_init(registry, sample_registry_conf):
    """Test registry initialization"""
    assert registry.tags_by_namespace == sample_registry_conf
    assert len(registry.tag_names) == 7  # Total unique tag names


def test_from_yaml():
    """Test loading registry from default YAML file"""
    registry = ExifRegistry.from_yaml()
    assert len(registry.tags_by_namespace) > 0
    assert all(
        key in registry.tags_by_namespace for key in ["Image", "Exif", "GPS", "Interop"]
    )


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
    registry = ExifRegistry.from_yaml(yaml_path)
    assert len(registry.tags_by_namespace) == 1
    assert registry.tags_by_namespace["Image"][271]["name"] == "Make"


def test_tag_names(registry):
    """Test getting list of tag names"""
    names = registry.tag_names
    assert len(names) == 7
    assert "Make" in names
    assert "Model" in names


def test_get_ifd_by_id(registry):
    """Test getting IFD by tag ID"""
    assert registry.get_ifd(271) == "IFD0"
    assert registry.get_ifd(33434) == "Exif"  # Exif tag -> Exif
    with pytest.raises(InvalidTagId):
        registry.get_ifd(1, thumbnail=True)


def test_get_ifd_by_name(registry):
    """Test getting IFD by tag name"""
    assert registry.get_ifd("Make") == "IFD0"
    assert registry.get_ifd("ExposureTime") == "Exif"
    assert registry.get_ifd("Make", thumbnail=True) == "IFD1"


def test_get_ifd_invalid_tag():
    """Test getting IFD with invalid tag"""
    with pytest.raises(InvalidTagId):
        tag_registry.get_ifd(99999)


def test_resolve_tag_id_by_id(registry):
    """Test getting tag ID when input is already an ID"""
    assert registry.resolve_tag_id(271) == 271
    assert registry.resolve_tag_id(33434) == 33434


def test_resolve_tag_id_by_name(registry):
    """Test getting tag ID from tag name"""
    assert registry.resolve_tag_id("Make") == 271
    assert registry.resolve_tag_id("ExposureTime") == 33434


def test_resolve_tag_id_invalid_id(registry):
    """Test getting tag ID with invalid ID"""
    with pytest.raises(InvalidTagId):
        registry.resolve_tag_id(99999)


def test_resolve_tag_id_invalid_name(registry):
    """Test getting tag ID with invalid name"""
    with pytest.raises(InvalidTagName):
        registry.resolve_tag_id("NonExistentTag")


def test_resolve_tag_name_by_name(registry):
    """Test getting tag name when input is already a name"""
    assert registry.resolve_tag_name("Make") == "Make"
    assert registry.resolve_tag_name("ExposureTime") == "ExposureTime"


def test_resolve_tag_name_by_id(registry):
    """Test getting tag name from ID"""
    assert registry.resolve_tag_name(271) == "Make"
    assert registry.resolve_tag_name(33434) == "ExposureTime"


def test_resolve_tag_name_by_id_with_ifd(registry):
    """Test getting tag name from ID with specific IFD"""
    assert registry.resolve_tag_name(271, ifd="IFD0") == "Make"
    assert registry.resolve_tag_name(33434, ifd="Exif") == "ExposureTime"


def test_resolve_tag_name_invalid_id(registry):
    """Test getting tag name with invalid ID"""
    with pytest.raises(InvalidTagId):
        registry.resolve_tag_name(99999)


def test_resolve_tag_name_invalid_name(registry):
    """Test getting tag name with invalid name"""
    with pytest.raises(InvalidTagName):
        registry.resolve_tag_name("NonExistentTag")


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


def test_get_ifd_warns_on_multiple_ifds():
    conf = {
        "Image": {123: {"name": "TestTag", "type": "ASCII"}},
        "Exif": {123: {"name": "TestTag", "type": "ASCII"}},
    }  # type: ignore
    reg = ExifRegistry(conf)  # type: ignore
    with pytest.raises(AmbiguousTagKey, match="Provide an explicit ifd"):
        reg.get_ifd(123)


def test_get_definition_by_ambiguous_id_requires_ifd(registry):
    with pytest.raises(AmbiguousTagKey):
        registry.get_definition(1)
    definition = registry.get_definition(1, ifd="GPS")
    assert definition.name == "GPSLatitudeRef"
    assert definition.namespace == "GPS"
    assert definition.allowed_ifds == ("GPS",)


@pytest.mark.parametrize("tag_key", [256, "ImageWidth"])
def test_ifd1_shares_ifd0_definitions(tag_key):
    registry = ExifRegistry(
        {"Image": {256: {"name": "ImageWidth", "type": ["SHORT", "LONG"], "count": 1}}}
    )
    main = registry.get_definition(tag_key)
    thumbnail = registry.get_definition(tag_key, ifd="IFD1")

    assert thumbnail is main
    assert main.namespace == "Image"
    assert main.allowed_ifds == ("IFD0", "IFD1")
    assert registry.resolve_tag(tag_key).ifd == "IFD0"
    assert registry.resolve_tag(tag_key, ifd="IFD1").ifd == "IFD1"
    assert registry.resolve_tag(tag_key, ifd="IFD1").definition is main
    assert thumbnail.tag_id == main.tag_id == 256
    assert thumbnail.name == main.name == "ImageWidth"
    assert thumbnail.allowed_types == main.allowed_types == ("SHORT", "LONG")
    assert thumbnail.count == main.count == 1
    assert registry.get_definition(tag_key, ifd="IFD0") == main
    assert registry.resolve_tag_id(tag_key, ifd="IFD1") == 256
    assert registry.resolve_tag_name(tag_key, ifd="IFD1") == "ImageWidth"


@pytest.mark.parametrize(
    "tag_key, error", [(33434, InvalidTagId), ("ExposureTime", InvalidTagName)]
)
def test_ifd1_does_not_use_exif_definitions(registry, tag_key, error):
    with pytest.raises(error):
        registry.get_definition(tag_key, ifd="IFD1")


@pytest.mark.parametrize(
    "tag_key", [513, "JPEGInterchangeFormat", 514, "JPEGInterchangeFormatLength"]
)
def test_thumbnail_location_tags_have_no_primary_placement(tag_key):
    resolved = tag_registry.resolve_tag(tag_key)
    assert resolved.ifd == "IFD1"
    assert resolved.definition.namespace == "Image"
    assert resolved.definition.allowed_ifds == ("IFD1",)
    assert tag_registry.get_ifd(tag_key) == "IFD1"
    with pytest.raises((InvalidTagId, InvalidTagName)):
        tag_registry.resolve_tag(tag_key, ifd="IFD0")


@pytest.mark.parametrize("tag_key", ["ExposureTime", "GPSLatitude", "InteropIndex"])
def test_thumbnail_selection_rejects_other_namespaces(registry, tag_key):
    with pytest.raises(InvalidTagName):
        registry.get_ifd(tag_key, thumbnail=True)


def test_default_policy_does_not_change_definition_identity():
    conf = {
        "Image": {274: {"name": "Orientation", "type": "SHORT", "default_ifd": "IFD1"}}
    }
    registry = ExifRegistry(conf)
    assert registry.resolve_tag("Orientation").ifd == "IFD1"
    assert registry.resolve_tag("Orientation", ifd="IFD0").ifd == "IFD0"
    assert registry.get_definition("Orientation") is registry.get_definition(
        "Orientation", ifd="IFD1"
    )


def test_explicit_directory_disambiguates_shared_name_and_id():
    registry = ExifRegistry(
        {
            "Image": {123: {"name": "TestTag", "type": "SHORT"}},
            "Exif": {123: {"name": "TestTag", "type": "LONG"}},
        }
    )
    for key in (123, "TestTag"):
        with pytest.raises(AmbiguousTagKey):
            registry.resolve_tag(key)
        assert registry.resolve_tag(key, ifd="IFD1").definition.namespace == "Image"
        assert registry.resolve_tag(key, ifd="Exif").definition.namespace == "Exif"
