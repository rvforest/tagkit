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
    render_bytes = False if binary_format is None else True

    table = Table(title="Exif Data")
    table.add_column("filename", style="cyan")
    table.add_column("id", style="magenta", no_wrap=True)
    table.add_column("name", style="magenta")
    table.add_column("value")

    for filename, tags in exif_data.files.items():
        is_first = True
        is_last = False
        for i, tag in enumerate(tags.tags.items()):
            if i == len(tags.tags.items()) - 1:
                is_last = True
            filename_val = filename if is_first else ""
            is_first = False
            row_data = [
                filename_val,
                tag[1].id,
                tag[1].name,
                tag[1].format(binary_format=binary_format),
            ]
            table.add_row(*[str(d) for d in row_data], end_section=is_last)

    console = Console()
    console.print(table)
