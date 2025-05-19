# Usage Guide

Welcome to **tagkit**! This guide will help you get started.

## Installation

```sh
pip install tagkit
```

## Basic Usage

### Reading EXIF Tags from an Image

```python
from tagkit.image_exif import read_exif

tags = read_exif('example.jpg')
print(tags)
```

### Writing EXIF Tags to an Image

```python
from tagkit.image_exif import write_exif

write_exif('example.jpg', {'Author': 'Alice'})
```

### Using the CLI

```sh
tagkit read example.jpg
tagkit write example.jpg --tag Author=Alice
```

## Tag Registry

```python
from tagkit.tag_registry import TagRegistry

registry = TagRegistry()
print(registry.list_tags())
```

For more details, see the API Reference below.
