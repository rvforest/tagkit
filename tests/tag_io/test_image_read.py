import json
from pathlib import Path
from typing import Any, overload

import pytest

from tagkit import ExifImage


@overload
def list_to_tuple(obj: dict[str, Any]) -> dict[str, Any]: ...
@overload
def list_to_tuple(obj: list) -> tuple: ...


def list_to_tuple(obj):
    if isinstance(obj, list):
        return tuple(list_to_tuple(item) for item in obj)
    elif isinstance(obj, dict):
        return {k: list_to_tuple(v) for k, v in obj.items()}
    return obj


def test_initialize_from_str(test_images: Path):
    path = test_images / "minimal.jpg"
    ExifImage(str(path))


def test_initialize_from_path(test_images: Path):
    pathlib_path = test_images / "minimal.jpg"
    ExifImage(pathlib_path)


def test_get_tags_no_filter(test_images: Path):
    """Test getting tags without filter for all test images"""
    here = Path(__file__).parents[1].resolve()
    metadata_path = here / "conf/test-img-metadata.json"

    with open(metadata_path, "r", encoding="utf-8") as f:
        img_metadata = json.load(f)

    for filename, expected in img_metadata.items():
        # Skip corrupt images or entries without tags
        if not expected.get("tags") or expected.get("corrupt", False):
            continue

        path = test_images / filename
        exif_handler = ExifImage(path)
        actual_tags = exif_handler.tags

        expected_tags = list_to_tuple(expected["tags"])
        for expected_tag in expected_tags:
            actual_val = actual_tags[expected_tag["name"]].value
            assert actual_val == expected_tag["value"], (
                f"Failed for {filename}, tag {expected_tag['name']}"
            )
