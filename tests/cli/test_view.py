import os
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from tagkit.cli.main import app
from tagkit import ExifImage

runner = CliRunner()
test_dir = Path(__file__).parents[1]


def always_fail(*args, **kwargs):
    raise Exception("fail!")


def always_empty(*args, **kwargs):
    return {}


# Use fixture for metadata
@pytest.fixture
def img_metadata():
    """Get the metadata from the metadata.json file"""
    metadata_path = test_dir / "io/test_images/metadata.json"

    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestViewCommand:
    @pytest.mark.parametrize("json_output", [False, True])
    def test_view_preserves_duplicate_tag_names(
        self, test_images, monkeypatch, json_output
    ):
        path = test_images / "minimal.jpg"
        image = ExifImage(path)
        image.write_tag("Orientation", 1, ifd="IFD0")
        image.write_tag("Orientation", 6, ifd="IFD1")
        image.write_tag("UserComment", b"\xff\x00")
        tags = {(tag_id, ifd): tag for (ifd, tag_id), tag in image.tag_entries.items()}
        monkeypatch.setattr(
            "tagkit.tag_io.piexif_io.PiexifBackend.load_tags",
            lambda self, file_path: tags,
        )
        monkeypatch.delenv("FORCE_COLOR", raising=False)
        monkeypatch.setenv("COLUMNS", "160")
        options = ["--json"] if json_output else []

        result = runner.invoke(
            app, ["view", str(path), *options, "--binary-format", "hex"]
        )

        assert result.exit_code == 0, result.exception
        if json_output:
            data = json.loads(result.output)["minimal.jpg"]
            assert data["IFD0:Orientation"] == {
                "id": 274,
                "value": "Top-left",
                "ifd": "IFD0",
            }
            assert data["IFD1:Orientation"] == {
                "id": 274,
                "value": "Right-top",
                "ifd": "IFD1",
            }
            assert data["Make"]["value"] == "TestMake"
            assert data["UserComment"]["value"] == "hex:ff00"
            assert len(data) == len(tags)
        else:
            lines = result.output.splitlines()
            assert "ifd" in lines[2]
            orientation_rows = [line for line in lines if "Orientation" in line]
            assert len(orientation_rows) == 2
            assert "IFD0" in orientation_rows[0]
            assert "IFD1" in orientation_rows[1]
            assert "hex:ff00" in result.output

    def test_view(self, test_images):
        """Make sure view command runs and prints something in table view.
        Don't check exact number of lines to make maintainability easier.
        """
        min_number_lines = 19

        result = runner.invoke(app, ["view", str(test_images) + "/*.jpg"])
        output_lines = result.output.splitlines()

        assert result.exit_code == 0, result.output
        assert "Exif Data" in output_lines[0]

        assert len(output_lines) >= min_number_lines

    def test_view_no_files(self):
        result = runner.invoke(app, ["view", "no_such_file_123456789.jpg"])
        assert result.exit_code == 1
        assert "No files matched the given pattern" in result.output

    def test_view_both_glob_and_regex(self):
        result = runner.invoke(app, ["view", "*.jpg", "--glob", "--regex"])
        assert result.exit_code != 0
        assert "Cannot specify both" in result.output

    def test_view_invalid_pattern(self):
        # This test assumes get_exif or file resolver will raise an error for an invalid regex
        result = runner.invoke(app, ["view", "[", "--regex"])
        assert result.exit_code != 0
        assert (
            "Failed to extract EXIF data" in result.output
            or "error" in result.output.lower()
        )

    def test_view_json(self, test_images):
        """Test that --json outputs valid JSON and includes expected EXIF data keys."""
        os.environ.pop("FORCE_COLOR", None)
        result = runner.invoke(app, ["view", str(test_images) + "/*.jpg", "--json"])
        assert result.exit_code == 0, result.output
        # The output should be valid JSON
        try:
            data = json.loads(result.output)
        except Exception as e:
            pytest.fail(f"Output is not valid JSON: {e}\nOutput: {result.output}")
        # There should be at least one file key in the output
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_view_exif_extraction_error(self, tmp_path, monkeypatch):
        # Create a dummy file that exists
        dummy_file = tmp_path / "dummy.txt"
        dummy_file.write_text("not an image")

        # Patch ExifImageCollection to raise an Exception
        monkeypatch.setattr(
            "tagkit.ExifImageCollection",
            always_fail,
        )

        result = runner.invoke(app, ["view", str(dummy_file)])
        assert result.exit_code == 2
        assert "Failed to extract EXIF data" in result.output

    def test_view_no_exif_data_warning(self, tmp_path, monkeypatch):
        # Create a dummy file that exists
        dummy_file = tmp_path / "dummy.jpg"
        dummy_file.write_bytes(b"\xff\xd8\xff\xd9")  # minimal JPEG

        # Patch ExifImageCollection to return an empty dict
        monkeypatch.setattr("tagkit.ExifImageCollection", always_empty)

        result = runner.invoke(app, ["view", str(dummy_file)])
        assert result.exit_code == 0, result.output
        assert "No EXIF data found for the selected files" in result.output
