# Quickstart Guide

This guide will help you get up and running with tagkit quickly.

## Basic Usage

### Reading EXIF Tags

```python
from tagkit.image.exif import ExifImage

# Create an instance for an image
exif = ExifImage("path/to/your/image.jpg")

# Read all EXIF tags
tags = exif.tags
for tag_id, tag in tags.items():
    print(f"{tag.name}: {tag.value}")

# Read specific tags
make = exif.get_tag("Make")
date_taken = exif.get_tag("DateTimeOriginal")
print(f"Photo taken with {make.value} on {date_taken.value}")
```

### Modifying EXIF Tags

```python
from tagkit.image.exif import ExifImage

# Create an instance for an image
exif = ExifImage("path/to/your/image.jpg")

# Set a single tag
exif.set_tag("Artist", "John Doe")

# Set multiple tags
tags_to_set = {
    "Artist": "Photographer Name",
    "Copyright": "© 2025 Your Name"
}
for tag, value in tags_to_set.items():
    exif.set_tag(tag, value)

# Remove a tag
try:
    exif.remove_tag("Copyright")
except KeyError:
    print("Copyright tag not found")
```

### Working with Multiple Images

```python
from tagkit import ExifImageCollection

# Create a collection from multiple images
collection = ExifImageCollection(["image1.jpg", "image2.jpg", "image3.jpg"])

# Process each image in the collection
for file_path, exif_image in collection.files.items():
    print(f"Processing {file_path}")

    # Get camera make and model
    try:
        make = exif_image.get_tag("Make").value
        model = exif_image.get_tag("Model").value
        print(f"Camera: {make} {model}")
    except KeyError:
        print("Camera information not available")

    # Add copyright information
    exif_image.set_tag("Copyright", "© 2025 Your Name")
    exif_image.save()
```

### Using the Tag Registry

```python
from tagkit.core.registry import ExifRegistry

# Get the registry instance
registry = ExifRegistry()

# Look up tag information
tag_id = registry.resolve_tag_id("Make")
tag_name = registry.resolve_tag_name(tag_id)
tag_type = registry.get_tag_type(tag_id)

print(f"Tag ID for 'Make': {tag_id}")
print(f"Tag name for ID {tag_id}: {tag_name}")
print(f"Data type for 'Make': {tag_type}")
```

### Working with Tag I/O Backends

```python
from tagkit.tag_io.piexif_io import PiexifBackend
from tagkit.core.tag import ExifTag

# Create a backend instance
backend = PiexifBackend()

# Load tags from an image
tags = backend.load_tags("path/to/your/image.jpg")

# Create new tags
new_tags = [
    ExifTag(270, "This is a description", "IFD0"),  # ImageDescription
    ExifTag(315, "Photographer Name", "IFD0")       # Artist
]

# Save tags to the image
backend.save_tags("path/to/your/image.jpg", new_tags)
```
