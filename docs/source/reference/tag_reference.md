# EXIF Tag Reference

:::{note}
This page is automatically generated from the contents of `conf/registry.yaml` and lists all supported EXIF tags, their IDs, types, namespaces, and supported directories.
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
The `Type` column defines the type as specified by the [Exif 2.3 specification](https://www.cipa.jp/std/documents/e/DC-008-2012_E.pdf#page=30).

:::{hint} Tag descriptions
For detailed descriptions of EXIF tags, see the [Exif 2.3 specification](https://www.cipa.jp/std/documents/e/DC-008-2012_E.pdf#page=33).
:::

```{jinja} tag_reference
| Namespace | Tag ID | Name | Type | IFDs |
|-----------|--------|------|------|------|
{% for namespace, tags in yaml.items() -%}
{% for tag_id, tag_info in tags.items() -%}
| {{ namespace }} | {{ tag_id }} | {{ tag_info.name }} | {{ tag_info.type }} | {{ tag_info.ifds | join(", ") if tag_info.ifds is defined else ("IFD0, IFD1" if namespace == "Image" else namespace) }} |
{% endfor %}
{%- endfor %}
```
