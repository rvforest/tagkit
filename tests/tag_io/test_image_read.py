import json
from pathlib import Path
from typing import Any

from tagkit import ExifImage
from tagkit.conf.models import ImageMetadataConfig

from tests.helpers import fixture_ifd


def list_to_tuple(obj: Any) -> Any:
    if isinstance(obj, list):
        return tuple(list_to_tuple(item) for item in obj)
    if isinstance(obj, dict):
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
        img_metadata = ImageMetadataConfig.model_validate(json.load(f))

    for filename, expected in img_metadata.root.items():
        # Skip corrupt images or entries without tags
        if not expected.tags or expected.corrupt:
            continue

        path = test_images / filename
        exif_handler = ExifImage(path)
        for expected_tag in expected.tags:
            actual_val = exif_handler.read_tag(
                expected_tag.id, ifd=fixture_ifd(expected_tag.ifd)
            )
            assert actual_val == list_to_tuple(expected_tag.value), (
                f"Failed for {filename}, tag {expected_tag.name}"
            )
