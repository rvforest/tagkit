# Custom Tags Example

This example demonstrates how to work with custom EXIF tags in tagkit.

## Understanding Custom Tags

EXIF has standard tags defined in the specification, but you can also create and use custom tags for specialized needs. Custom tags require:

1. A unique tag ID (typically in a private range)
2. A data type (string, integer, etc.)
3. A name and description

## Registering Custom Tags

Before using custom tags, you need to register them with the tag registry:

```python
from tagkit.tag_registry import tag_registry

# Register a custom tag
tag_registry.register_custom_tag(
    name="ProjectName",
    tag_id=0x9C9C,  # Choose a unique ID in the private range
    tag_type="string"
)

# Register another custom tag
tag_registry.register_custom_tag(
    name="SceneID",
    tag_id=0x9C9D,
    tag_type="integer"
)

# Verify the tags were registered
print(f"ProjectName tag ID: 0x{tag_registry.get_tag_id('ProjectName'):X}")
print(f"SceneID tag ID: 0x{tag_registry.get_tag_id('SceneID'):X}")
print(f"ProjectName tag type: {tag_registry.get_tag_type('ProjectName')}")
```

## Writing Custom Tags

Once registered, you can write custom tags just like standard tags:

```python
from tagkit.image_exif import ImageExifData
from tagkit.tag_registry import tag_registry

# Register custom tags
tag_registry.register_custom_tag(
    name="ProjectName",
    tag_id=0x9C9C,
    tag_type="string"
)

tag_registry.register_custom_tag(
    name="SceneID",
    tag_id=0x9C9D,
    tag_type="integer"
)

# Now write the custom tags to an image
exif = ImageExifData("path/to/your/image.jpg")

# Set the custom tags
exif.set_tag("ProjectName", "Mountain Landscape Series")
exif.set_tag("SceneID", 42)

print(f"Custom tags written to {exif.file_path}")
```

## Reading Custom Tags

To read custom tags, they must be registered before reading:

```python
from tagkit.image_exif import ImageExifData
from tagkit.tag_registry import tag_registry

# First, register the custom tags
tag_registry.register_custom_tag(
    name="ProjectName",
    tag_id=0x9C9C,
    tag_type="string"
)

tag_registry.register_custom_tag(
    name="SceneID",
    tag_id=0x9C9D,
    tag_type="integer"
)

# Now read the image including custom tags
exif = ImageExifData("path/to/your/image.jpg")

# Access the custom tags
try:
    project_name = exif.get_tag("ProjectName").value
    scene_id = exif.get_tag("SceneID").value

    print(f"Project: {project_name}")
    print(f"Scene ID: {scene_id}")
except KeyError as e:
    print(f"Tag not found: {e}")
```

## Working with Vendor-Specific Tags

You can also register vendor-specific tags that are not part of the standard EXIF specification:

```python
from tagkit.image_exif import ImageExifData
from tagkit.tag_registry import tag_registry

# Register a vendor-specific tag
tag_registry.register_custom_tag(
    name="CanonImageType",
    tag_id=0x0083,  # Canon-specific tag ID
    tag_type="string"
)

# Read the tag from a Canon image
exif = ImageExifData("path/to/canon_image.jpg")

try:
    image_type = exif.get_tag("CanonImageType").value
    print(f"Canon Image Type: {image_type}")
except KeyError:
    print("Canon Image Type tag not found")
```

## Batch Processing with Custom Tags

For more complex custom tag sets, you can create a helper function:

```python
from tagkit.tag_registry import tag_registry

def register_project_tags():
    """Register all custom tags for a project."""
    # Register project-specific tags
    tag_registry.register_custom_tag(
        name="ProjectName",
        tag_id=0x9C9C,
        tag_type="string"
    )

    tag_registry.register_custom_tag(
        name="SceneID",
        tag_id=0x9C9D,
        tag_type="integer"
    )

    tag_registry.register_custom_tag(
        name="LocationCode",
        tag_id=0x9C9E,
        tag_type="string"
    )

# Register all project tags
register_project_tags()

# Now use them in batch processing
import os
from tagkit.image_exif import ImageExifData

def process_directory(directory_path, project_name):
    """Process all images in a directory with custom tags."""
    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.tiff', '.tif')

    # Process all images
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(image_extensions):
            file_path = os.path.join(directory_path, filename)

            # Create exif instance
            exif = ImageExifData(file_path)

            # Add custom tags
            exif.set_tag("ProjectName", project_name)
            exif.set_tag("SceneID", get_scene_id(filename))
            exif.set_tag("LocationCode", "LOC-" + filename[:3])

            print(f"Tagged {filename}")

def get_scene_id(filename):
    """Extract scene ID from filename."""
    # Example: IMG_1234.jpg -> 1234
    try:
        return int(filename.split('_')[1].split('.')[0])
    except (IndexError, ValueError):
        return 0

# Example usage
process_directory("path/to/your/images", "Mountain Landscape Series")
```

## Checking for Custom Tags

You can check if a custom tag exists in an image:

```python
from tagkit.image_exif import ImageExifData
from tagkit.tag_registry import tag_registry

# Register custom tags first
tag_registry.register_custom_tag(
    name="ProjectName",
    tag_id=0x9C9C,
    tag_type="string"
)

# Create exif instance
exif = ImageExifData("path/to/your/image.jpg")

# Check if the tag exists
try:
    project_tag = exif.get_tag("ProjectName")
    print(f"Project name found: {project_tag.value}")
except KeyError:
    print("No project name tag found in this image")

# You can also check all available tags
all_tags = exif.get_tags()
for tag_id, tag in all_tags.items():
    print(f"{tag.name}: {tag.value}")
```

## Custom Tag Namespaces

You can organize custom tags into namespaces to avoid conflicts:

```python
from tagkit.tag_registry import tag_registry

# Register tags with namespace prefixes
tag_registry.register_custom_tag(
    name="MyCompany:ProjectID",
    tag_id=0x9D01,
    tag_type="string",
    description="Project identifier",
    category="MyCompany"
)

tag_registry.register_custom_tag(
    name="MyCompany:ClientName",
    tag_id=0x9D02,
    tag_type="string",
    description="Client name",
    category="MyCompany"
)

# Write tags with namespaces
from tagkit.image_exif import write_exif

write_exif("image.jpg", {
    "MyCompany:ProjectID": "PROJ-123",
    "MyCompany:ClientName": "Acme Corp"
})
```

## Next Steps

Now that you've learned how to work with custom tags, check out:

- [Metadata Analysis Example](metadata_analysis.md) for analyzing image collections
- [GPS Mapping Example](gps_mapping.md) for working with location data
