# Working with DateTime Tags

This guide covers working with EXIF datetime tags using tagkit's high-level datetime API.

## Overview

EXIF images contain several datetime-related tags that store information about when photos were taken, modified, or digitized. Tagkit provides a user-friendly API for working with these datetime fields without needing to know the underlying EXIF tag IDs or structures.

## EXIF DateTime Tags

There are three primary datetime tags in EXIF:

1. **DateTimeOriginal** (tag 36867, Exif IFD) - The date and time when the original image was captured
2. **DateTimeDigitized** (tag 36868, Exif IFD) - The date and time when the image was digitized
3. **DateTime** (tag 306, IFD0) - The date and time when the image file was last modified

### Tag Precedence

When reading datetime information, tagkit uses the following precedence order:

1. **DateTimeOriginal** (preferred) - represents when the photo was taken
2. **DateTimeDigitized** (backup) - represents when the photo was digitized
3. **DateTime** (fallback) - represents last modification

This ensures that requesting a "primary" datetime returns the most relevant
value for a photo (DateTimeOriginal &gt; DateTimeDigitized &gt; DateTime).

## Basic Usage

### Getting Datetime from an Image

Use the `ExifImage` object to retrieve the primary datetime from an image:

```python
from tagkit import ExifImage

# Get the primary datetime (uses precedence order)
exif = ExifImage('photo.jpg')
dt = exif.get_datetime()
print(dt)  # 2025-05-01 14:30:00
```

### Setting Datetime

Use `ExifImage.set_datetime()` to set datetime values (the change is kept
in-memory; call `save()` to write the file):

```python
from datetime import datetime
from tagkit import ExifImage

exif = ExifImage('photo.jpg')
dt = datetime(2025, 6, 15, 10, 30, 0)

# Update all three datetime tags (DateTime, DateTimeOriginal, DateTimeDigitized)
exif.set_datetime(dt)
exif.save()

# Or update only a specific tag
exif.set_datetime(dt, tags=['DateTimeOriginal'])
exif.save()
```

### Getting All Datetime Tags

To read all present datetime tags from an image:

```python
from tagkit import ExifImage

exif = ExifImage('photo.jpg')
datetimes = exif.get_all_datetimes()
for tag_name, dt in datetimes.items():
    print(f"{tag_name}: {dt}")
```

## Advanced Operations

### Offsetting Datetime Values

Adjust datetime values by a timedelta with `ExifImage.offset_datetime()`:

```python
from datetime import timedelta
from tagkit import ExifImage

exif = ExifImage('photo.jpg')

# Add 2 hours to all datetime tags
exif.offset_datetime(timedelta(hours=2))
exif.save()

# Offset only the primary tag
exif.offset_datetime(timedelta(hours=2), tags=['DateTimeOriginal'])
exif.save()
```

### Bulk Operations

For multiple files use `ExifImageCollection` which provides collection-wide
helpers and a `save_all()` convenience method:

```python
from datetime import timedelta
from tagkit import ExifImageCollection

files = ['photo1.jpg', 'photo2.jpg', 'photo3.jpg']
collection = ExifImageCollection(files)

# Offset all images in memory and then persist
collection.offset_datetime(timedelta(hours=2))
collection.save_all()
```

### Finding Earliest or Latest Datetime

You can compute extrema from the per-tag datetimes returned by
`ExifImage.get_all_datetimes()`:

```python
from tagkit import ExifImage

exif = ExifImage('photo.jpg')
datetimes = exif.get_all_datetimes()
if datetimes:
    earliest = min(datetimes.values())
    latest = max(datetimes.values())
    print(f"Earliest: {earliest}")
    print(f"Latest: {latest}")
```

## EXIF-Specific Operations

For fine-grained control over specific datetime tags, pass a list of tag names
to the `tags` parameter on the `set_datetime` / `offset_datetime` methods.

```python
from datetime import datetime, timedelta
from tagkit import ExifImage

exif = ExifImage('photo.jpg')

# Read a specific tag
dt = exif.get_datetime(tag='DateTimeOriginal')

# Set only the DateTime tag
exif.set_datetime(datetime(2025, 6, 15, 10, 30, 0), tags=['DateTime'])
exif.save()

# Offset only DateTimeOriginal
exif.offset_datetime(timedelta(hours=2), tags=['DateTimeOriginal'])
exif.save()
```

### Parsing and Formatting

Utility helpers for parsing/formatting the EXIF string representation are
available from `tagkit.image.exif` and are re-exported at the package root:

```python
from datetime import datetime
from tagkit import parse_exif_datetime, format_exif_datetime

dt = parse_exif_datetime('2025:05:01 14:30:00')
print(format_exif_datetime(dt))  # '2025:05:01 14:30:00'
```

## Common Use Cases

### Correcting Camera Time

If your camera's clock was set incorrectly, offset the datetimes on the file:

```python
from datetime import timedelta
from tagkit import ExifImage

exif = ExifImage('photo.jpg')
exif.offset_datetime(timedelta(hours=-3))
exif.save()
```

### Timezone Adjustments

Convert a folder of images from one timezone to another with an
`ExifImageCollection`:

```python
from datetime import timedelta
from tagkit import ExifImageCollection
import glob

photos = glob.glob('vacation/*.jpg')
collection = ExifImageCollection(photos)
collection.offset_datetime(timedelta(hours=-5))
collection.save_all()
```

### Standardizing Datetime Tags

Use the primary datetime to set all datetime tags for an image:

```python
from tagkit import ExifImage

exif = ExifImage('photo.jpg')
dt = exif.get_datetime()
if dt:
    exif.set_datetime(dt)
    exif.save()
```

### Batch Processing with Error Handling

Use `ExifImageCollection` and handle exceptions at the script level. The
collection helpers operate in-memory; call `save_all()` to persist changes.

```python
from pathlib import Path
from datetime import timedelta
from tagkit import ExifImageCollection

photo_dir = Path('my_photos')
photos = [str(p) for p in photo_dir.glob('**/*.jpg')]

collection = ExifImageCollection(photos)
try:
    collection.offset_datetime(timedelta(hours=2))
    collection.save_all()
    print(f'Processed {len(photos)} files successfully')
except Exception as e:
    with open('errors.log', 'w') as f:
        f.write(str(e) + '\n')
    print('Errors occurred; see errors.log')
```

## Important Notes

### Timezone Handling

All datetime operations in tagkit are timezone-naive by default; returned
datetimes do not carry tzinfo. EXIF does have offset tags (OffsetTime*), but
they are not automatically applied by the high-level API at this time.

### DateTime Format

EXIF datetime strings use the format `YYYY:MM:DD HH:MM:SS` (note the colons).
The library exposes `parse_exif_datetime` and `format_exif_datetime` to convert
between this format and Python's `datetime` objects.

### File Modifications

All modifications are made in-memory on the `ExifImage` instance. Call
`save()` or `ExifImageCollection.save_all()` to write changes. You can create a
backup when saving using the `create_backup=True` flag on `save()`.

## Error Handling

`ExifImage` methods raise `DateTimeError` when an EXIF datetime string cannot be
parsed. IO-related errors such as `FileNotFoundError` or `IOError` are also
propagated so callers can handle them appropriately.

```python
from tagkit import ExifImage
from tagkit.core.exceptions import DateTimeError

exif = ExifImage('photo.jpg')
try:
    dt = exif.get_datetime()
except FileNotFoundError:
    print('Image file not found')
except DateTimeError as e:
    print(f'Invalid datetime format: {e}')
except IOError as e:
    print(f'Error reading image: {e}')
```

## API Reference

For complete API documentation, see the [API Reference](../reference/api.md).

### ExifImage (single-file API)

- `ExifImage.get_datetime(tag=None, use_precedence=True)` — Get the primary datetime
- `ExifImage.set_datetime(dt, tags=None)` — Set datetime values (in-memory)
- `ExifImage.get_all_datetimes()` — Get all datetime tags as a dict
- `ExifImage.offset_datetime(delta, tags=None)` — Offset datetimes (in-memory)
- `ExifImage.save(create_backup=False)` — Persist changes to disk

### ExifImageCollection (multi-file API)

- `ExifImageCollection.get_datetime(files=None, tag=None)` — Get datetimes for collection files
- `ExifImageCollection.set_datetime(dt, tags=None, files=None)` — Set datetimes across the collection (in-memory)
- `ExifImageCollection.offset_datetime(delta, tags=None, files=None)` — Offset datetimes across the collection (in-memory)
- `ExifImageCollection.save_all(create_backup=False)` — Save changes for all files

### Utilities

- `parse_exif_datetime(datetime_str)` — Parse an EXIF datetime string
- `format_exif_datetime(dt)` — Format a datetime as an EXIF string
