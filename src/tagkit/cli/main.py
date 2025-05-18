import typer
from tagkit import __version__
from tagkit.cli.view import view

app = typer.Typer()


def version_callback(value: bool):
    if value:
        print(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        help="Show the version and exit.",
        is_eager=True,
        callback=version_callback,
    ),
):
    """
    Tagkit: A CLI tool for viewing and manipulating EXIF metadata in image files.
    Run with --help for more info.
    """
    pass


app.command()(view)
