# Command Line Interface

Tagkit provides a command-line interface (CLI) for viewing EXIF metadata in image files.

## Basic Usage

The CLI follows this pattern:

```bash
tagkit [global-options] view [options] FILE_OR_PATTERN
```

## Global Options

- `--version`: Show the version and exit
- `--help`: Show help message and exit

## Error Handling

- If no files match the pattern, an error message is displayed.
- If EXIF data cannot be extracted, an error message is shown.
- If no EXIF data is found for the selected files, a warning is displayed.

## Commands

- **[view](./reading.md)**: Reads all or selected tags from one or more images.
