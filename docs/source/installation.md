# Installation Guide

## Prerequisites

Before installing tagkit, ensure you have the following:

- Python 3.8 or higher
- pip (Python package installer)

## Standard Installation

Invoke directly with [uvx](https://docs.astral.sh/uv/#tools)

```bash
uvx tagkit [command]
```

or install with uv, pipx, or pip

```bash
uv tool install tagkit
pipx install tagkit
pip install tagkit
```

## Development Installation

For development purposes, you can install tagkit with development dependencies:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tagkit.git
   cd tagkit
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   uv sync
   ```

## Verifying Installation

To verify that tagkit is installed correctly, run:

```bash
tagkit --version
# or
python -c "import tagkit; print(tagkit.__version__)"
```

This should print the version number of tagkit.

## Troubleshooting

If you encounter issues during installation:

- Ensure your Python version is 3.9 or higher
- Try upgrading pip: `pip install --upgrade pip`
- If you're behind a proxy, configure pip to use it
- Check for any error messages and search for solutions in the [FAQ](faq.md) or open an issue on the GitHub repository
