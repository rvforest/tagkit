from typing import Optional

from rich import print_json
from rich.console import Console
from rich.table import Table

from tagkit import ExifImageCollection


def to_serializable(val, binary_format: Optional[str] = None):
    """
    Recursively convert objects to types suitable for JSON serialization.

    - Any object with an as_dict() method is converted using that method.
    - Bytes values are formatted according to binary_format if they cannot be decoded as UTF-8.
    - Lists and dicts are processed recursively.

    Args:
        val: The value to convert
        binary_format: How to format binary data - 'bytes' (default), 'hex', or 'base64'.
    """
    if hasattr(val, "as_dict") and callable(val.as_dict):
        return to_serializable(val.as_dict(binary_format=binary_format), binary_format)
    elif isinstance(val, dict):
        return {k: to_serializable(v, binary_format) for k, v in val.items()}
    elif isinstance(val, list):
        return [to_serializable(i, binary_format) for i in val]
    else:
        return str(val)


def print_exif_json(
    exif_data: ExifImageCollection, binary_format: Optional[str] = None
):
    """
    Print EXIF data as JSON using rich formatting.

    Args:
        exif_data: EXIF data to print.
        binary_format: How to format binary data - 'bytes' (default), 'hex', or 'base64'.
    """
    print_json(data=exif_data.as_dict(binary_format=binary_format))


def print_exif_table(
    exif_data: ExifImageCollection, binary_format: Optional[str] = None
) -> None:
    """
    Print EXIF data as a formatted table using rich.

    Args:
        exif_data: EXIF data to print.
        binary_format: How to format binary data - 'bytes' (default), 'hex', or 'base64'.
    """
    table = Table(title="Exif Data")
    table.add_column("filename", style="cyan")
    table.add_column("ifd", style="magenta", no_wrap=True)
    table.add_column("id", style="magenta", no_wrap=True)
    table.add_column("name", style="magenta")
    table.add_column("value")

    for filename, tags in exif_data.files.items():
        entries = tags.tag_entries
        for i, tag in enumerate(entries.values()):
            row_data = [
                filename if i == 0 else "",
                tag.ifd,
                tag.id,
                tag.name,
                tag.format(binary_format=binary_format),
            ]
            table.add_row(
                *[str(d) for d in row_data], end_section=i == len(entries) - 1
            )

    console = Console()
    console.print(table)
