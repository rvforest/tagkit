"""
Tests for validating configuration file schemas.

This module validates that all YAML configuration files used by tagkit
adhere to their expected schemas, ensuring:
- registry.yaml: Contains valid EXIF tag definitions
- formatting.yaml: Contains valid formatting rules
- Test image metadata files: Match expected structure

Schema validation catches:
- Missing required keys
- Invalid data types
- Unexpected additional properties
- Malformed structures
"""

import json
from pathlib import Path

import jsonschema
import yaml


HERE = Path(__file__).parent
SRC_CONF = Path(__file__).parents[1] / "src" / "tagkit" / "conf"

# Image metadata test configs
IMG_METADATA_SCHEMA = HERE / "conf" / "img-metadata.schema.json"
IMG_METADATA_CONFIGS = [
    HERE / "conf" / "test-img-metadata.json",
    HERE / "conf" / "doctest-img-metadata.json",
]

# Main configuration files
REGISTRY_SCHEMA = SRC_CONF / "registry.schema.json"
REGISTRY_CONFIG = SRC_CONF / "registry.yaml"
FORMATTING_SCHEMA = SRC_CONF / "formatting.schema.json"
FORMATTING_CONFIG = SRC_CONF / "formatting.yaml"


def load_json(path: Path):
    """Load a JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path):
    """Load a YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def convert_int_keys_to_str(data):
    """
    Recursively convert integer keys to strings in dictionaries.
    
    YAML safe_load converts numeric keys to integers, but JSON Schema
    patternProperties only works with string keys.
    
    Args:
        data: Dictionary or other data structure
        
    Returns:
        Data with integer keys converted to strings
    """
    if isinstance(data, dict):
        return {
            str(k) if isinstance(k, int) else k: convert_int_keys_to_str(v)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [convert_int_keys_to_str(item) for item in data]
    else:
        return data


def validate_against_schema(data, schema_path: Path):
    """
    Validate data against a JSON schema.

    Args:
        data: Data to validate
        schema_path: Path to the JSON schema file

    Returns:
        List of validation errors (empty if valid)
    """
    # Convert integer keys to strings for JSON Schema validation
    data = convert_int_keys_to_str(data)
    
    schema = load_json(schema_path)
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{schema_path}", referrer=schema
    )
    validator = jsonschema.Draft7Validator(schema, resolver=resolver)
    return sorted(validator.iter_errors(data), key=lambda e: e.path)


def test_image_metadata_configs_against_schema():
    """Test that image metadata test configs match their schema."""
    for cfg in IMG_METADATA_CONFIGS:
        data = load_json(cfg)
        errors = validate_against_schema(data, IMG_METADATA_SCHEMA)
        assert not errors, f"{cfg.name} schema validation errors: " + "; ".join(
            [str(e) for e in errors]
        )


def test_registry_config_against_schema():
    """
    Test that registry.yaml matches its schema.

    Validates:
    - All four IFD sections (Image, Exif, GPS, Interop) are present
    - Each tag entry has required 'name' and 'type' fields
    - Tag IDs are integers
    - Types are from the allowed enum
    """
    data = load_yaml(REGISTRY_CONFIG)
    errors = validate_against_schema(data, REGISTRY_SCHEMA)
    assert not errors, "registry.yaml schema validation errors: " + "; ".join(
        [str(e) for e in errors]
    )


def test_formatting_config_against_schema():
    """
    Test that formatting.yaml matches its schema.

    Validates:
    - Each tag has a 'display' format specified
    - Display format is from allowed enum
    - Optional fields (unit, show_plus, mapping) have correct types
    - Tags with 'map' display have a 'mapping' object
    """
    data = load_yaml(FORMATTING_CONFIG)
    errors = validate_against_schema(data, FORMATTING_SCHEMA)
    assert not errors, "formatting.yaml schema validation errors: " + "; ".join(
        [str(e) for e in errors]
    )


# ============================================================================
# Negative Tests - Invalid Configurations
# ============================================================================


def test_registry_missing_required_ifd():
    """Test that registry with missing required IFD section fails validation."""
    invalid_data = {
        "Image": {11: {"name": "ProcessingSoftware", "type": "ASCII"}},
        "Exif": {33434: {"name": "ExposureTime", "type": "RATIONAL"}},
        "GPS": {1: {"name": "GPSLatitudeRef", "type": "ASCII"}},
        # Missing "Interop" - should fail
    }
    errors = validate_against_schema(invalid_data, REGISTRY_SCHEMA)
    assert errors, "Expected validation error for missing required IFD section"
    assert any("'Interop' is a required property" in str(e) for e in errors)


def test_registry_invalid_tag_type():
    """Test that registry with invalid tag type fails validation."""
    invalid_data = {
        "Image": {271: {"name": "Make", "type": "INVALID_TYPE"}},
        "Exif": {33434: {"name": "ExposureTime", "type": "RATIONAL"}},
        "GPS": {1: {"name": "GPSLatitudeRef", "type": "ASCII"}},
        "Interop": {1: {"name": "InteroperabilityIndex", "type": "ASCII"}},
    }
    errors = validate_against_schema(invalid_data, REGISTRY_SCHEMA)
    assert errors, "Expected validation error for invalid tag type"
    assert any("'INVALID_TYPE' is not one of" in str(e) for e in errors)


def test_registry_missing_tag_name():
    """Test that registry with missing tag name fails validation."""
    invalid_data = {
        "Image": {271: {"type": "ASCII"}},  # Missing "name"
        "Exif": {33434: {"name": "ExposureTime", "type": "RATIONAL"}},
        "GPS": {1: {"name": "GPSLatitudeRef", "type": "ASCII"}},
        "Interop": {1: {"name": "InteroperabilityIndex", "type": "ASCII"}},
    }
    errors = validate_against_schema(invalid_data, REGISTRY_SCHEMA)
    assert errors, "Expected validation error for missing tag name"
    assert any("'name' is a required property" in str(e) for e in errors)


def test_registry_additional_properties():
    """Test that registry with unexpected properties fails validation."""
    invalid_data = {
        "Image": {
            271: {"name": "Make", "type": "ASCII", "extra_field": "not_allowed"}
        },
        "Exif": {33434: {"name": "ExposureTime", "type": "RATIONAL"}},
        "GPS": {1: {"name": "GPSLatitudeRef", "type": "ASCII"}},
        "Interop": {1: {"name": "InteroperabilityIndex", "type": "ASCII"}},
    }
    errors = validate_against_schema(invalid_data, REGISTRY_SCHEMA)
    assert errors, "Expected validation error for additional properties"
    assert any("Additional properties are not allowed" in str(e) for e in errors)


def test_formatting_missing_display():
    """Test that formatting config with missing display field fails validation."""
    invalid_data = {
        "ExposureTime": {"unit": "s"}  # Missing required "display" field
    }
    errors = validate_against_schema(invalid_data, FORMATTING_SCHEMA)
    assert errors, "Expected validation error for missing display field"
    assert any("'display' is a required property" in str(e) for e in errors)


def test_formatting_invalid_display_type():
    """Test that formatting config with invalid display type fails validation."""
    invalid_data = {"ExposureTime": {"display": "invalid_display_type", "unit": "s"}}
    errors = validate_against_schema(invalid_data, FORMATTING_SCHEMA)
    assert errors, "Expected validation error for invalid display type"
    assert any("'invalid_display_type' is not one of" in str(e) for e in errors)


def test_formatting_map_without_mapping():
    """Test that formatting with 'map' display but no mapping fails validation."""
    invalid_data = {"Orientation": {"display": "map"}}  # Missing required "mapping"
    errors = validate_against_schema(invalid_data, FORMATTING_SCHEMA)
    assert errors, "Expected validation error for map display without mapping"
    assert any("'mapping' is a required property" in str(e) for e in errors)


def test_formatting_invalid_mapping_key():
    """Test that formatting with invalid mapping key fails validation."""
    invalid_data = {
        "Orientation": {
            "display": "map",
            "mapping": {
                "1": "Top-left",
                "invalid_key_123": "Invalid",  # Keys should be single digit or letter
            },
        }
    }
    errors = validate_against_schema(invalid_data, FORMATTING_SCHEMA)
    assert errors, "Expected validation error for invalid mapping key"
    assert any(
        "does not match any of the regexes" in str(e)
        or "do not match any of the regexes" in str(e)
        or "Additional properties" in str(e)
        for e in errors
    )


def test_formatting_wrong_type_for_unit():
    """Test that formatting with wrong type for unit fails validation."""
    invalid_data = {
        "ExposureTime": {"display": "fraction", "unit": 123}  # unit should be string
    }
    errors = validate_against_schema(invalid_data, FORMATTING_SCHEMA)
    assert errors, "Expected validation error for wrong unit type"
    assert any("123 is not of type 'string'" in str(e) for e in errors)
