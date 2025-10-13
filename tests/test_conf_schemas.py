import json
from pathlib import Path

import pytest
from pydantic import ValidationError
import yaml

from tagkit.conf.models import (
    FormattingConfig,
    ImageMetadataConfig,
    RegistryConfig,
)


HERE = Path(__file__).parent
CONFIG_FILES = [
    HERE / "conf" / "test-img-metadata.json",
    HERE / "conf" / "doctest-img-metadata.json",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_image_metadata_configs_against_schema():
    """Validate image metadata configs using Pydantic models."""
    for cfg in CONFIG_FILES:
        data = load_json(cfg)
        # This will raise ValidationError if the data is invalid
        ImageMetadataConfig.model_validate(data)


def test_registry_yaml_config():
    """Validate registry.yaml using Pydantic models."""
    registry_path = (
        Path(__file__).parents[1] / "src" / "tagkit" / "conf" / "registry.yaml"
    )
    data = load_yaml(registry_path)
    # This will raise ValidationError if the data is invalid
    RegistryConfig.model_validate(data)


def test_formatting_yaml_config():
    """Validate formatting.yaml using Pydantic models."""
    formatting_path = (
        Path(__file__).parents[1] / "src" / "tagkit" / "conf" / "formatting.yaml"
    )
    data = load_yaml(formatting_path)
    # This will raise ValidationError if the data is invalid
    FormattingConfig.model_validate(data)


# Negative test cases for malformed configs


def test_image_metadata_invalid_filename():
    """Test that invalid filenames are rejected."""
    invalid_data = {
        "not_a_jpg_file.txt": {
            "tags": [{"id": 271, "name": "Make", "value": "Test", "ifd": "0th"}]
        }
    }
    with pytest.raises(ValidationError, match="must end with .jpg or .jpeg"):
        ImageMetadataConfig.model_validate(invalid_data)


def test_image_metadata_missing_required_field():
    """Test that missing required fields are rejected."""
    invalid_data = {
        "test.jpg": {
            "tags": [
                {"id": 271, "name": "Make", "ifd": "0th"}  # missing 'value'
            ]
        }
    }
    with pytest.raises(ValidationError, match="Field required"):
        ImageMetadataConfig.model_validate(invalid_data)


def test_image_metadata_invalid_ifd():
    """Test that invalid IFD values are rejected."""
    invalid_data = {
        "test.jpg": {
            "tags": [{"id": 271, "name": "Make", "value": "Test", "ifd": "InvalidIFD"}]
        }
    }
    with pytest.raises(ValidationError):
        ImageMetadataConfig.model_validate(invalid_data)


def test_registry_invalid_type():
    """Test that invalid EXIF types are rejected."""
    invalid_data = {
        "Image": {
            271: {
                "name": "Make",
                "type": "INVALID_TYPE",  # Not a valid ExifType
            }
        }
    }
    with pytest.raises(ValidationError):
        RegistryConfig.model_validate(invalid_data)


def test_registry_missing_name():
    """Test that missing tag name is rejected."""
    invalid_data = {
        "Image": {
            271: {
                "type": "ASCII"  # missing 'name'
            }
        }
    }
    with pytest.raises(ValidationError, match="Field required"):
        RegistryConfig.model_validate(invalid_data)


def test_formatting_extra_field():
    """Test that extra fields in formatting config are rejected."""
    invalid_data = {
        "ExposureTime": {
            "display": "fraction",
            "unit": "s",
            "extra_field": "not_allowed",  # Extra field not in schema
        }
    }
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        FormattingConfig.model_validate(invalid_data)
