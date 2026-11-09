# EXIF Tag Reference

:::{note}
This page is automatically generated from `conf/registry.yaml` and inventories tag definitions, their types, counts, namespaces, and supported directories.
:::

---

## Tag Table

:::{note}
`Image` is a shared tag namespace for `IFD0` (main image) and `IFD1` (thumbnail).
Individual definitions can restrict their supported directories. An omitted
`ifds` entry uses the namespace default: `IFD0, IFD1` for Image, or the namesake
directory for Exif, GPS, and Interop. These placements do not express every
compression-dependent rule in the EXIF standard.
:::

:::{note}
The `Type` column lists the types currently accepted by tagkit, not necessarily
every type permitted by a standard. The piexif backend chooses its own encoding
type, so permitting additional types in the registry alone would not guarantee
that they can be saved. Exif permits SHORT or LONG for ImageWidth, ImageLength,
StripOffsets, RowsPerStrip, StripByteCounts, PixelXDimension, and
PixelYDimension; the current backend writes these as LONG. Other TIFF and DNG
definitions remain in the registry for compatibility, but have not all been
audited against their respective specifications. Their presence does not imply
support for editing TIFF or DNG files.
:::

:::{hint} Tag descriptions
For detailed descriptions of EXIF tags, see the [Exif 2.3 specification](https://www.cipa.jp/std/documents/e/DC-008-2012_E.pdf#page=33).
:::

```{jinja} tag_reference
| Namespace | Tag ID | Name | Type | Count | IFDs |
|-----------|--------|------|------|-------|------|
{% for namespace, tags in yaml.items() -%}
{% for tag_id, tag_info in tags.items() -%}
| {{ namespace }} | {{ tag_id }} | {{ tag_info.name }} | {{ tag_info.type }} | {{ tag_info.count if tag_info.count is defined else "unspecified" }} | {{ tag_info.ifds | join(", ") if tag_info.ifds is defined else ("IFD0, IFD1" if namespace == "Image" else namespace) }} |
{% endfor %}
{%- endfor %}
```

## Count coverage and write policy

The table is the inventory of count coverage: `unspecified` means the count is
not modeled, while `any` records a variable count without enforcing possible
dependencies between tags. An integer is an enforced fixed count; a list gives
the allowed counts. The EXIF counts follow
[CIPA DC-X008-2019](https://www.cipa.jp/std/documents/e/DC-X008-Translation-2019-E.pdf),
sections 4.6.3–4.6.7. EXIF SubjectArea accepts 2, 3, or 4 values. StripOffsets and
StripByteCounts depend on image dimensions, rows per strip, and planar
configuration; their counts remain unspecified. Dependencies between tags are
not checked. Validating them would require a model of related tags and a policy
for incomplete images while callers make sequential writes.

Some Image counts follow the EXIF RGB profile rather than general TIFF. In
particular, BitsPerSample has count 3 and TransferFunction has count 768;
general TIFF permits other counts based on the number of samples and bit depth.
The fixed counts can therefore reject values valid in other TIFF profiles.

Definitions with unspecified counts remain writable for compatibility. Writes
still validate their declared type, numeric range, and value shape, but skip
the count check; this is partial validation, not a guarantee of standards
conformance. Writes to newly fixed-count definitions now reject values with
other counts that older versions accepted. Loaded values are not revalidated.
