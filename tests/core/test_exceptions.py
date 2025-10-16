import pytest

from tagkit.core.exceptions import TagNotFound


def test_tag_not_found_single():
    with pytest.raises(TagNotFound) as exc_info:
        raise TagNotFound("DateTimeOriginal")
    assert str(exc_info.value) == "Tag 'DateTimeOriginal' not found in image."


def test_tag_not_found_multiple():
    with pytest.raises(TagNotFound) as exc_info:
        raise TagNotFound(["DateTimeOriginal", "CreateDate"])
    assert (
        str(exc_info.value) == "Tags 'DateTimeOriginal, CreateDate' not found in image."
    )
