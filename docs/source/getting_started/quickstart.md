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

# Set multiple tags at once
tags_to_set = {
    "Artist": "Photographer Name",
    "Copyright": "© 2025 Your Name"
}
exif.write_tags(tags_to_set)

# Delete a tag
try:
    exif.delete_tag("Copyright")
except KeyError:
    print("Copyright tag not found")

# Delete multiple tags at once
exif.delete_tags(["Artist", "Copyright"])
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

# Set a tag for all images in the collection
collection.write_tag("Artist", "John Doe")

# Set multiple tags for all images in the collection
multi_tag_dict = {
    "Artist": "Photographer Name",
    "Copyright": "© 2025 Your Name"
}
collection.write_tags(multi_tag_dict)

# Remove a tag from all images
collection.delete_tag("Artist")

# Remove multiple tags from all images
collection.delete_tags(["Artist", "Copyright"])

# Set a tag for a single image
collection.write_tag("Artist", "Jane", files=["image2.jpg"])

# Remove a tag from a single image
collection.delete_tag("Artist", files=["image2.jpg"])

# Remove multiple tags from a single image
collection.delete_tags(["Artist", "Copyright"], files=["image2.jpg"])

# Save all changes to all images, making a backup of each
collection.save_all(create_backup=True)
```
