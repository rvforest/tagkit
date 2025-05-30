"""Set up doctest fixtures.

This file contains fixtures that are needed for doctests.
Test-specific fixtures are in tests/conftest.py.
"""

from pathlib import Path

import pytest

from tests.conftest import create_test_images_from_metadata


@pytest.fixture(autouse=True)
def doctest_files(doctest_namespace, tmp_path):
    """Create JPG test files specifically for doctests."""
    # Path to the doctest metadata file
    here = Path(__file__).parent.resolve()
    metadata_path = here / "tests/conf/doctest-img-metadata.json"

    # Create test images from the doctest metadata
    img_dir = tmp_path / "doctest_images"
    create_test_images_from_metadata(img_dir, metadata_path)

    # Create a text file
    (img_dir / "foo.txt").touch()

    # Add to doctest namespace
    doctest_namespace["img_dir"] = str(img_dir)
