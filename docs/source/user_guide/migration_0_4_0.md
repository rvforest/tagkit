# Migrating to tagkit 0.4.0

Version 0.4.0 corrects the EXIF tag model and includes breaking changes before
1.0. This release does not establish a 1.0 API stability guarantee. Existing
scripts should check directory selection, tag collection access, and values
passed to low-level writes.

## Select the intended definition and directory

A tag occurrence is identified by its directory (IFD) and numeric tag ID.
The registry stores shared definitions identified by namespace and tag ID.
One definition can support multiple directories: the Image definition of
`Orientation` supports both `IFD0` (primary image) and `IFD1` (thumbnail).

Names and IDs that match multiple definitions raise `AmbiguousTagKey` unless
`ifd` disambiguates them. Previously, a lookup could silently select a match.
For example, numeric ID `1` identifies different tags in GPS and Interop.

Before, code might have omitted the directory:

```python
exif.write_tag(1, "N")
```

Use an explicit directory in 0.4.0:

```{testcode}
from tagkit import ExifImage
from tagkit.core.exceptions import AmbiguousTagKey

exif = ExifImage("image1.jpg")
try:
    exif.write_tag(1, "N")
except AmbiguousTagKey:
    pass
else:
    raise AssertionError("An ambiguous ID must require an IFD")

exif.write_tag(1, "N", ifd="GPS")
assert exif.read_tag(1, ifd="GPS") == "N"
```

This rule applies to low-level reads and deletes as well as writes. It is
based on registry definitions, even if only one matching tag is present in
the image.

If a key resolves to one definition and `ifd` is omitted, tagkit selects its
configured default directory. Image definitions normally default to `IFD0`;
Exif, GPS, and Interop definitions default to their namesake directories.
Pass `ifd="IFD1"` when you intend to access the thumbnail occurrence:

```{testcode}
thumbnail = ExifImage("migration_thumbnail.jpg")
assert thumbnail.read_tag("Orientation") == 1
assert thumbnail.read_tag("Orientation", ifd="IFD1") == 6
thumbnail.write_tag("Orientation", 3, ifd="IFD1")
assert thumbnail.read_tag("Orientation") == 1
assert thumbnail.read_tag("Orientation", ifd="IFD1") == 3
```

Single-tag operations target only the selected occurrence. A missing primary
value does not cause a fallback to the thumbnail, and defaults do not move
existing tags between directories.

## Preserve repeated tags when reading a collection of tags

The name-keyed `exif.tags` view raises `AmbiguousTagKey` when multiple
occurrences share a name. Code that iterated `exif.tags.items()` should use
`tag_entries` if it needs to handle every occurrence:

```{testcode}
try:
    thumbnail.tags
except AmbiguousTagKey:
    pass
else:
    raise AssertionError("The name view must reject repeated names")

entries = thumbnail.tag_entries
assert entries[("IFD0", 274)].value == 1
assert entries[("IFD1", 274)].value == 3
for (ifd, tag_id), tag in entries.items():
    print(ifd, tag_id, tag.name, tag.value)
assert "Orientation" not in thumbnail.as_dict()
assert "IFD0:Orientation" in thumbnail.as_dict()
assert "IFD1:Orientation" in thumbnail.as_dict()
```

`tag_entries` is a read-only mapping keyed by `(ifd, tag_id)`. Use `write_tag`
and `delete_tag` to change occurrences. The CLI table includes an IFD column;
JSON output and `as_dict()` preserve repeated names using keys such as
`IFD0:Orientation` and `IFD1:Orientation`. Unique names retain their usual keys.

## Supply EXIF-shaped values to low-level writes

`write_tag` checks known type, range, rational-shape, and count constraints
before replacing an in-memory value. Catch `tagkit.core.exceptions.ValidationError`
at the write call rather than waiting for `save()`. Errors include the tag name,
numeric ID, namespace, target IFD, expected constraints, and received value/type.

For example, replace a floating-point altitude with an explicit rational:

```python
# Before: this value could fail later during save().
exif.write_tag("GPSAltitude", 10.5)
```

```{testcode}
exif.write_tag("GPSAltitude", (105, 10))
assert exif.read_tag("GPSAltitude") == (105, 10)
```

A rational is a `(numerator, denominator)` pair of integers. A GPS coordinate
contains three such pairs, representing degrees, minutes, and seconds.
Lists are normalized to tuples, including nested lists, when the resulting
shape is valid:

```{testcode}
exif.write_tag("GPSLatitude", [[37, 1], [48, 1], [30, 1]])
assert exif.read_tag("GPSLatitude") == ((37, 1), (48, 1), (30, 1))
exif.write_tag("GPSLatitudeRef", "N")
```

ASCII tags take Python `str`, including `"N"` above, rather than `bytes`.
The backend handles encoding on save. Tagkit uses UTF-8 for text; fixed ASCII
counts measure encoded bytes plus the terminating NULL. Binary UNDEFINED
tags take `bytes`.

Fixed counts are enforced where declared: for example, `Orientation` requires
one component, `BitsPerSample` three, `YCbCrSubSampling` two, and
`ReferenceBlackWhite` six rationals. A rejected single-tag write leaves the
existing value unchanged:

```{testcode}
from tagkit.core.exceptions import ValidationError

original = thumbnail.read_tag("Orientation", ifd="IFD1")
try:
    thumbnail.write_tag("Orientation", (1, 2), ifd="IFD1")
except ValidationError as error:
    assert "IFD IFD1" in str(error)
else:
    raise AssertionError("Orientation must reject two components")
assert thumbnail.read_tag("Orientation", ifd="IFD1") == original
```

`write_tags` applies writes in order; an error can leave earlier successful
writes applied. It does not provide a transaction over the whole mapping.
Direct construction or mutation of `ExifTag.value` bypasses `write_tag`
validation; use the image write methods when you need these checks.

## Validation coverage and convenience helpers

The 0.4.0 baseline includes count/type definitions for tags used by the
test-image fixtures and documentation examples, plus the supported sequence
tags described above. Other registry entries can still have unspecified
counts. Tagkit validates their known type, range, and shape constraints but
skips unspecified count checks. An explicit `count: any` means a known variable
count; an omitted count means the constraint has not been modeled.

Low-level writes do not convert decimal coordinates to GPS rationals, floats
to rationals, or labels such as `"top-left"` to numeric enum values. Such
semantic conversions belong in convenience APIs. The existing
[datetime helpers](datetime.md) accept Python datetime values; a high-level
GPS API remains planned in [issue #4](https://github.com/rvforest/tagkit/issues/4).
Helper names suggested in design discussions do not imply availability.

## Save thumbnail changes explicitly

Writes change memory until `save()` is called. The default piexif backend
preserves an existing embedded JPEG thumbnail and its IFD1 tags during save:

```{testcode}
thumbnail.save()
reloaded = ExifImage("migration_thumbnail.jpg")
assert reloaded.read_tag("Orientation", ifd="IFD0") == 1
assert reloaded.read_tag("Orientation", ifd="IFD1") == 3
```

Saving IFD1 tags requires an embedded JPEG thumbnail. Without that payload,
`save()` raises `ValueError` before changing the file. Writing IFD1 tags alone
does not create a thumbnail.

See the [reading guide](reading.md) and [writing guide](writing.md) for the
full API workflows.
