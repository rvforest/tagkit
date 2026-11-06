"""Test fixtures for tagkit.

This file contains fixtures that are used by tests.
Doctest-specific fixtures are in the root conftest.py.
"""

import json
import os
from pathlib import Path
from typing import Any

import piexif
import pytest


def _format_tag_value(value, tag_id):
    """Format the tag value based on tag ID"""
    # GPS coordinate values need special handling
    if tag_id in (2, 4):  # GPSLatitude or GPSLongitude
        return tuple(tuple(coord) for coord in value)
    # String values should be bytes
    elif isinstance(value, str):
        return value.encode("utf-8")
    # Return as is for other types
    return value


def create_test_images_from_metadata(img_dir: Path, metadata_path: str | Path) -> None:
    """Create test images from a metadata file

    Args:
        img_dir: Path to the directory where images will be created
        metadata_path: Path to the metadata JSON file
    """
    # Create directory for images
    os.makedirs(img_dir, exist_ok=True)

    # Read the metadata file
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    base_image = (Path(__file__).parent / "conf/base.jpg").read_bytes()

    # Create images based on metadata
    for filename, img_data in metadata.items():
        # Skip corrupt image, it will be handled separately
        if filename == "corrupt.jpg" and img_data.get("corrupt", False):
            continue

        # Initialize exif_dict with empty IFDs
        exif_dict: dict[str, Any] = {
            "0th": {},
            "Exif": {},
            "GPS": {},
            "1st": {},
            "thumbnail": None,
        }

        # Add tags to appropriate IFDs
        for tag_info in img_data.get("tags", []):
            tag_id = tag_info["id"]
            tag_value = tag_info["value"]

            # IFD must be explicitly specified in metadata
            if "ifd" not in tag_info:
                raise ValueError(
                    f"IFD not specified for tag {tag_info['name']} in {filename}"
                )

            ifd_name = tag_info["ifd"]

            # Format the value based on tag type
            formatted_value = _format_tag_value(tag_value, tag_id)

            # Add to exif_dict
            exif_dict[ifd_name][tag_id] = formatted_value

        # Create and save the image
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, base_image, str(img_dir / filename))

    # Create a corrupt image if specified in metadata
    if "corrupt.jpg" in metadata and metadata["corrupt.jpg"].get("corrupt", False):
        # Insert a deliberately invalid APP1 payload after the JPEG SOI marker.
        payload = b"garbage_exif_data"
        app1 = b"\xff\xe1" + (len(payload) + 2).to_bytes(2, "big") + payload
        (img_dir / "corrupt.jpg").write_bytes(base_image[:2] + app1 + base_image[2:])


@pytest.fixture
def test_images(tmp_path: Path) -> Path:
    """Create test images in a temporary directory based on metadata.json"""
    here = Path(__file__).parent.resolve()
    metadata_path = here / "conf/test-img-metadata.json"

    # Create images from metadata
    img_dir = tmp_path / "test_images"
    create_test_images_from_metadata(img_dir, metadata_path)
    return img_dir
