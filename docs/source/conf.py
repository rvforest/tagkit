# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from textwrap import dedent
from pathlib import Path

import yaml

project = "tagkit"
copyright = "2025, Robert Forest"
author = "Robert Forest"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "autodoc2",
    "myst_parser",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx_jinja",  # Enable Jinja2 templating in Markdown
]
myst_enable_extensions = [
    "colon_fence",
]
autodoc2_packages = [
    "../../src/tagkit",
]

# doctest settings
doctest_test_doctest_blocks = ""
doctest_global_setup = dedent(
    """
    import os
    import sys
    import tempfile
    from pathlib import Path

    sys.path.append(".")
    from conftest import create_test_images_from_metadata

    metadata_path = "./tests/conf/doctest-img-metadata.json"

    # Create test images from the doctest metadata
    img_dir = Path(tempfile.mkdtemp()) / "doctest_images"
    create_test_images_from_metadata(img_dir, metadata_path)

    original_dir = os.getcwd()
    os.chdir(img_dir)

    # Create a dummy print function to avoid needing to check outputs with doctest.
    # doctest is just being used to ensure examples run without error.
    def print(*args, **kwargs):
        pass
    """
)
doctest_global_cleanup = dedent(
    """
    import os
    import shutil

    os.chdir(original_dir)
    shutil.rmtree(img_dir)
    """
)

templates_path = ["_templates"]
exclude_patterns = []  # type: ignore

autosummary_generate = True

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'sphinx_rtd_theme'
html_theme = "furo"
html_static_path = ["_static"]
html_theme_options = {
    "light_logo": "logo/tagkit-logo-light.png",
    "dark_logo": "logo/tagkit-logo-dark.png",
}

# Favicon configuration
html_favicon = "_static/logo/favicon.png"


def load_yaml_file(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


jinja_contexts = {
    "tag_reference": {
        "yaml": load_yaml_file(
            str(Path(__file__).parents[2] / "src" / "tagkit" / "conf" / "registry.yaml")
        )
    }
}
