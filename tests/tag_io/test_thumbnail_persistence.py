"""Round-trip coverage for JPEG thumbnails using the real piexif backend."""

import piexif
import pytest

from tagkit import ExifImage
from tagkit.tag_io.piexif_io import PiexifBackend


@pytest.mark.parametrize(
    "operation",
    [
        "unchanged",
        "write_primary",
        "write_thumbnail",
        "delete_thumbnail",
        "delete_primary",
    ],
)
def test_thumbnail_payload_and_occurrences_survive_save(test_images, operation):
    path = test_images / "with_thumbnail.jpg"
    original = piexif.load(str(path))
    thumbnail = original["thumbnail"]
    assert thumbnail is not None
    exif = ExifImage(path)

    primary_orientation = 1
    thumbnail_orientation = 6
    if operation == "write_primary":
        exif.write_tag("Orientation", 3)
        primary_orientation = 3
    elif operation == "write_thumbnail":
        exif.write_tag("Orientation", 3, ifd="IFD1")
        thumbnail_orientation = 3
    elif operation == "delete_thumbnail":
        exif.delete_tag("Orientation", ifd="IFD1")
        thumbnail_orientation = None
    elif operation == "delete_primary":
        exif.delete_tag("Orientation")
        primary_orientation = None

    # Saving twice also verifies that preservation works after offsets change.
    for _ in range(2):
        exif.save()
        raw = piexif.load(str(path))
        assert raw["thumbnail"] == thumbnail
        assert raw["0th"].get(274) == primary_orientation
        assert raw["1st"].get(274) == thumbnail_orientation
        assert raw["1st"][514] == len(thumbnail)
        assert raw["1st"][270] == b"Thumbnail"

        exif = ExifImage(path)
        expected_keys = {("IFD0", 274), ("IFD1", 274)}
        if primary_orientation is None:
            expected_keys.remove(("IFD0", 274))
        if thumbnail_orientation is None:
            expected_keys.remove(("IFD1", 274))
        assert {key for key in exif.tag_entries if key[1] == 274} == expected_keys


def test_thumbnail_payload_is_not_shared_between_images(test_images):
    backend = PiexifBackend()
    with_thumbnail = test_images / "with_thumbnail.jpg"
    without_thumbnail = test_images / "minimal.jpg"
    thumbnail = piexif.load(str(with_thumbnail))["thumbnail"]
    first = ExifImage(with_thumbnail, io_backend=backend)
    second = ExifImage(without_thumbnail, io_backend=backend)

    first.write_tag("Artist", "Primary image")
    second.write_tag("Artist", "Other image")
    first.save()
    second.save()

    assert piexif.load(str(with_thumbnail))["thumbnail"] == thumbnail
    assert piexif.load(str(without_thumbnail))["thumbnail"] is None


def test_save_rejects_thumbnail_tags_without_a_thumbnail_payload(test_images):
    path = test_images / "minimal.jpg"
    original = path.read_bytes()
    exif = ExifImage(path)
    exif.write_tag("Orientation", 6, ifd="IFD1")

    with pytest.raises(ValueError, match="embedded JPEG thumbnail"):
        exif.save()

    assert path.read_bytes() == original
