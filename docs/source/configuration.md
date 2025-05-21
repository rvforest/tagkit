# Configuration Guide

Tagkit provides basic configuration options through its API. This document describes how to customize its behavior.

## Tag Value Formatting

Tagkit allows customization of how tag values are formatted when displayed. This is handled by the `TagValueFormatter` class.

### Creating a Formatter

```python
from pathlib import Path
from tagkit.value_formatting import TagValueFormatter

# Create a formatter with default configuration
formatter = TagValueFormatter({})


# Or load from a YAML configuration file
formatter = TagValueFormatter.from_yaml("path/to/format_config.yaml")
```

### Formatting Tag Values

```python
# Format a tag value
formatted_value = formatter.format(tag_entry)
```

## Tag Registry

Tagkit maintains a registry of known EXIF tags. The registry is loaded from a YAML file and can be accessed through the `tag_registry` module.

### Accessing Tag Information

```python
from tagkit import tag_registry

# Get all tag names
tag_names = tag_registry.tag_names

# Get tag ID by name
tag_id = tag_registry.get_tag_id("Make")

# Get tag name by ID
tag_name = tag_registry.get_tag_name(271)  # 271 is the ID for 'Make'

# Get EXIF type for a tag
exif_type = tag_registry.get_exif_type("Make")
```


## Next Steps

- Learn more about [working with EXIF data](tutorials/basic_exif_operations.md)
