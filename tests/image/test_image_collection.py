from unittest import mock

import pytest

from tagkit import ExifImageCollection


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
