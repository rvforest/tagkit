# Contributing to tagkit

Thank you for your interest in contributing to tagkit! This guide will help you get started with contributing to the project.

## Setting Up Your Development Environment

### Prerequisites

- Python 3.9 or higher
- Git
- A GitHub account

### Fork and Clone the Repository

1. Fork the repository on GitHub by clicking the "Fork" button at the top right of the repository page.

2. Clone your fork to your local machine:
   ```bash
   git clone https://github.com/yourusername/tagkit.git
   cd tagkit
   ```

3. Add the original repository as an upstream remote:
   ```bash
   git remote add upstream https://github.com/originalowner/tagkit.git
   ```

### Create a Development Environment

1. Create and activate a virtual environment and install project and dev dependencies
   ```bash
   uv sync
   ```

## Development Workflow

### Creating a Branch

Create a new branch for your feature or bugfix:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bugfix-name
```

### Making Changes

1. Make your changes to the codebase.
2. Add tests for your changes.
3. Ensure all tests pass:
   ```bash
   nox -s tests
   ```
4. Check code quality:
   ```bash
   nox -s lint
   ```

### Committing Changes

1. Stage your changes:
   ```bash
   git add .
   ```

2. Commit your changes with a descriptive message:
   ```bash
   git commit -m "Add feature: your feature description"
   ```

3. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

### Creating a Pull Request

1. Go to the original repository on GitHub.
2. Click "Pull Requests" and then "New Pull Request".
3. Click "compare across forks" and select your fork and branch.
4. Fill out the pull request template with details about your changes.
5. Submit the pull request.

## Coding Standards

### Code Style

We use [Ruff](https://github.com/charliermarsh/ruff) for both code formatting (using Black-compatible rules) and linting. You can automatically format your code with:

```bash
nox -s format
```

And check for linting issues with:

```bash
nox -s lint
```

To check formatting without making changes:

```bash
nox -s format -- --check
```

### Type Hints

We use type hints throughout the codebase. Please add appropriate type hints to your code:

```python
def example_function(param1: str, param2: int) -> bool:
    """Example function with type hints."""
    return len(param1) > param2
```

### Documentation

All public functions, classes, and methods should have docstrings following the [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings):

```python
def example_function(param1: str, param2: int) -> bool:
    """Example function with Google style docstring.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    return len(param1) > param2
```

## Testing

### Writing Tests

We use [pytest](https://docs.pytest.org/) for testing. Place your tests in the `tests/` directory, mirroring the structure of the `src/` directory.

Example test:

```python
# tests/test_image_exif.py
import pytest
from tagkit.image_exif import read_exif

def test_read_exif():
    """Test reading EXIF data from an image."""
    # Setup
    test_image = "tests/data/test_image.jpg"

    # Execute
    tags = read_exif(test_image)

    # Assert
    assert "Make" in tags
    assert "Model" in tags
    assert tags["Make"] == "Example Camera"
```

### Running Tests

Run the test suite with:

```bash
nox -s tests
```

Or run specific tests with:

```bash
pytest tests/test_image_exif.py
```

### Test Coverage

Check coverage with:

```bash
nox -s coverage
```

## Documentation

### Building Documentation

Build the documentation locally with:

```bash
nox -s docs
```

The built documentation will be in the `docs/build/html/` directory.


### Previewing Documentation

You can preview the documentation by opening `docs/build/html/index.html` in your browser or by running:

```bash
python -m http.server -d docs/build/html
```

Then visit `http://localhost:8000` in your browser.


## Getting Help

If you need help with contributing to tagkit, you can:

- Open an issue on GitHub
- Reach out to the maintainers
- Join our community discussions

Thank you for contributing to tagkit!
