# Quickstart Guide

This guide will help you get up and running with tagkit quickly.

## Basic Usage

### Reading EXIF Tags

```python
from tagkit.image_exif import ImageExifData

# Create an instance for an image
exif = ImageExifData("path/to/your/image.jpg")

# Read all EXIF tags
tags = exif.get_tags()
for tag_id, tag in tags.items():
    print(f"{tag.name}: {tag.value}")

# Read specific tags
make = exif.get_tag("Make")
date_taken = exif.get_tag("DateTimeOriginal")
print(f"Photo taken with {make.value} on {date_taken.value}")
```

### Modifying EXIF Tags

```python
from tagkit.image_exif import ImageExifData

# Create an instance for an image
exif = ImageExifData("path/to/your/image.jpg")

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

### Using the Tag Registry

```python
from tagkit import tag_registry

# List all available tag names
tag_names = tag_registry.tag_names
print(f"Available tags: {', '.join(tag_names[:5])}...")

# Get information about a specific tag
tag_id = tag_registry.get_tag_id("Make")
tag_name = tag_registry.get_tag_name(tag_id)
tag_type = tag_registry.get_exif_type(tag_id)
print(f"Tag '{tag_name}' has ID {tag_id} and type {tag_type}")

# Register a custom tag (if needed)
tag_registry.register_tag(
    ifd="Exif",
    tag_id=0x9999,
    name="MyCustomTag",
    exif_type="ASCII"
)
```

### Working with Thumbnail Tags

```python
from tagkit.image_exif import ImageExifData

# Create an instance for an image
exif = ImageExifData("path/to/your/image.jpg")


# Get thumbnail tags
thumbnail_tags = exif.get_tags(thumbnail=True)
print(f"Found {len(thumbnail_tags)} tags in thumbnail")

# Set a tag in the thumbnail
exif.set_tag("ImageDescription", "Thumbnail description", thumbnail=True)

# Remove a tag from the thumbnail
try:
    exif.remove_tag("ImageDescription", thumbnail=True)
except KeyError:
    print("Tag not found in thumbnail")
```

## Next Steps

- Learn more about [working with EXIF data](tutorials/basic_exif_operations.md)
- Explore [advanced usage](tutorials/advanced_usage.md) for more complex scenarios

## Command Line Interface

Tagkit also provides a convenient command-line interface:

```bash
# Read all tags from an image
tagkit read path/to/your/image.jpg

# Read specific tags
tagkit read path/to/your/image.jpg --tags Model,DateTimeOriginal

# Write tags to an image
tagkit write path/to/your/image.jpg --tag Artist="Photographer Name" --tag Copyright="© 2025"

# List all available tags
tagkit list-tags
```

## Next Steps

- Explore the [Usage Guide](usage.md) for more detailed examples
- Check out the [Tutorials](tutorials/index.md) for step-by-step guides
- See the [API Reference](api.md) for complete documentation of all functions and classes
