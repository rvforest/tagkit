<!-- markdownlint-disable MD033 MD041 -->
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/source/_static/logo/tagkit-logo-dark.png" width="500">
    <img alt="Tagkit Logo" src="docs/source/_static/logo/tagkit-logo-light.png" width="500">
  </picture>
</div>

# Tagkit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/tagkit.svg)](https://pypi.org/project/tagkit/)

**Tagkit** is a Python toolkit and CLI for viewing and manipulating EXIF metadata in image files. It provides both a user-friendly command-line interface and a flexible Python API for programmatic access to EXIF data, with rich formatting options for photographers.

---

## Features

- View EXIF metadata for one or more images
- Filter by tag names or IDs
- Output as a rich table or JSON
- Handles binary EXIF data (bytes) with base64 encoding
- Photographer-friendly formatting for shutter speed, aperture, ISO, and more
- Extensible Python API for custom workflows

---

## Installation

### CLI

Invoke directly with [uvx](https://docs.astral.sh/uv/#tools)

```bash
uvx tagkit [command]
```

or install with uv, pipx, or pip

```bash
uv tool install tagkit
pipx install tagkit
pip install tagkit
```

### Python Package

Install in your project with pip or the package manager of your choice.

```bash
pip install tagkit
```

---

## CLI Usage

### View EXIF Data

```bash
tagkit view [OPTIONS] FILE_OR_PATTERN
```

#### Options

- `--glob`
  Use glob pattern matching for file selection.

- `--regex`
  Use regex pattern matching for file selection.

- `--tags TAGS`
  Comma-separated list of EXIF tag names or IDs to filter.

- `--thumbnail`
  Show EXIF tags from image thumbnails instead of the main image.

- `--json`
  Output EXIF data as JSON instead of a table.

#### Examples

```bash
# View EXIF data for a single image
tagkit view image.jpg

# View EXIF data for all JPGs in a folder
tagkit view "*.jpg" --glob

# Filter by specific tags
tagkit view image.jpg --tags Make,Model

# Output as JSON
tagkit view image.jpg --json
```

---

## API Usage

### Extract EXIF Data

```python
from tagkit import ExifImageCollection

# Get EXIF data for one or more images
exif_collection = ExifImageCollection(['image1.jpg', 'image2.jpg'], tag_filter=['Make', 'Model'])

# Access EXIF data for each file
for file_path, exif_image in exif_collection.files.items():
    print(f"File: {file_path}")
    for tag in exif_image.tags.values():
        print(f"  {tag.name}: {tag.formatted_value}")
```

### Working with ExifTag

```python
from tagkit.core.tag import ExifTag

tag = ExifTag(id=271, value="Canon", ifd="IFD0")
print(tag.name)             # e.g., "Make"
print(tag.exif_type)        # e.g., "ASCII"
print(tag.formatted_value)  # e.g., "Canon"
print(tag.as_dict())        # Dict representation
```

---

## Notes

- Any EXIF bytes that cannot be decoded as UTF-8 will be displayed as base64-encoded strings.
- Shutter speed, aperture, and ISO are formatted in a style familiar to photographers.
- The CLI and API are extensible for custom workflows and formatting.

---

## License

MIT

---

## Contributing

Pull requests and issues are welcome! Please see the code and tests for examples of usage and extension.
