import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from tagkit.cli.main import app
from tagkit import __version__

runner = CliRunner()
test_dir = Path(__file__).parents[1]


# Use fixture for metadata
@pytest.fixture
def img_metadata():
    """Get the metadata from the metadata.json file"""
    metadata_path = test_dir / "io/test_images/metadata.json"

    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestMain:
    def test_version_option(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert result.output.strip() == __version__
