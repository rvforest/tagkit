import json
from pathlib import Path
from typing import Any, overload

import pytest

from tagkit.image_exif import ImageExifData

# Change to use the fixture instead of a hardcoded path
@pytest.fixture
def img_metadata():
    """Get the metadata from the metadata.json file"""
    here = Path(__file__).parent.resolve()
    metadata_path = here / "test_images/metadata.json"
    
    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)


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


def test_initialize_from_str(test_images, img_metadata):
    str_path = str(test_images / next(iter(img_metadata)))
    ImageExifData(str_path)


def test_initialize_from_path(test_images, img_metadata):
    pathlib_path = test_images / next(iter(img_metadata))
    ImageExifData(pathlib_path)


def test_get_tags_no_filter(test_images, img_metadata):
    """Test getting tags without filter for all test images"""
    for filename, expected in img_metadata.items():
        # Skip corrupt images or entries without tags
        if not expected.get("tags") or expected.get("corrupt", False):
            continue
            
        path = test_images / filename
        exif_handler = ImageExifData(path)
        actual_tags = exif_handler.get_tags()

        expected_tags = list_to_tuple(expected["tags"])
        for expected_tag in expected_tags:
            actual_val = actual_tags[expected_tag["id"]].value
            assert actual_val == expected_tag["value"], f"Failed for {filename}, tag {expected_tag['name']}"
