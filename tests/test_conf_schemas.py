import json
from pathlib import Path

import jsonschema


HERE = Path(__file__).parent
SCHEMA_PATH = HERE / "conf" / "img-metadata.schema.json"
CONFIG_FILES = [
    HERE / "conf" / "test-img-metadata.json",
    HERE / "conf" / "doctest-img-metadata.json",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_image_metadata_configs_against_schema():
    schema = load(SCHEMA_PATH)
    resolver = jsonschema.RefResolver(base_uri=f"file://{SCHEMA_PATH}", referrer=schema)
    validator = jsonschema.Draft7Validator(schema, resolver=resolver)
    for cfg in CONFIG_FILES:
        data = load(cfg)
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        assert not errors, "Schema validation errors: " + "; ".join(
            [str(e) for e in errors]
        )
