from typing import Optional
import typer
import re
from tagkit.cli.file_resolver import FileResolver
from tagkit.cli.cli_formatting import print_exif_json, print_exif_table
from tagkit import ExifImageCollection


def view(
    file_or_pattern: str = typer.Argument(
        ..., help="A file path, glob, or regex pattern to match image files."
    ),
    glob_mode: bool = typer.Option(
        False, "--glob", help="Use glob pattern matching for file selection."
    ),
    regex_mode: bool = typer.Option(
        False, "--regex", help="Use regex pattern matching for file selection."
    ),
    tags: Optional[str] = typer.Option(
        None, "--tags", help="Comma separated list of EXIF tag names or IDs to filter."
    ),
    thumbnail: bool = typer.Option(
        False,
        "--thumbnail",
        help="Show EXIF tags from image thumbnails instead of main image.",
    ),
    json: bool = typer.Option(
        False, "--json", help="Output EXIF data as JSON instead of a table."
    ),
    binary_format: Optional[str] = typer.Option(
        None,
        "--binary-format",
        help="How to format binary data: 'bytes' (default), 'hex', or 'base64'.",
        case_sensitive=False,
    ),
):
    """
    View EXIF data for one or more image files. Supports filtering by tag and output as table or JSON.
    """
    # Note: tag filtering is no longer supported directly with ImageCollection
    # If needed, tag filtering should be implemented separately
    try:
        resolver = FileResolver(file_or_pattern, glob_mode, regex_mode)
    except re.error as e:
        typer.secho(
            f"[ERROR] Invalid regular expression: {e}", fg=typer.colors.RED, err=True
        )
        typer.secho(
            "Please check your pattern for typos or unbalanced brackets.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=2)
    if not resolver.files:
        typer.secho(
            "[ERROR] No files matched the given pattern.", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1)

    try:
        exif_data = ExifImageCollection(resolver.files)
    except Exception as e:
        typer.secho(
            f"[ERROR] Failed to extract EXIF data: {e}", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=2)
    # Show warning if there are no tags for any file
    if exif_data.n_tags == 0:
        typer.secho(
            "[WARNING] No EXIF data found for the selected files.",
            fg=typer.colors.YELLOW,
        )
    if json:
        print_exif_json(exif_data, binary_format=binary_format)
    else:
        print_exif_table(exif_data, binary_format=binary_format)
