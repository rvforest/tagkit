# Command Line Interface

Tagkit provides a powerful command-line interface (CLI) for working with image metadata without writing code.

## Installation

The CLI is automatically installed when you install tagkit:

```bash
pip install tagkit
```

## Basic Usage

The CLI follows this general pattern:

```bash
tagkit [command] [options] [arguments]
```

## Available Commands

### read

Read EXIF tags from an image file:

```bash
tagkit read path/to/image.jpg
```

Options:
- `--tags TAG1,TAG2,...`: Only display specific tags
- `--format [json|yaml|table]`: Output format (default: table)
- `--output FILE`: Save output to a file instead of printing to console

Examples:
```bash
# Read all tags in table format
tagkit read photo.jpg

# Read only specific tags in JSON format
tagkit read photo.jpg --tags Make,Model,DateTimeOriginal --format json

# Save output to a file
tagkit read photo.jpg --output metadata.json --format json
```

### write

Write EXIF tags to an image file:

```bash
tagkit write path/to/image.jpg --tag TAG=VALUE
```

Options:
- `--tag TAG=VALUE`: Tag and value to write (can be used multiple times)
- `--from-file FILE`: Read tags from a JSON or YAML file
- `--backup`: Create a backup of the original image

Examples:
```bash
# Write a single tag
tagkit write photo.jpg --tag Artist="Jane Doe"

# Write multiple tags
tagkit write photo.jpg --tag Artist="Jane Doe" --tag Copyright="© 2025"

# Write tags from a file
tagkit write photo.jpg --from-file metadata.json --backup
```

### list-tags

List all available EXIF tags:

```bash
tagkit list-tags
```

Options:
- `--category CATEGORY`: Filter tags by category
- `--format [json|yaml|table]`: Output format (default: table)

Examples:
```bash
# List all available tags
tagkit list-tags

# List only camera-related tags
tagkit list-tags --category Camera

# Output in JSON format
tagkit list-tags --format json
```

### batch

Process multiple images at once:

```bash
tagkit batch [command] [options] [path/pattern]
```

Options:
- `--recursive`: Process images in subdirectories
- `--dry-run`: Show what would be done without making changes

Examples:
```bash
# Read EXIF data from all JPG files in current directory
tagkit batch read *.jpg

# Write the same tags to all images in a directory and its subdirectories
tagkit batch write --tag Artist="Jane Doe" --recursive ./vacation_photos/

# Remove GPS data from all images in a directory
tagkit batch remove --tags GPS* ./vacation_photos/
```

### remove

Remove specific EXIF tags from an image:

```bash
tagkit remove path/to/image.jpg --tags TAG1,TAG2,...
```

Options:
- `--tags TAG1,TAG2,...`: Tags to remove (supports wildcards)
- `--backup`: Create a backup of the original image

Examples:
```bash
# Remove GPS data
tagkit remove photo.jpg --tags GPS*

# Remove multiple specific tags with backup
tagkit remove photo.jpg --tags Make,Model,Software --backup
```

## Global Options

These options can be used with any command:

- `--verbose`: Show detailed output
- `--quiet`: Suppress all output except errors
- `--help`: Show help for a command
- `--version`: Show tagkit version

## Examples

### Complete Workflow Example

```bash
# 1. Read the original metadata
tagkit read original.jpg --output original_metadata.json --format json

# 2. Edit the metadata file (manually or with other tools)

# 3. Write the edited metadata back to the image
tagkit write original.jpg --from-file edited_metadata.json --backup

# 4. Verify the changes
tagkit read original.jpg --format table
```

## Next Steps

- See the [CLI Tutorials](../tutorials/cli_advanced.md) for more advanced usage
- Learn about [batch processing](../tutorials/batch_processing.md) with the CLI
- Check the [Configuration Guide](../configuration.md) for customizing CLI behavior
