# Development Guide

This guide provides detailed information for developers working on or extending the tagkit library.

## Architecture Overview

Tagkit is organized into several core components:

1. **Core Components**:
   - `image_exif.py`: Handles reading and writing EXIF data
   - `tag_registry.py`: Manages the registry of known tags
   - `exif_entry.py`: Represents individual EXIF entries
   - `value_formatting.py`: Handles formatting and parsing of tag values

2. **I/O System**:
   - `tag_io/`: Contains readers and writers for different formats
   - `operations.py`: High-level operations for working with tags

3. **CLI**:
   - `cli/`: Command-line interface components

4. **Utilities**:
   - `utils.py`: Common utility functions
   - `types.py`: Type definitions
   - `exceptions.py`: Custom exceptions

## Code Organization

```
src/tagkit/
├── __init__.py             # Package initialization
├── cli/                    # Command-line interface
│   ├── __init__.py
│   ├── commands.py         # CLI commands
│   └── main.py             # CLI entry point
├── conf/                   # Configuration handling
│   ├── __init__.py
│   └── config.py           # Configuration management
├── exceptions.py           # Custom exceptions
├── exif_entry.py           # EXIF entry representation
├── image_exif.py           # EXIF reading/writing
├── operations.py           # High-level operations
├── tag_io/                 # Tag I/O system
│   ├── __init__.py
│   ├── readers.py          # Tag readers
│   └── writers.py          # Tag writers
├── tag_registry.py         # Tag registry
├── types.py                # Type definitions
├── utils.py                # Utility functions
└── value_formatting.py     # Value formatting
```

## Core Components

### Image EXIF Module

The `image_exif.py` module is the primary interface for working with EXIF data in images. It provides functions for reading, writing, and manipulating EXIF tags.

Key components:
- `ImageExifData` class: Represents EXIF data for an image
- `read_exif()`: Function to read EXIF data from an image
- `write_exif()`: Function to write EXIF data to an image

### Tag Registry

The `tag_registry.py` module maintains a registry of known EXIF tags and their properties.

Key components:
- `TagRegistry` class: Manages the registry of known tags
- `TagInfo` class: Represents information about a tag

### EXIF Entry

The `exif_entry.py` module defines the representation of individual EXIF entries.

Key components:
- `ExifEntry` class: Represents a single EXIF tag entry
- `ExifValue` class: Represents the value of an EXIF tag

### Value Formatting

The `value_formatting.py` module handles formatting and parsing of tag values.

Key components:
- `format_value()`: Formats a value for display
- `parse_value()`: Parses a string value into the appropriate type

## Extending Tagkit

### Adding New Tag Types

To add support for a new tag type:

1. Update the `TagRegistry` in `tag_registry.py`:
   ```python
   registry.register_tag(
       name="NewTagName",
       tag_id=0x9999,  # Unique ID
       tag_type="string",  # Data type
       description="Description of the new tag",
       category="Category"
   )
   ```

2. If needed, add custom formatting in `value_formatting.py`:
   ```python
   def format_new_tag_type(value):
       """Format the new tag type for display."""
       # Custom formatting logic
       return formatted_value
   
   # Register the formatter
   register_formatter("new_tag_type", format_new_tag_type)
   ```

### Adding Support for New File Formats

To add support for a new file format:

1. Create a new reader in `tag_io/readers.py`:
   ```python
   class NewFormatReader(BaseTagReader):
       """Reader for the new format."""
       
       def read_all(self):
           """Read all tags from the source."""
           # Implementation
           return tags
       
       def read_tags(self, tag_names):
           """Read specific tags from the source."""
           # Implementation
           return tags
   ```

2. Create a new writer in `tag_io/writers.py`:
   ```python
   class NewFormatWriter(BaseTagWriter):
       """Writer for the new format."""
       
       def write_tags(self, tags):
           """Write tags to the target."""
           # Implementation
           
       def write_tags_to_new_file(self, tags, output_file):
           """Write tags to a new file."""
           # Implementation
   ```

3. Register the new format in `tag_io/__init__.py`:
   ```python
   register_reader("new_format", NewFormatReader)
   register_writer("new_format", NewFormatWriter)
   ```

### Creating Plugins

Tagkit supports plugins for extending functionality:

1. Create a plugin module:
   ```python
   # my_tagkit_plugin.py
   
   def initialize_plugin(registry):
       """Initialize the plugin."""
       # Register custom tags, formatters, etc.
       registry.register_tag(...)
   ```

2. Register the plugin in your configuration:
   ```yaml
   # .tagkit.yaml
   plugins:
     - my_tagkit_plugin
   ```

## Performance Considerations

### Optimizing for Large Files

When working with large image files:

1. Use selective tag reading:
   ```python
   # Instead of reading all tags
   tags = read_exif(image_path)
   
   # Read only the tags you need
   tags = read_exif(image_path, tags=["Make", "Model", "DateTimeOriginal"])
   ```

2. Use batch processing for multiple files:
   ```python
   from tagkit.operations import batch_process
   
   def process_image(image_path):
       # Process a single image
       return result
   
   results = batch_process(image_paths, process_image, max_workers=4)
   ```

### Memory Management

For memory-intensive operations:

1. Use streaming APIs when available:
   ```python
   with open_exif_stream(large_image_path) as stream:
       for tag in stream:
           # Process one tag at a time
           process_tag(tag)
   ```

2. Clean up resources explicitly:
   ```python
   exif_data = ImageExifData(image_path)
   try:
       # Work with exif_data
   finally:
       exif_data.close()
   ```

## Testing

### Unit Testing

Write unit tests for individual components:

```python
# tests/test_tag_registry.py
def test_register_tag():
    registry = TagRegistry()
    registry.register_tag("TestTag", 0x9999, "string", "Test description")
    
    tag_info = registry.get_tag_info("TestTag")
    assert tag_info is not None
    assert tag_info.tag_id == 0x9999
    assert tag_info.tag_type == "string"
```

### Integration Testing

Write integration tests for interactions between components:

```python
# tests/integration/test_read_write.py
def test_read_write_roundtrip():
    # Write tags to a test image
    test_tags = {"Artist": "Test Artist", "Copyright": "Test Copyright"}
    write_exif("test_image.jpg", test_tags)
    
    # Read tags back
    read_tags = read_exif("test_image.jpg")
    
    # Verify tags were preserved
    assert read_tags["Artist"] == "Test Artist"
    assert read_tags["Copyright"] == "Test Copyright"
```

### Test Data

Use the provided test images in `tests/data/`:

- `test_image.jpg`: Standard test image with known EXIF data
- `no_exif.jpg`: Image with no EXIF data
- `corrupt_exif.jpg`: Image with corrupted EXIF data

## Debugging

### Logging

Tagkit uses Python's standard logging module:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("tagkit")

# Use logger in your code
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
```

### Debugging Tools

For debugging complex issues:

1. Enable verbose output:
   ```python
   from tagkit.conf import config
   
   config.set("general.verbose", True)
   ```

2. Use the debug CLI mode:
   ```bash
   tagkit --debug read image.jpg
   ```

## API Stability

### Versioning Policy

- Public API functions and classes are guaranteed to be stable within a major version
- Internal modules (prefixed with underscore) may change between minor versions
- Experimental features are marked with a warning and may change at any time

### Deprecation Process

1. Mark deprecated features with warnings:
   ```python
   import warnings
   
   def deprecated_function():
       warnings.warn(
           "deprecated_function is deprecated and will be removed in version 2.0. "
           "Use new_function instead.",
           DeprecationWarning,
           stacklevel=2
       )
       # Implementation
   ```

2. Document deprecations in the changelog
3. Remove deprecated features in the next major version

## Documentation

### Docstrings

Use Google-style docstrings for all public APIs:

```python
def example_function(param1: str, param2: int) -> bool:
    """Example function with Google style docstring.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    return len(param1) > param2
```

### Building Documentation

Build documentation with Sphinx:

```bash
cd docs
make html
```

## Resources

- [EXIF Specification](https://www.exif.org/specifications.html)
- [XMP Specification](https://www.adobe.com/devnet/xmp.html)
- [IPTC Standard](https://iptc.org/standards/photo-metadata/)
