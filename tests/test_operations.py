from unittest import mock

import pytest

import tagkit.operations as ops


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
def patch_exif_io(mock_exif_data):
    with mock.patch("tagkit.tag_io.piexif_io.piexif.load") as mocked_fn:
        mocked_fn.return_value = mock_exif_data
        yield mock_exif_data


class TestGetExif:
    def test_get_exif_files_loaded(self, patch_exif_io):
        n_files_expected = 3

        result = ops.get_exif([f"foo_{i}" for i in range(n_files_expected)])

        for i in range(n_files_expected):
            assert f"foo_{i}" in result

    def test_all_tags_retrieved(self, n_tags_expected, patch_exif_io):
        n_tags_expected = sum(len(d) for d in patch_exif_io.values() if d is not None)
        result = ops.get_exif(["foo"])
        n_tags = len(result["foo"])
        assert n_tags == n_tags_expected

    def test_get_exif_tag_values_retrieved(self, n_tags_expected, patch_exif_io):
        result = ops.get_exif(["foo"])

        assert result["foo"][271].value == patch_exif_io["0th"][271].decode("ascii")
        assert result["foo"][272].value == patch_exif_io["0th"][272].decode("ascii")
        assert result["foo"][37385].value == patch_exif_io["Exif"][37385]

    def test_get_exif_w_id_filter(self, patch_exif_io):
        result = ops.get_exif(["foo"], tag_filter=[271])
        assert len(result["foo"]) == 1
