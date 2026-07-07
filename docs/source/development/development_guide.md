# Development Guide

> For contribution workflow, coding standards, and testing instructions, see [contributing.md](contributing.md).

This guide provides detailed information for developers working on or extending the tagkit library.

## Architecture Overview

Tagkit is organized into several core components:

### Core Components

The `core/` modules provide the foundational logic: tag representation, registry, formatting, types, and utilities.

- `core/tag.py`: Defines the `ExifTag` class, representing a single EXIF tag entry with its ID, value, and IFD location.
- `core/registry.py`: Manages the registry of known EXIF tags and their properties via the `ExifRegistry` class and config from `conf/registry.yaml`.
- `core/formatting.py`: Handles formatting and parsing of tag values using the `ValueFormatter` class
  and config from `conf/formatting.yaml`.
- `core/utils.py`: Common utility functions
- `core/types.py`: Type definitions
- `core/exceptions.py`: Custom exceptions

### Image Handling

The `image/` modules use the core logic to provide high-level EXIF image handling and batch operations.

- `image/exif.py`: The primary interface for working with EXIF data in images. It provides the `ExifImage` class for reading, writing, and manipulating EXIF tags.
- `image/collection.py`: Provides classes for batch operations on multiple images.

### I/O System

The `tag_io/` modules implement backends for reading and writing EXIF bytes data. The default is `piexif`, but custom classes can be added by subclassing the base classes.

- `tag_io/`: Contains readers and writers for different formats
- `tag_io/base.py`: Base classes for tag I/O
- `tag_io/piexif_io.py`: Piexif backend for EXIF I/O

### CLI

The `cli/` modules provide the command-line interface, using the core and image APIs.

- `cli/`: Command-line interface components
- `cli/main.py`: CLI entry point
- `cli/commands.py`: CLI commands
- `cli/view.py`, `cli/cli_formatting.py`: CLI utilities

### Configuration

The `conf/` directory contains configuration and registry YAML files used by the registry and formatting logic.

- `conf/config.py`: Configuration management
- `conf/registry.yaml`: Tag registry configuration
- `conf/formatting.yaml`: Value formatting configuration

### Code Organization

```text
src/tagkit/
├── __init__.py
├── cli/
│   ├── __init__.py
│   ├── main.py
│   ├── commands.py
│   ├── view.py
│   └── cli_formatting.py
├── conf/
│   ├── __init__.py
│   ├── config.py
│   ├── registry.yaml
│   └── formatting.yaml
├── core/
│   ├── __init__.py
│   ├── exceptions.py
│   ├── formatting.py
│   ├── registry.py
│   ├── tag.py
│   ├── types.py
│   └── utils.py
├── image/
│   ├── __init__.py
│   ├── exif.py
│   └── collection.py
├── tag_io/
│   ├── __init__.py
│   ├── base.py
│   └── piexif_io.py
└── py.typed
```

## Extending Tagkit

### Adding New Tags

To add support for a new tag:

1. Update the tag registry configuration in `conf/registry.yaml`, including
   the tag name, EXIF type or allowed types, and count metadata when the tag is
   writable or otherwise validated.
2. If needed, add custom formatting in `core/formatting.py` and register it in the configuration (`conf/formatting.yaml`).

## Testing

- Unit tests are in `tests/core/`, `tests/image/`, `tests/tag_io/`, and `tests/cli/`.

## API Stability

- After the version 1 release, public API functions and classes are stable within a
  major version.
- For version 0, all functions and classes may change between minor versions.
- Internal modules (prefixed with underscore) may change between minor versions.

## Documentation

- Use Google-style docstrings for all public APIs.
- Build documentation with Sphinx: `nox -s docs`

## Resources

- [EXIF Specification](https://www.cipa.jp/std/documents/e/DC-X008-Translation-2019-E.pdf)
