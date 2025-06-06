# Quickstart Guide

This guide will help you get up and running with tagkit quickly.

## Basic Usage

### Reading EXIF Tags

```{testcode}
from tagkit.image.exif import ExifImage

# Create an instance for an image
exif = ExifImage("image1.jpg")

# Read all EXIF tags
tags = exif.tags
print(tags)

# Read specific tags
make = exif.tags["Make"]
print(f"Photo taken with {make.value}")
```

### Modifying EXIF Tags

```{testcode}
from tagkit.image.exif import ExifImage

# Create an instance for an image
exif = ExifImage("image1.jpg")

# Set a single tag
exif.write_tag("Artist", "John Doe")

# Set multiple tags
tags_to_set = {
    "Artist": "Photographer Name",
    "Copyright": "© 2025 Your Name"
}
for tag, value in tags_to_set.items():
    exif.write_tag(tag, value)

# Delete a tag
try:
    exif.delete_tag("Copyright")
except KeyError:
    print("Copyright tag not found")
```

### Working with Multiple Images

```{testcode}
from tagkit import ExifImageCollection

# Create a collection from multiple images
collection = ExifImageCollection(["image1.jpg", "image2.jpg", "image3.jpg"])

# Print all tags as dictionary
print(collection.as_dict())

# Process each image in the collection
for file_path, exif_image in collection.files.items():
    print(f"Processing {file_path}")

    # Get camera make and model
    try:
        make = exif_image.tags["Make"].value
        model = exif_image.tags["Model"].value
        print(f"Camera: {make} {model}")
    except KeyError:
        print("Camera information not available")

    # Add copyright information
    exif_image.write_tag("Copyright", "© 2025 Your Name")
    exif_image.save()
```
