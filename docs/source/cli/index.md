# Command Line Interface

Tagkit provides a command-line interface (CLI) for viewing EXIF metadata in image files.

## Installation

Invoke directly with [uvx](https://docs.astral.sh/uv/#tools):

```bash
uvx tagkit [command]
```

Or install with uv, pipx, or pip:

```bash
uv tool install tagkit
pipx install tagkit
pip install tagkit
```

## Basic Usage

The CLI follows this pattern:

```bash
tagkit [global-options] view [options] FILE_OR_PATTERN
```

## View Command

View EXIF data for one or more image files:

```bash
tagkit view path/to/image.jpg
```

### Options

- `--glob`: Use glob pattern matching for file selection
- `--regex`: Use regex pattern matching for file selection
- `--tags TAG1,TAG2,...`: Comma-separated list of EXIF tag names or IDs to filter
- `--thumbnail`: Show EXIF tags from image thumbnails instead of main image
- `--json`: Output EXIF data as JSON instead of a table
- `--binary-format [bytes|hex|base64]`: How to format binary data (default: 'bytes')

### Examples

```bash
# View EXIF data for a single file
tagkit view photo.jpg

# View specific tags from multiple files using glob pattern
tagkit view --glob "*.jpg" --tags Make,Model,DateTimeOriginal

# View EXIF data as JSON
tagkit view --json photo.jpg

# View EXIF data from thumbnails
tagkit view --thumbnail photo.jpg

# Use regex pattern to match files
tagkit view --regex ".*\d{4}-\d{2}-\d{2}.*\.jpg"
```

## Global Options

- `--version`: Show the version and exit
- `--help`: Show help message and exit

## Error Handling

- If no files match the pattern, an error message will be displayed
- If EXIF data cannot be extracted, an error message will be shown
- A warning will be displayed if no EXIF data is found for the selected files
