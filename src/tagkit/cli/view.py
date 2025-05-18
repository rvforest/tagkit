from typing import Optional
import typer
import re
from tagkit.cli.file_resolver import FileResolver
from tagkit.cli.cli_formatting import print_exif_json, print_exif_table
from tagkit.operations import get_exif
from tagkit.cli.cli_utils import tag_ids_to_int


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
):
    """
    View EXIF data for one or more image files. Supports filtering by tag and output as table or JSON.

    Notes:
        - Any bytes values in EXIF data will be displayed as base64-encoded strings if they cannot be decoded as UTF-8, both in table and JSON output.
    """
    tag_filter = tag_ids_to_int(tags)
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
        exif_data = get_exif(resolver.files, tag_filter=tag_filter, thumbnail=thumbnail)
    except Exception as e:
        typer.secho(
            f"[ERROR] Failed to extract EXIF data: {e}", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=2)
    # Show warning if there are no tags for any file
    if not exif_data or all(not tags for tags in exif_data.values()):
        typer.secho(
            "[WARNING] No EXIF data found for the selected files.",
            fg=typer.colors.YELLOW,
        )
    if json:
        print_exif_json(exif_data)
    else:
        print_exif_table(exif_data)
