from rich import print_json
from rich.console import Console
from rich.table import Table

from tagkit.exif_entry import ExifEntry


def to_serializable(val):
    """
    Recursively convert objects to types suitable for JSON serialization.

    - Any object with a to_dict() method is converted using that method.
    - Bytes values are displayed as base64-encoded strings if they cannot be decoded as UTF-8.
    - Lists and dicts are processed recursively.
    """
    if hasattr(val, "to_dict") and callable(val.to_dict):
        return to_serializable(val.to_dict())
    elif isinstance(val, dict):
        return {k: to_serializable(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [to_serializable(i) for i in val]
    else:
        return str(val)


def print_exif_json(exif_data):
    """
    Print EXIF data as JSON using rich formatting.

    Args:
        exif_data (dict): EXIF data to print.

    Notes:
        - Any bytes values in the EXIF data will be displayed as base64-encoded strings if they cannot be decoded as UTF-8.

    Example:
        >>> print_exif_json({"img.jpg": {256: ExifEntry(...)}})
    """
    data = to_serializable(exif_data)
    print_json(data=data)


def print_exif_table(exif_data: dict[str, dict[int, ExifEntry]]) -> None:
    """
    Print EXIF data as a formatted table using rich.

    Args:
        exif_data (dict[str, dict[int, ExifEntry]]): EXIF data to print.

    Notes:
        - Any bytes values in the EXIF data will be displayed as '<bytes>'

    Example:
        >>> print_exif_table({"img.jpg": {256: ExifEntry(...)}})
    """
    table = Table(title="Exif Data")
    table.add_column("filename", style="cyan")
    table.add_column("id", style="magenta", no_wrap=True)
    table.add_column("name", style="magenta")
    table.add_column("value", justify="right", style="green")  # , no_wrap=True)

    for filename, tags in exif_data.items():
        is_first = True
        is_last = False
        for i, tag in enumerate(tags.values()):
            if i == len(tags) - 1:
                is_last = True
            filename_val = filename if is_first else ""
            is_first = False
            row_data = [filename_val] + [tag.id, tag.name, tag.format(render_bytes=False)]
            row_data = [str(d) for d in row_data]
            table.add_row(*row_data, end_section=is_last)

    console = Console()
    console.print(table)
