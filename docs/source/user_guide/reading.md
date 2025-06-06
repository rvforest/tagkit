# Reading

This guide demonstrates how to read EXIF metadata from image files using tagkit.

(cli)=

## Command Line Interface

Tags can be read with the CLI using the `view` command:

```bash
tagkit [global-options] view [options] FILE_OR_PATTERN
```

`FILE_OR_PATTERN` can be a single file name, a glob, or a regex pattern.
The CLI will infer which to use based on the pattern, but you can be explicit with the `--regex` or `--glob` options.
Glob patterns *must* be enclosed in quotes, for example: `tagkit view "*.jpg"`.

The default output is a table. Use the `--json` option for JSON output, which is useful for downstream processing.

Use `--tags` to filter for specific tags.

### Examples

```bash
# View EXIF data for a single file
tagkit view photo.jpg

# View specific tags from multiple files using a glob pattern
tagkit view "*.jpg" --tags Make,Model,DateTimeOriginal

# View EXIF data as JSON
tagkit view --json photo.jpg

# View EXIF data from thumbnails
tagkit view --thumbnail photo.jpg

# Use a regex pattern to match files
tagkit view ".*\d{4}-\d{2}-\d{2}.*\.jpg"
```

(api)=

## API

### Reading All Tags

The simplest way to read all EXIF tags from an image:

```{testcode}
from tagkit.image.exif import ExifImage

# Create an instance for an image
exif = ExifImage("image1.jpg")

# Get all tags
tags = exif.tags

# Print all tags
for tag_id, tag in tags.items():
    print(f"{tag.name}: {tag.value}")
```

### Reading Specific Tags

If you're only interested in certain tags, you can get them directly:

```{testcode}
from tagkit.image.exif import ExifImage

# Create an instance for an image
exif = ExifImage("image1.jpg")

# Get specific tags with error handling
try:
    # Extract camera information
    camera_make = exif.tags["Make"].value
    camera_model = exif.tags["Model"].value
    print(f"Camera: {camera_make} {camera_model}")

    # Extract photo information
    date_taken = exif.tags["DateTimeOriginal"].value
    exposure = exif.tags["ExposureTime"].value
    aperture = exif.tags["FNumber"].value
    iso = exif.tags["ISOSpeedRatings"].value

    print(f"Date Taken: {date_taken}")
    print(f"Exposure: {exposure} sec, f/{aperture}, ISO {iso}")
except KeyError as e:
    print(f"Tag not found: {e}")
```

### Filtering Tags

```{testcode}
from tagkit.image.exif import ExifImage

# Create an instance
exif_data = ExifImage("image1.jpg")

# Get all tags
all_tags = exif_data.tags

# Get a specific tag
make = exif_data.tags["Make"]
print(f"Make: {make}")
```

### Error Handling

Tagkit defines several [custom exceptions](../apidocs/tagkit/tagkit.core.exceptions.rst).
An example of handling errors when writing tags:

```{testcode}
from tagkit.image.exif import ExifImage
from tagkit.core.exceptions import TagkitError

try:
    exif = ExifImage("image.jpg")
except FileNotFoundError:
    print("Error: Image file not found")
except TagkitError as e:
    print(f"Error reading EXIF data: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Next Steps

Now that you've learned how to read EXIF data, check out:

- [Basic Writing Example](./writing.md) to learn how to write EXIF data
- [Batch Processing Example](batch_processing.md) for handling multiple files efficiently
