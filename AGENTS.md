# AGENTS.md

This file provides essential project information and development standards for coding agents working on the tagkit project.

## Project Overview

**tagkit** is a Python toolkit and CLI for viewing and manipulating EXIF metadata in image files. It provides both a user-friendly command-line interface and a flexible Python API for programmatic access to EXIF data, with rich formatting options for photographers.

- **Repository**: https://github.com/rvforest/tagkit
- **Documentation**: https://tagkit.readthedocs.io
- **License**: MIT
- **Python Version**: 3.10+
- **Main Dependencies**: piexif, pyyaml, rich, typer

## Architecture Overview

The project is organized into several core components:

### Directory Structure

```text
src/tagkit/
├── __init__.py
├── cli/                    # Command-line interface components
│   ├── main.py            # CLI entry point
│   ├── commands.py        # CLI commands
│   ├── view.py            # CLI view utilities
│   └── cli_formatting.py  # CLI formatting utilities
├── conf/                  # Configuration and registry files
│   ├── config.py          # Configuration management
│   ├── registry.yaml      # Tag registry configuration
│   └── formatting.yaml    # Value formatting configuration
├── core/                  # Core components and business logic
│   ├── exceptions.py      # Custom exceptions
│   ├── formatting.py      # Tag value formatting
│   ├── registry.py        # Tag registry management
│   ├── tag.py            # EXIF tag representation
│   ├── types.py          # Type definitions
│   └── utils.py          # Utility functions
├── image/                 # Image handling components
│   ├── exif.py           # EXIF data extraction
│   └── collection.py     # Image collections
└── tag_io/               # I/O system for reading/writing tags
    ├── base.py           # Base I/O classes
    └── piexif_io.py      # piexif backend implementation
```

### Key Components

- **Core**: Business logic for tag handling, registry management, and formatting
- **Image**: EXIF data extraction and image collection management
- **I/O System**: Pluggable backend for reading/writing EXIF data (currently uses piexif)
- **CLI**: Command-line interface built with typer and rich
- **Configuration**: YAML-based configuration for tag registry and formatting

## Development Standards

### Development Environment Setup

1. **Prerequisites**: Python 3.10+, Git, uv package manager
2. **Setup**: Run `uv sync` to create virtual environment and install dependencies
3. **Workflow**: Create feature branches, make changes, test, commit, and open PRs

### Code Quality Standards

#### Code Style and Formatting
- **Tool**: Ruff (Black-compatible formatting + linting)
- **Commands**:
  - Format code: `uv run nox -s format`
  - Check linting: `uv run nox -s lint`
  - Check all: `uv run nox -s check`

#### Type Hints
- **Required**: All public functions, classes, and methods must have type hints
- **Tool**: mypy for static type checking
- **Command**: `uv run nox -s types`

#### Documentation
- **Style**: Google-style docstrings for all public APIs
- **Tool**: Sphinx with autodoc2, myst_parser extensions
- **Commands**:
  - Build docs: `uv run nox -s docs`
  - Live docs: `uv run nox -s livedocs`

#### Naming Conventions

The codebase follows a consistent naming convention for tag-related parameters:

- **`tag_key: Union[int, str]`**: Single tag identifier that may be either a tag name (str) or tag ID (int)
  - Used in: `read_tag()`, `write_tag()`, `delete_tag()`, `get_ifd()`, `resolve_tag_id()`, `resolve_tag_name()`
  - Example: `exif.read_tag('Make')` or `exif.read_tag(271)`

- **`tag_keys: Iterable[Union[int, str]]`**: Sequence of tag identifiers (names or IDs)
  - Used in: `read_tags()`, `delete_tags()`
  - Example: `exif.read_tags(['Make', 'Model'])` or `exif.delete_tags([271, 272])`

- **`tags: dict[Union[int, str], Value]`**: Mapping from tag identifiers to values
  - Used in: `write_tags()`
  - Example: `exif.write_tags({'Artist': 'Jane', 'Copyright': '2025 John'})`

- **Other existing names remain unchanged**: `ifd`, `files`, `tag_filter`, etc.

This convention makes it explicit that parameters accept both numeric IDs and textual names, improving API clarity and consistency.

### Testing Standards

#### Framework and Coverage
- **Framework**: pytest
- **Coverage**: pytest-cov
- **Commands**:
  - Run tests: `uv run nox -s tests`
  - Coverage report: `uv run nox -s coverage`
  - Doctests: `uv run nox -s doctest_docs`

#### Test Organization
- Tests are organized in `tests/` directory, mirroring `src/` structure
- Unit tests for each component: `core/`, `image/`, `tag_io/`, `cli/`
- Test configuration in `tests/conf/` with metadata for generating test images
  - `test-img-metadata.json`: Generates images for pytest unit/integration tests
  - `doctest-img-metadata.json`: Generates images for documentation examples and API docstrings
  - Images are created via `create_test_images_from_metadata` function in `tests/conftest.py`

### Pre-commit Hooks and CI

#### Pre-commit Hooks
- **Enabled**: Ruff linting/formatting, mypy type checking, yaml validation
- **Spell checking**: cspell for Markdown files only
- **Security**: detect-secrets for credential scanning
- **Setup**: Automatically configured with uv sync

#### Continuous Integration
- **Platform**: GitHub Actions
- **Checks**: All pre-commit hooks, tests across Python 3.10-3.14, coverage reporting

### Configuration Files

All configuration files use Pydantic for validation:

- **pyproject.toml**: Project metadata, dependencies, tool configuration
- **noxfile.py**: Task automation (testing, linting, docs, etc.)
- **cspell.json**: Spell checking configuration for documentation
- **.pre-commit-config.yaml**: Pre-commit hook configuration
- **src/tagkit/conf/registry.yaml**: EXIF tag registry (validated by `RegistryConfig` model)
- **src/tagkit/conf/formatting.yaml**: Tag formatting rules (validated by `FormattingConfig` model)
- **tests/conf/test-img-metadata.json**: Test image metadata (validated by `ImageMetadataConfig` model)
- **tests/conf/doctest-img-metadata.json**: Doctest image metadata (validated by `ImageMetadataConfig` model)

Pydantic models are defined in `src/tagkit/conf/models.py` and provide type-safe validation with clear error messages.

## Making Changes

### Workflow for Agents

1. **Understanding**: Review existing code, tests, and documentation before making changes
2. **Minimal Changes**: Make the smallest possible changes to achieve the goal
3. **Testing**: Run relevant tests early and frequently
4. **Quality**: Ensure code passes all linting, formatting, and type checking
5. **Documentation**: Update docstrings and docs if changing public APIs

### Guidance for coding agents: test-image metadata schema

This repository includes machine-readable validation for the JSON files used to generate test images (`tests/conf/test-img-metadata.json` and `tests/conf/doctest-img-metadata.json`). When working on features or docs that add or change test images, follow these steps:

- Edit or add image metadata only in `tests/conf/test-img-metadata.json` (for pytest) or `tests/conf/doctest-img-metadata.json` (for doctests).
- The repository uses Pydantic models in `src/tagkit/conf/models.py` to validate configuration structure. Use these models to ensure new entries match the required structure.
- A pytest (`tests/test_conf_schemas.py`) validates both config files using Pydantic models in CI. Run this test locally after changes.

Quick local validation:

```bash
uv run pytest tests/test_conf_schemas.py -q
```

If you (the agent) modify the Pydantic models, update the pytest and the human-friendly summary in `docs/source/development/contributing.md`.

### Common Commands

```bash
# Setup development environment
uv sync

# Run all quality checks
uv run nox -s check

# Run tests
uv run nox -s tests

# Build documentation
uv run nox -s docs

# Format and lint code
uv run nox -s format
uv run nox -s lint
```

### Important Notes

- **Spell checking**: Only Markdown files are spell-checked; add technical terms to `cspell.json`
- **API stability**: Public APIs are stable within major versions (after v1.0)
- **Extensibility**: The system is designed to be extensible (new tags, formatters, I/O backends)
- **Backwards compatibility**: Maintain compatibility when making changes to public APIs
- **Documentation examples**: All docstring and documentation examples must use image files defined in `tests/conf/doctest-img-metadata.json`. If you need a new example image with specific EXIF metadata, add it to this config file first before referencing it in documentation or docstrings. This ensures examples are reproducible and stable across documentation builds and doctest runs.

## Resources

- **EXIF Specification**: https://www.cipa.jp/std/documents/e/DC-X008-Translation-2019-E.pdf
- **Contributing Guide**: `docs/source/development/contributing.md`
- **Development Guide**: `docs/source/development/development_guide.md`
- **Documentation**: https://tagkit.readthedocs.io

## Contact

For questions or issues, open an issue on GitHub or refer to the contributing guidelines.
