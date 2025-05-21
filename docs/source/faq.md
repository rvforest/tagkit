# Frequently Asked Questions

## General Questions

### What is tagkit?

Tagkit is a Python library for reading, writing, and manipulating metadata tags in image files, with a focus on EXIF, XMP, and IPTC standards. It provides both a programming API and a command-line interface.

### Which Python versions are supported?

Tagkit supports Python 3.8 and newer versions.

### Is tagkit compatible with Windows/macOS/Linux?

Yes, tagkit is cross-platform and works on Windows, macOS, and Linux.

## Installation Questions

### Why am I getting installation errors?

Common installation issues include:

1. **Incompatible Python version**: Ensure you're using Python 3.8 or newer
2. **Missing dependencies**: Some dependencies require system libraries. On Linux, you might need to install `libjpeg-dev` and `libexif-dev`
3. **Permission issues**: Try installing with `pip install --user tagkit` or use a virtual environment

### Can I use tagkit with Anaconda/Conda?

Yes, you can install tagkit in a Conda environment:

```bash
conda create -n tagkit-env python=3.9
conda activate tagkit-env
pip install tagkit
```

## Usage Questions

### How do I read EXIF data from an image?

```python
from tagkit.image_exif import read_exif

tags = read_exif("path/to/image.jpg")
print(tags)
```

### Why are some tags missing when I read an image?

Some possible reasons:

1. The image doesn't contain those specific tags
2. The tags use a format not supported by tagkit
3. The image file might be corrupted

Try using the `--verbose` flag with the CLI to get more information:

```bash
tagkit read image.jpg --verbose
```

### How do I preserve original metadata when writing new tags?

By default, tagkit preserves existing metadata. If you want to explicitly ensure this behavior:

```python
from tagkit.image_exif import write_exif

write_exif("image.jpg", {"Artist": "Jane Doe"}, preserve_existing=True)
```

### Can I remove all metadata from an image?

Yes, you can use the `remove_all_metadata` function:

```python
from tagkit.image_exif import remove_all_metadata

remove_all_metadata("image.jpg")
```

Or with the CLI:

```bash
tagkit remove image.jpg --all
```

## File Format Questions

### Which image formats are supported?

Tagkit supports the following formats:
- JPEG (.jpg, .jpeg)
- TIFF (.tif, .tiff)
- PNG (.png)
- WebP (.webp)
- HEIF/HEIC (.heif, .heic) - requires additional dependencies

### Can I use tagkit with RAW image formats?

Yes, tagkit supports common RAW formats including:
- Canon RAW (.cr2, .cr3)
- Nikon RAW (.nef)
- Sony RAW (.arw)
- Adobe DNG (.dng)

Note that RAW support requires installing the optional RAW dependencies:

```bash
pip install "tagkit[raw]"
```

### Does tagkit support video files?

Yes, tagkit can read and write metadata for some video formats, including:
- MP4 (.mp4)
- QuickTime (.mov)
- AVI (.avi)

Video support is limited to metadata that follows the same standards as image files.

## Advanced Questions

### How do I handle custom or non-standard tags?

You can work with custom tags by defining them in your configuration:

```python
from tagkit.tag_registry import TagRegistry

registry = TagRegistry()
registry.register_custom_tag(
    name="MyCustomTag",
    tag_id=0x9999,
    tag_type="string",
    description="My custom tag"
)
```

### Can I use tagkit with cloud storage services?

Tagkit primarily works with local files. For cloud storage:

1. Download the file locally
2. Process it with tagkit
3. Upload the modified file back to cloud storage

Some cloud services may strip metadata during upload, so check your service's documentation.

### How do I contribute to tagkit?

See our [Contributing Guide](contributing.md) for information on how to contribute to the project.

## Troubleshooting

### Why did tagkit modify my original image?

By default, tagkit modifies files in place. To preserve originals:

1. Use the `--backup` flag with CLI commands
2. Use the `save_as()` method when using the API
3. Set `general.backup: true` in your configuration file

### I'm getting "Tag not found" errors

This could happen if:
1. You're using a tag name that doesn't exist in the standard
2. The tag name has a different capitalization or format than expected

Use `tagkit list-tags` to see all available standard tags.

### How do I report a bug?

Please report bugs on our GitHub issue tracker with:
1. A clear description of the problem
2. Steps to reproduce the issue
3. Information about your environment (Python version, OS, tagkit version)
4. If possible, a sample image that demonstrates the issue (with personal data removed)
