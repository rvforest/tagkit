# Tag I/O System

The Tag I/O system in tagkit provides a flexible framework for reading and writing metadata tags from various sources and formats.

## Overview

The Tag I/O system abstracts the process of reading and writing metadata tags, allowing you to work with different file formats and sources using a consistent API.

```{toctree}
:maxdepth: 1

readers.md
writers.md
formats.md
```

## Basic Concepts

### EXIF I/O Backend System

Tagkit's I/O system is built around the `ExifIOBackend` abstract base class, which defines the interface for reading and writing EXIF data. The default implementation uses the `piexif` library.

### Supported IFDs (Image File Directories)

Tagkit supports the following IFDs for EXIF data:

- `IFD0` (0th IFD) - Main image tags
- `IFD1` (1st IFD) - Thumbnail image tags
- `Exif` - EXIF-specific metadata
- `GPS` - GPS-related tags
- `Interop` - Interoperability information

### Tag Storage

EXIF tags are stored in an `ExifTagDict` which is a specialized dictionary that maps `(tag_id, ifd_name)` tuples to `ExifEntry` objects. The dictionary provides convenient access to tags by ID alone when there's no ambiguity.

### Default Implementation

The default `PiexifBackend` provides the following functionality:

- **Reading EXIF data** from image files
- **Writing EXIF data** back to image files
- Automatic handling of ASCII string encoding/decoding
- Conversion between piexif's IFD naming and tagkit's standard naming

### Character Encoding

While the EXIF standard only allows ASCII, the implementation uses UTF-8 encoding for better compatibility with modern systems. This affects how string values are stored and retrieved from EXIF data.

## Using the EXIF I/O System

### Basic Usage

The main way to interact with EXIF data is through the `ImageExifData` class, which internally uses the I/O backend system:

```python
from tagkit.image_exif import ImageExifData

# Create an instance for an image
exif = ImageExifData("path/to/your/image.jpg")

# Read all tags
tags = exif.get_tags()

# Read a specific tag
try:
    make = exif.get_tag("Make")
    print(f"Camera make: {make.value}")
except KeyError:
    print("Make tag not found")
```

### Using a Custom I/O Backend

You can create and use a custom I/O backend by implementing the `ExifIOBackend` interface:

```python
from tagkit.tag_io.base import ExifIOBackend, ExifTagDict
from tagkit.exif_entry import ExifEntry
from tagkit.types import FilePath

class MyCustomBackend(ExifIOBackend):
    def load_tags(self, image_path: FilePath) -> ExifTagDict:
        # Implement loading tags from the image
        # Return an ExifTagDict
        pass
        
    def save_tags(self, image_path: FilePath, tags: ExifTagDict) -> None:
        # Implement saving tags to the image
        pass

# Use the custom backend
from tagkit.image_exif import ImageExifData

exif = ImageExifData("path/to/image.jpg", io_backend=MyCustomBackend())
```

### Working with Thumbnails

The I/O system supports reading and writing thumbnail EXIF data:

```python
from tagkit.image_exif import ImageExifData

# Create an instance for an image
exif = ImageExifData("path/to/your/image.jpg")

# Get thumbnail tags
thumbnail_tags = exif.get_tags(thumbnail=True)

# Set a tag in the thumbnail
exif.set_tag("ImageDescription", "Thumbnail description", thumbnail=True)
```

## Advanced Usage

### Direct Backend Usage

For advanced use cases, you can use the backend directly:

```python
from tagkit.tag_io.piexif_io import PiexifBackend

# Create a backend instance
backend = PiexifBackend()

# Load tags
tags = backend.load_tags("path/to/image.jpg")

# Modify tags as needed
# ...

# Save tags
backend.save_tags("path/to/image.jpg", tags)
```

## Next Steps

- Learn more about [working with EXIF data](../tutorials/basic_exif_operations.md)
- Explore the [API Reference](../api.md) for detailed class and function documentation
- Check out the [configuration guide](../configuration.md) for customizing tag handling
