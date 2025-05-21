# Basic EXIF Operations

This tutorial covers the fundamental operations for working with EXIF metadata in images using tagkit.

## Reading EXIF Data

### Reading All Tags

The most basic operation is reading all EXIF tags from an image:

```python
from tagkit.image_exif import ImageExifData

# Create an instance for an image
exif = ImageExifData("path/to/your/image.jpg")

# Read all EXIF tags
tags = exif.get_tags()

# Print all tags
for tag_id, tag in tags.items():
    print(f"{tag.name}: {tag.value}")
```

### Reading Specific Tags

If you're only interested in certain tags, you can get them directly:

```python
from tagkit.image_exif import ImageExifData

# Create an instance for an image
exif = ImageExifData("path/to/your/image.jpg")

# Get specific tags
try:
    make = exif.get_tag("Make").value
    model = exif.get_tag("Model").value
    date_taken = exif.get_tag("DateTimeOriginal").value
    exposure = exif.get_tag("ExposureTime").value
    fnumber = exif.get_tag("FNumber").value
    iso = exif.get_tag("ISOSpeedRatings").value  # Note: Some tags might have different names
    
    print("Camera Information:")
    print(f"  Make: {make}")
    print(f"  Model: {model}")
    print(f"  Date Taken: {date_taken}")
    print("Exposure Information:")
    print(f"  Exposure Time: {exposure}")
    print(f"  F-Number: {fnumber}")
    print(f"  ISO: {iso}")
except KeyError as e:
    print(f"Tag not found: {e}")
```

## Modifying EXIF Data

### Adding or Updating Tags

You can add new tags or update existing ones:

```python
from tagkit.image_exif import ImageExifData

# Create an instance for an image
exif = ImageExifData("path/to/your/image.jpg")

# Set individual tags
exif.set_tag("Artist", "Jane Doe")
exif.set_tag("Copyright", "© 2025 Jane Doe")

# Or set multiple tags
tags_to_set = {
    "Artist": "Jane Doe",
    "Copyright": "© 2025 Jane Doe",
    "UserComment": "Beautiful sunset at the beach"
}

for tag, value in tags_to_set.items():
    exif.set_tag(tag, value)

# Changes are automatically saved to the original file
print("Tags updated successfully")
```

### Backing Up Before Modifying

It's a good practice to create a backup before modifying EXIF data:

```python
import shutil
from tagkit.image_exif import ImageExifData

image_path = "path/to/your/image.jpg"
backup_path = image_path + ".backup"

# Create a backup
shutil.copy2(image_path, backup_path)
print(f"Backup created at {backup_path}")

# Modify the original
try:
    exif = ImageExifData(image_path, create_backup_on_mod=True)
    exif.set_tag("Artist", "Jane Doe")
    print("Tags updated successfully")
except Exception as e:
    print(f"Error updating tags: {e}")
```

## Removing EXIF Data

To remove specific tags from an image:

```python
from tagkit.image_exif import ImageExifData

# Create an instance for an image
exif = ImageExifData("path/to/your/image.jpg")

# Remove specific tags
try:
    exif.remove_tag("GPSLatitude")
    exif.remove_tag("GPSLongitude")
    print("GPS location data removed")
except KeyError:
    print("GPS tags not found")

# Note: There's no wildcard support, remove tags individually
```

## Working with Thumbnails

You can also work with thumbnail EXIF data:

```python
from tagkit.image_exif import ImageExifData

# Create an instance for an image
exif = ImageExifData("path/to/your/image.jpg")

# Get thumbnail tags
thumbnail_tags = exif.get_tags(thumbnail=True)
print(f"Found {len(thumbnail_tags)} tags in thumbnail")

# Modify thumbnail tags
exif.set_tag("ImageDescription", "Thumbnail description", thumbnail=True)

# Remove a thumbnail tag
try:
    exif.remove_tag("ImageDescription", thumbnail=True)
except KeyError:
    print("Tag not found in thumbnail")
```

## Next Steps

Now that you understand the basics of reading and writing EXIF data with tagkit, you can:

- Learn about [batch processing](batch_processing.md) multiple images
- Explore how to work with [custom tags](custom_tags.md)
- See how to integrate with image processing workflows in [advanced tutorials](advanced_filtering.md)
