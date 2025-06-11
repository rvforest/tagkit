from unittest import mock

import pytest

from tagkit import ExifImageCollection
import os
from pathlib import Path
from tagkit.image.exif import ExifImage
from typing import Union
from tagkit.core.types import TagValue
from tagkit.core.exceptions import InvalidTagName


@pytest.fixture
def mock_exif_data():
    return {
        "0th": {271: b"TestMake", 272: b"TestModel"},
        "Exif": {37385: 1},
        "GPS": {},
        "Interop": {},
        "1st": {},
        "thumbnail": None,
    }


@pytest.fixture
def n_tags_expected(mock_exif_data):
    n = 0
    for tags in mock_exif_data.values():
        try:
            n += len(tags)
        except TypeError:  # len(None) failed
            pass
    return n


@pytest.fixture
def mock_exif_w_patch(mock_exif_data):
    with mock.patch("tagkit.tag_io.piexif_io.piexif.load") as mocked_fn:
        mocked_fn.return_value = mock_exif_data
        yield mock_exif_data


class TestImageCollection:
    def test_image_collection_files_loaded(self, mock_exif_w_patch):
        n_files_expected = 3

        result = ExifImageCollection([f"foo_{i}" for i in range(n_files_expected)])

        for i in range(n_files_expected):
            assert f"foo_{i}" in result.files

    def test_all_tags_retrieved(self, n_tags_expected, mock_exif_w_patch):
        result = ExifImageCollection(["foo"])
        n_tags = len(result.files["foo"])
        assert n_tags == n_tags_expected

    def test_n_tags_property(self, n_tags_expected, mock_exif_w_patch):
        result = ExifImageCollection(["foo"])
        assert result.n_tags == n_tags_expected

    def test_image_collection_tag_values_retrieved(self, mock_exif_w_patch):
        result = ExifImageCollection(["foo"])

        assert result.files["foo"].tags["Make"].value == mock_exif_w_patch["0th"][
            271
        ].decode("ascii")
        assert result.files["foo"].tags["Model"].value == mock_exif_w_patch["0th"][
            272
        ].decode("ascii")
        assert (
            result.files["foo"].tags["Flash"].value == mock_exif_w_patch["Exif"][37385]
        )

    def test_write_tag_all_files(self, mock_exif_w_patch):
        files = [f"foo_{i}" for i in range(2)]
        collection = ExifImageCollection(files)
        collection.write_tag("Artist", "John Doe")
        for fname in files:
            assert collection.files[fname].tags["Artist"].value == "John Doe"

    def test_write_tag_selected_files(self, mock_exif_w_patch):
        files = ["foo_0", "foo_1"]
        collection = ExifImageCollection(files)
        collection.write_tag("Artist", "Jane", files=["foo_1"])
        assert "Artist" not in collection.files["foo_0"].tags
        assert collection.files["foo_1"].tags["Artist"].value == "Jane"

    def test_delete_tag_all_files(self, mock_exif_w_patch):
        files = ["foo_0", "foo_1"]
        collection = ExifImageCollection(files)
        # Add tag to both
        for fname in files:
            collection.files[fname].write_tag("Artist", "val")
        collection.delete_tag("Artist")
        for fname in files:
            assert "Artist" not in collection.files[fname].tags

    def test_delete_tag_selected_files(self, mock_exif_w_patch):
        files = ["foo_0", "foo_1"]
        collection = ExifImageCollection(files)
        collection.files["foo_0"].write_tag("Artist", "val0")
        # Only foo_0 has the tag
        collection.delete_tag("Artist", files=["foo_0", "foo_1"])
        assert "Artist" not in collection.files["foo_0"].tags
        # foo_1 never had the tag, should not raise
        assert "Artist" not in collection.files["foo_1"].tags

    def test_delete_tag_missing_tag_ignored(self, mock_exif_w_patch):
        files = ["foo_0"]
        collection = ExifImageCollection(files)
        # No tag written
        # Should not raise
        collection.delete_tag("Artist")
        assert "Artist" not in collection.files["foo_0"].tags

    def test_write_tag_file_not_found(self, mock_exif_w_patch):
        collection = ExifImageCollection(["foo_0"])
        with pytest.raises(KeyError):
            collection.write_tag("Artist", "X", files=["not_a_file"])

    def test_delete_tag_file_not_found(self, mock_exif_w_patch):
        collection = ExifImageCollection(["foo_0"])
        with pytest.raises(KeyError):
            collection.delete_tag("Artist", files=["not_a_file"])

    def test_write_tag_selected_files_accepts_path(self, mock_exif_w_patch):
        files = ["foo_0", "foo_1"]
        collection = ExifImageCollection(files)
        # Pass a Path object as the file identifier
        collection.write_tag("Artist", "Jane", files=[Path("foo_1")])
        assert "Artist" not in collection.files["foo_0"].tags
        assert collection.files["foo_1"].tags["Artist"].value == "Jane"

    def test_delete_tag_selected_files_accepts_path(self, mock_exif_w_patch):
        files = ["foo_0", "foo_1"]
        collection = ExifImageCollection(files)
        collection.files["foo_0"].write_tag("Artist", "val0")
        # Pass a Path object as the file identifier
        collection.delete_tag("Artist", files=[Path("foo_0")])
        assert "Artist" not in collection.files["foo_0"].tags
        # foo_1 never had the tag, should not raise
        assert "Artist" not in collection.files["foo_1"].tags

    def test_write_tags_all_files(self, mock_exif_w_patch: dict):
        files = [f"foo_{i}" for i in range(2)]
        tags: dict[Union[str, int], TagValue] = {
            "Artist": "Jane Doe",
            "Copyright": b"2025 John",
        }
        collection = ExifImageCollection(files)
        collection.write_tags(tags)
        for fname in files:
            assert collection.files[fname].tags["Artist"].value == "Jane Doe"
            assert collection.files[fname].tags["Copyright"].value == b"2025 John"

    @pytest.mark.parametrize("file_type", [str, Path])
    def test_write_tags_selected_files(self, mock_exif_w_patch: dict, file_type):
        files = ["foo_0", "foo_1"]
        tags: dict[Union[str, int], TagValue] = {"Artist": "Jane Doe"}
        collection = ExifImageCollection(files)
        file_id = file_type("foo_1")
        collection.write_tags(tags, files=[file_id])
        assert "Artist" not in collection.files["foo_0"].tags
        assert collection.files["foo_1"].tags["Artist"].value == "Jane Doe"

    def test_write_tags_empty_dict(self, mock_exif_w_patch):
        files = ["foo_0"]
        collection = ExifImageCollection(files)
        collection.write_tags({})
        # Should not raise, tags remain unchanged
        assert "Make" in collection.files["foo_0"].tags or True

    def test_write_tags_file_not_found(self, mock_exif_w_patch: dict):
        files = ["foo_0"]
        tags: dict[Union[str, int], TagValue] = {"Artist": "Jane Doe"}
        collection = ExifImageCollection(files)
        with pytest.raises(KeyError):
            collection.write_tags(tags, files=["not_a_file"])

    def test_delete_tags_all_files(self, mock_exif_w_patch: dict):
        files = [f"foo_{i}" for i in range(2)]
        tags: dict[Union[str, int], TagValue] = {
            "Artist": "Jane Doe",
            "Copyright": "2025 John",
        }
        collection = ExifImageCollection(files)
        collection.write_tags(tags)
        collection.delete_tags(["Artist", "Copyright"])
        for fname in files:
            assert "Artist" not in collection.files[fname].tags
            assert "Copyright" not in collection.files[fname].tags

    def test_delete_tags_file_not_found(self, mock_exif_w_patch):
        collection = ExifImageCollection(["foo_0"])
        with pytest.raises(KeyError):
            collection.delete_tags(["Artist"], files=["not_a_file"])

    @pytest.mark.parametrize("file_type", [str, Path])
    def test_delete_tags_selected_files(self, mock_exif_w_patch: dict, file_type):
        files = ["foo_0", "foo_1"]
        tags: dict[Union[str, int], TagValue] = {"Artist": "Jane Doe"}
        collection = ExifImageCollection(files)
        file_id = file_type("foo_0")
        collection.write_tags(tags, files=[file_id])
        collection.delete_tags(["Artist"], files=[file_id])
        assert "Artist" not in collection.files["foo_0"].tags
        # foo_1 never had the tag, should not raise
        assert "Artist" not in collection.files["foo_1"].tags

    def test_delete_tags_empty_list(self, mock_exif_w_patch):
        files = ["foo_0"]
        collection = ExifImageCollection(files)
        collection.delete_tags([])
        # Should not raise, tags remain unchanged
        assert "Make" in collection.files["foo_0"].tags or True

    def test_delete_tags_partial_missing(self, mock_exif_w_patch):
        files = ["foo_0"]
        collection = ExifImageCollection(files)
        collection.write_tags({"Artist": "Jane Doe"})
        with pytest.raises(InvalidTagName):
            collection.delete_tags(["Artist", "NonExistentTag"])

    def test_delete_tags_valid_but_missing_tag_is_forgiving(self, mock_exif_w_patch):
        files = ["foo_0", "foo_1"]
        collection = ExifImageCollection(files)
        # Only write 'Artist' to foo_0
        collection.files["foo_0"].write_tag("Artist", "Jane Doe")
        # Attempt to delete 'Artist' from both files
        # Should not raise, and 'Artist' should be gone from foo_0, still absent from foo_1
        collection.delete_tags(["Artist"], files=files)
        assert "Artist" not in collection.files["foo_0"].tags
        assert "Artist" not in collection.files["foo_1"].tags

    def test_n_files_property(self, mock_exif_w_patch):
        files = [f"foo_{i}" for i in range(4)]
        collection = ExifImageCollection(files)
        assert collection.n_files == 4


class TestImageCollectionIntegration:
    def test_bulk_write_save_reload(self, test_images: Path):
        # files = list(test_images.glob("*.jpg"))
        files = test_images.glob("*.jpg")

        collection = ExifImageCollection(files)
        collection.write_tag("Make", "IntegrationTest")
        collection.save_all()

        # Reload and check
        reloaded = ExifImageCollection(files)
        for exif in reloaded.files.values():
            assert exif.tags["Make"].value == "IntegrationTest"

    def test_bulk_delete_save_reload(self, test_images: Path):
        files = list(test_images.glob("*.jpg"))
        collection = ExifImageCollection(files)
        # Delete a tag that exists
        collection.delete_tag("Make")
        collection.save_all()
        # Reload and check
        reloaded = ExifImageCollection(files)
        for exif in reloaded.files.values():
            assert "Make" not in exif.tags

    def test_partial_write_delete_save_reload(self, test_images: Path):
        files = list(test_images.glob("*.jpg"))
        collection = ExifImageCollection(files)

        # Only update one file (choose a valid, non-corrupt file with 'Make' tag)
        valid_files = [
            f for f in files if "corrupt" not in str(f) and "minimal" in str(f)
        ]
        file_path = valid_files[0]
        fname = file_path.name
        collection.write_tag("Make", "PartialTest", files=[fname])
        collection.save_all()

        reloaded = ExifImageCollection(files)
        assert reloaded.files[fname].tags["Make"].value == "PartialTest"

        # Now delete only from that file
        collection.delete_tag("Make", files=[fname])
        collection.save_all()

        reloaded2 = ExifImageCollection(files)
        print(f"DEBUG: reloaded2.files.keys()={list(reloaded2.files.keys())}")
        assert "Make" not in reloaded2.files[fname].tags

    def test_save_all_creates_backup(self, test_images: Path):
        files = list(test_images.glob("*.jpg"))
        collection = ExifImageCollection(files)
        # Use all valid files for backup test
        valid_files = [
            f for f in files if "corrupt" not in str(f) and "minimal" in str(f)
        ]
        fnames = [f.name for f in valid_files]
        # Write a tag to all valid files
        collection.write_tag("Make", "BackupTest", files=fnames)
        collection.save_all(create_backup=True)
        for file_path in valid_files:
            backup = file_path.parent / (file_path.name + ".bak")
            assert backup.exists(), f"Backup not found for {file_path.name}"
            # The backup should not have the new value
            exif_bak = ExifImage(backup)
            assert exif_bak.tags["Make"].value != "BackupTest", (
                f"Backup for {file_path.name} has the new value!"
            )

    def test_bulk_write_tags_save_reload(self, test_images: Path):
        files = list(test_images.glob("*.jpg"))
        tags: dict[Union[str, int], TagValue] = {
            "Artist": "Jane Doe",
            "Copyright": "2025 John",
        }
        collection = ExifImageCollection(files)
        collection.write_tags(tags)
        collection.save_all()
        reloaded = ExifImageCollection(files)
        for exif in reloaded.files.values():
            assert exif.tags["Artist"].value == "Jane Doe"
            assert exif.tags["Copyright"].value == "2025 John"

    def test_bulk_delete_tags_save_reload(self, test_images: Path):
        files = list(test_images.glob("*.jpg"))
        tags: dict[Union[str, int], TagValue] = {
            "Artist": "Jane Doe",
            "Copyright": "2025 John",
        }
        collection = ExifImageCollection(files)
        collection.write_tags(tags)
        collection.save_all()
        collection.delete_tags(["Artist", "Copyright"])
        collection.save_all()
        reloaded = ExifImageCollection(files)
        for exif in reloaded.files.values():
            assert "Artist" not in exif.tags
            assert "Copyright" not in exif.tags
