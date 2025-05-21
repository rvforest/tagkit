# Basic Reading Example

This example demonstrates how to read EXIF metadata from image files using tagkit.

## Reading All Tags

The simplest way to read all EXIF tags from an image:

```python
from tagkit.image_exif import ImageExifData

# Create an instance for an image
exif = ImageExifData("path/to/your/image.jpg")

# Get all tags
tags = exif.get_tags()

# Print all tags
for tag_id, tag in tags.items():
    print(f"{tag.name}: {tag.value}")
```

## Reading Specific Tags

If you're only interested in certain tags, you can get them directly:

```python
from tagkit.image_exif import ImageExifData

# Create an instance for an image
exif = ImageExifData("path/to/your/image.jpg")

# Get specific tags with error handling
try:
    # Extract camera information
    camera_make = exif.get_tag("Make").value
    camera_model = exif.get_tag("Model").value
    print(f"Camera: {camera_make} {camera_model}")
    
    # Extract photo information
    date_taken = exif.get_tag("DateTimeOriginal").value
    exposure = exif.get_tag("ExposureTime").value
    aperture = exif.get_tag("FNumber").value
    iso = exif.get_tag("ISOSpeedRatings").value
    
    print(f"Date Taken: {date_taken}")
    print(f"Exposure: {exposure} sec, f/{aperture}, ISO {iso}")
except KeyError as e:
    print(f"Tag not found: {e}")
```

## Filtering Tags

```python
from tagkit.image_exif import ImageExifData

# Create an instance
exif_data = ImageExifData("path/to/your/image.jpg")

# Get all tags
all_tags = exif_data.get_tags()

# Get a specific tag
artist = exif_data.get_tag("Artist")
print(f"Artist: {artist}")

# Check if a tag exists
if exif_data.has_tag("Copyright"):
    print(f"Copyright: {exif_data.get_tag('Copyright')}")
else:
    print("No copyright information found")

# Get tags by category
gps_tags = exif_data.get_tags_by_category("GPS")
for tag_name, tag_value in gps_tags.items():
    print(f"{tag_name}: {tag_value}")
```

## Error Handling

It's good practice to include error handling when reading EXIF data:

```python
from tagkit.image_exif import read_exif
from tagkit.exceptions import TagkitError

try:
    tags = read_exif("path/to/your/image.jpg")
    # Process tags
except FileNotFoundError:
    print("Error: Image file not found")
except TagkitError as e:
    print(f"Error reading EXIF data: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Reading from Multiple Images

To read EXIF data from multiple images:

```python
import os
from tagkit.image_exif import read_exif

def process_directory(directory):
    results = {}
    
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.jpg', '.jpeg', '.tiff', '.png')):
            file_path = os.path.join(directory, filename)
            try:
                tags = read_exif(file_path)
                results[filename] = tags
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    return results

# Process all images in a directory
image_metadata = process_directory("path/to/your/images/")

# Print camera models used
for filename, tags in image_metadata.items():
    camera = tags.get("Model", "Unknown")
    print(f"{filename}: {camera}")
```

## Next Steps

Now that you've learned how to read EXIF data, check out:

- [Basic Writing Example](basic_writing.md) to learn how to write EXIF data
- [Batch Processing Example](batch_processing.md) for handling multiple files efficiently
