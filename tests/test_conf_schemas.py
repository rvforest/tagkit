import json
from pathlib import Path

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
    registry_path = Path(__file__).parents[1] / "src" / "tagkit" / "conf" / "registry.yaml"
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
