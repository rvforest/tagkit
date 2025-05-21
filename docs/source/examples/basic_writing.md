# Basic Writing Example

This example demonstrates how to write EXIF metadata to image files using tagkit.

## Writing Single Tags

The simplest way to write a single tag to an image:

```python
from tagkit.image_exif import ImageExifData

# Create an instance for an image
exif = ImageExifData("path/to/your/image.jpg")

# Set a single tag
exif.set_tag("Artist", "Jane Doe")
print(f"Artist tag written to {exif.file_path}")
```

## Writing Multiple Tags

You can write multiple tags one after another:

```python
from tagkit.image_exif import ImageExifData

# Create an instance for an image
exif = ImageExifData("path/to/your/image.jpg")

# Define multiple tags to write
tags_to_write = {
    "Artist": "Jane Doe",
    "Copyright": " 2025 Jane Doe",
    "UserComment": "Beautiful sunset at the beach",
    "Software": "tagkit example"
}

# Set each tag
for tag_name, tag_value in tags_to_write.items():
    exif.set_tag(tag_name, tag_value)
    
print(f"Multiple tags written to {exif.file_path}")
```

## Creating Backups Before Writing

It's a good practice to create a backup before modifying EXIF data:

```python
from tagkit.image_exif import ImageExifData
import shutil

# Create an instance with backup enabled
exif = ImageExifData(
    "path/to/your/image.jpg",
    create_backup_on_mod=True  # This will create a backup automatically
)
backup_path = f"{exif.file_path}.bak"
shutil.copy2(exif.file_path, backup_path)
print(f"Backup created at {backup_path}")

# Write tags
tags_to_write = {"Artist": "Jane Doe"}
for tag_name, tag_value in tags_to_write.items():
    exif.set_tag(tag_name, tag_value)
print(f"Tags written to {exif.file_path}")
```

## Using the ImageExifData Class

For more control, you can use the `ImageExifData` class directly:

```python
from tagkit.image_exif import ImageExifData

# Create an instance
exif_data = ImageExifData("path/to/your/image.jpg")

# Set individual tags
exif_data.set_tag("Artist", "Jane Doe")
exif_data.set_tag("Copyright", " 2025 Jane Doe")
exif_data.set_tag("UserComment", "Beautiful sunset at the beach")

# Save changes to the original file
exif_data.save()

# Or save to a new file (preserving the original)
exif_data.save_as("path/to/modified_image.jpg")
```

## Selectively Preserving Metadata

If you want to keep only specific tags and remove others:

```python
from tagkit.image_exif import ImageExifData

# Create an instance
exif = ImageExifData("path/to/your/image.jpg")

# Get all tags
all_tags = exif.get_tags()

# List of tags to keep
tags_to_keep = ["Make", "Model", "DateTimeOriginal"]

# Remove tags not in the keep list
for tag_id, tag in list(all_tags.items()):
    if tag.name not in tags_to_keep:
        try:
            exif.remove_tag(tag.id, ifd=tag.ifd)
        except KeyError:
            pass  # Tag might already be gone

# Add new tags
exif.set_tag("Artist", "Jane Doe")
print("Tags updated successfully")
```

## Error Handling

Include error handling when writing EXIF data:

```python
from tagkit.image_exif import ImageExifData
from tagkit.exceptions import TagkitError

try:
    exif = ImageExifData("path/to/your/image.jpg")
    exif.set_tag("Artist", "Jane Doe")
    print("Tags written successfully")
except FileNotFoundError:
    print("Error: Image file not found")
except PermissionError:
    print("Error: No permission to write to the file")
except TagkitError as e:
    print(f"Error writing EXIF data: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Writing Tags with Special Formatting

Some tags require special formatting:

```python
from tagkit.image_exif import ImageExifData
from datetime import datetime

# Create an instance
exif = ImageExifData("path/to/your/image.jpg")

# Get current date and time in EXIF format
now = datetime.now().strftime("%Y:%m:%d %H:%M:%S")

# Set date-related tags
exif.set_tag("DateTimeOriginal", now)
exif.set_tag("CreateDate", now)
exif.set_tag("ModifyDate", now)

print("Date tags updated successfully")
```

## Writing GPS Information

Adding GPS coordinates to an image:

```python
from tagkit.image_exif import ImageExifData

# Create an instance
exif = ImageExifData("path/to/your/image.jpg")

# GPS coordinates (latitude, longitude)
# Format: Degrees, minutes, seconds
latitude = (40, 44, 52.0)  # 40° 44' 52" N
longitude = (73, 59, 2.0)  # 73° 59' 2" W

# Set GPS tags
exif.set_tag("GPSLatitude", latitude)
exif.set_tag("GPSLatitudeRef", "N")
exif.set_tag("GPSLongitude", longitude)
exif.set_tag("GPSLongitudeRef", "W")
exif.set_tag("GPSAltitude", 10.5)  # Altitude in meters
exif.set_tag("GPSAltitudeRef", 0)    # 0 = above sea level, 1 = below sea level

print("GPS information added successfully")
```

## Next Steps

Now that you've learned how to write EXIF data, check out:

- [Batch Processing Example](batch_processing.md) for handling multiple files efficiently
- [Custom Tags Example](custom_tags.md) to learn how to work with custom tags
