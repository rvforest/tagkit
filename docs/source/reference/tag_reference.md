# EXIF Tag Reference

:::{note}
This page is automatically generated from the contents of `conf/registry.yaml` and lists all supported EXIF tags, their IDs, types, and IFD categories.
:::

---

## Tag Table

:::{note}
If the IFD is `Image`, it can refer to either `IFD0` (main image) or `IFD1` (thumbnail image).
:::

:::{note}
The `Type` column defines the type as specified by the [Exif 2.3 specification](https://www.cipa.jp/std/documents/e/DC-008-2012_E.pdf#page=30).

:::{hint} Tag descriptions
For detailed descriptions of EXIF tags, see the [Exif 2.3 specification](https://www.cipa.jp/std/documents/e/DC-008-2012_E.pdf#page=33).
:::

```{jinja} tag_reference
| IFD | Tag ID | Name | Type |
|-----|--------|------|------|
{% for ifd, tags in yaml.items() -%}
{% for tag_id, tag_info in tags.items() -%}
| {{ ifd }} | {{ tag_id }} | {{ tag_info.name }} | {{ tag_info.type }}
{% endfor %}
{%- endfor %}
```
