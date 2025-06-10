# Writing

This guide demonstrates how to write EXIF metadata to image files using tagkit.

## CLI

Writing tag values via the CLI is not yet supported.

## API

### Writing Single Tags

Use the `write_tag` method to write a single tag to an image. You can specify the tag by name or integer ID, along with its value. If the tag does not exist, it will be created.
You may specify an explicit IFD (Image File Directory) using the `ifd` argument. If not specified, the IFD is determined based on the tag name or ID. For tags associated with both the main and thumbnail IFDs, the main IFD is used by default unless the `thumbnail` argument is set to `True`.
If the tag already exists, it will be updated with the new value.

If a tag id or tag name is provided that is present in both the main and thumbnail IFDs, the tag will be written to the main IFD only unless you specify `ifd='IFD1'`. If a tag id or tag name
is provided that is present in two other IFDs and the ifd is not specified, the tag
will be written to the first IFD that contains the tag and a warning is emitted.
IFD's are searched in the order of IFD0, Exif, GPS, Interop. In general, there is much
less chance of overlap when specifying tags by name rather than by ID, but explicitly
specifying the IFD eliminates this issue.

**Note:** Changes are not saved to disk until you call the `save()` method.

```{testcode}
from tagkit.image.exif import ExifImage

# Create an instance for an image
exif = ExifImage("image1.jpg")

# Set a single tag (in-memory)
exif.write_tag("Artist", "Jane Doe")
print(f"Artist tag set for {exif.file_path}")

# Tag 271 is the ID for Make
exif.write_tag(271, "Canon")
print(f"Make tag set for {exif.file_path}")

# Save changes to disk
exif.save()
print(f"Tags written to {exif.file_path}")
```

### Writing Multiple Tags at Once

To efficiently set several tags in a single call, use the `write_tags` method, which accepts a dictionary of tag names or IDs to values.

```{testcode}
from tagkit.image.exif import ExifImage

# Create an instance
exif = ExifImage("image1.jpg")

# Write multiple tags (in-memory)
tags_to_write = {
    "Artist": "Jane Doe",
    "Copyright": "© 2025 Jane Doe"
}
exif.write_tags(tags_to_write)

# Save changes
exif.save()
print(f"Tags written to {exif.file_path}")
```

### Deleting Tags

To remove tags from an image, use the `delete_tag` method. You can specify the tag by name or ID, and optionally target a specific IFD (via the `ifd` argument).
If the tag exists in both the main and thumbnail IFDs and `ifd` is not specified, it will be removed from the main IFD only.

You can also delete multiple tags at once using `delete_tags`, which takes a list of tag names or IDs.

**Remember:** Call `save()` to persist deletions to disk.

```{testcode}
from tagkit.image.exif import ExifImage

# Create an instance
exif = ExifImage("image1.jpg")

# Get all tags
all_tags = exif.tags

# List of tags to keep
tags_to_keep = ["Make", "Model", "DateTimeOriginal"]

# Remove tags not in the keep list
for tag_name, tag in list(all_tags.items()):
    if tag_name not in tags_to_keep:
        try:
            exif.delete_tag(tag.id, ifd=tag.ifd)
        except KeyError:
            pass  # Tag might already be gone

# Add new tags
exif.write_tag("Artist", "Jane Doe")

# Remove multiple tags at once
exif.delete_tags(["Artist", "Copyright"])

# Save changes
exif.save()
print("Tags updated successfully")
```

### Creating Backups Before Saving

A backup can be created automatically before saving changes to the image file. This helps prevent data loss in case of errors during writing.
To enable this feature, pass `create_backup=True` to the `save()` method. The backup will be saved with the same name as the original file, but with a `.bak` extension.

```{testcode}
from tagkit.image.exif import ExifImage

# Create an instance
exif = ExifImage("image1.jpg")

# Write tags (in-memory)
tags_to_write = {"Artist": "Jane Doe"}
exif.write_tags(tags_to_write)

# Save changes and create a backup
exif.save(create_backup=True)
print(f"Tags written to {exif.file_path}")
print(f"Backup created at {exif.file_path}.bak")
```

## Writing GPS Information

You can add GPS coordinates to an image as follows:

```{testcode}
from tagkit.image.exif import ExifImage

# Create an instance for the image
exif = ExifImage("image1.jpg")

# GPS coordinates (latitude, longitude)
# Latitude and longitude must be provided as tuples of (degrees, minutes, seconds),
# where each value is a (numerator, denominator) tuple (i.e., rational number)
latitude = ((40, 1), (44, 1), (52, 1))   # 40° 44' 52" N
longitude = ((73, 1), (59, 1), (2, 1))   # 73° 59' 2" W

# Set GPS tags (in-memory)
exif.write_tag("GPSLatitude", latitude)
exif.write_tag("GPSLatitudeRef", "N")
exif.write_tag("GPSLongitude", longitude)
exif.write_tag("GPSLongitudeRef", "W")
exif.write_tag("GPSAltitude", (105, 10))      # Altitude in meters as rational (e.g., 10.5m)
exif.write_tag("GPSAltitudeRef", 0)      # 0 = above sea level, 1 = below sea level

# Save changes
exif.save()
print("GPS information added successfully")
```

## Error Handling

Tagkit defines several [custom exceptions](../apidocs/tagkit/tagkit.core.exceptions.rst).
Here is an example of handling errors when writing tags:

```{testcode}
from tagkit.image.exif import ExifImage
from tagkit.core.exceptions import TagkitError

try:
    exif = ExifImage("path/to/your/image.jpg")
    exif.write_tag("Artist", "Jane Doe")
    exif.save()
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
