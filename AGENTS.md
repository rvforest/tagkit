# AGENTS.md

This file provides essential project information and development standards for coding agents working on the tagkit project.

## Project Overview

**tagkit** is a Python toolkit and CLI for viewing and manipulating EXIF metadata in image files. It provides both a user-friendly command-line interface and a flexible Python API for programmatic access to EXIF data, with rich formatting options for photographers.

- **Repository**: https://github.com/rvforest/tagkit
- **Documentation**: https://tagkit.readthedocs.io
- **License**: MIT
- **Python Version**: 3.9+
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

1. **Prerequisites**: Python 3.9+, Git, uv package manager
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
- **Checks**: All pre-commit hooks, tests across Python 3.9-3.13, coverage reporting

### Configuration Files

- **pyproject.toml**: Project metadata, dependencies, tool configuration
- **noxfile.py**: Task automation (testing, linting, docs, etc.)
- **cspell.json**: Spell checking configuration for documentation
- **.pre-commit-config.yaml**: Pre-commit hook configuration

## Making Changes

### Workflow for Agents

1. **Understanding**: Review existing code, tests, and documentation before making changes
2. **Minimal Changes**: Make the smallest possible changes to achieve the goal
3. **Testing**: Run relevant tests early and frequently
4. **Quality**: Ensure code passes all linting, formatting, and type checking
5. **Documentation**: Update docstrings and docs if changing public APIs

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
