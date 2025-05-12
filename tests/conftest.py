import json
import os
from pathlib import Path
import piexif
from PIL import Image
import pytest


def _format_tag_value(value, tag_id):
    """Format the tag value based on tag ID"""
    # GPS coordinate values need special handling
    if tag_id in (2, 4):  # GPSLatitude or GPSLongitude
        return tuple(tuple(coord) for coord in value)
    # String values should be bytes
    elif isinstance(value, str):
        return value.encode('utf-8')
    # Return as is for other types
    return value


@pytest.fixture
def test_images(tmp_path):
    """Create test images in a temporary directory based on metadata.json"""
    # Path to the metadata.json file
    here = Path(__file__).parent.resolve()
    metadata_path = here / "io/test_images/metadata.json"
    
    # Read the metadata.json file
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    # Create directory for images
    image_dir = tmp_path / "test_images"
    os.makedirs(image_dir, exist_ok=True)
    
    # Create images based on metadata
    for filename, img_data in metadata.items():
        # Skip corrupt image, it will be handled separately
        if filename == "corrupt.jpg" and img_data.get("corrupt", False):
            continue
            
        # Initialize exif_dict with empty IFDs
        exif_dict = {
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
                raise ValueError(f"IFD not specified for tag {tag_info['name']} in {filename}")
            
            ifd_name = tag_info["ifd"]
            
            # Format the value based on tag type
            formatted_value = _format_tag_value(tag_value, tag_id)
            
            # Add to exif_dict
            exif_dict[ifd_name][tag_id] = formatted_value
        
        # Create and save the image
        img = Image.new("RGB", (100, 100), color="white")
        exif_bytes = piexif.dump(exif_dict)
        img_path = image_dir / filename
        img.save(img_path, "jpeg", exif=exif_bytes)

    # Create a corrupt image if specified in metadata
    if "corrupt.jpg" in metadata and metadata["corrupt.jpg"].get("corrupt", False):
        img = Image.new("RGB", (100, 100), color="white")
        img_path = image_dir / "corrupt.jpg"
        img.save(img_path, "jpeg", exif=b"garbage_exif_data")
    
    # Return the directory containing the images
    return image_dir
