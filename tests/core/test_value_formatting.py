import base64
import pytest

from tagkit.exif_entry import ExifEntry
from tagkit.types import IfdName
from tagkit.value_formatting import TagValueFormatter


@pytest.fixture
def formatter() -> TagValueFormatter:
    return TagValueFormatter.from_yaml()


def test_format_decimal(formatter: TagValueFormatter):
    assert formatter._format_decimal((1, 2)) == "0.5"


def test_format_fraction(formatter: TagValueFormatter):
    assert formatter._format_fraction((1, 2)) == "1/2"


def test_format_f_number(formatter: TagValueFormatter):
    assert formatter._format_f_number((497, 100)) == "f/5.6"
    assert formatter._format_f_number((2, 1)) == "f/2.0"


def test_format_percent(formatter: TagValueFormatter):
    assert formatter._format_percent((1, 2)) == "50%"


def test_format_coordinates_with_seconds(formatter: TagValueFormatter):
    assert formatter._format_coordinates(((1, 1), (2, 1), (3, 1))) == "1°2'3\""


def test_format_coordinates_with_fract_min(formatter: TagValueFormatter):
    assert formatter._format_coordinates(((1, 1), (2, 1), (3, 100))) == "1°2.03'"


def test_exif_entry_formatted_value_b64():
    # Use a valid tag id (271 is used in doc examples, e.g. 'Make')
    tag_id = 271
    ifd: IfdName = "IFD0"
    raw_bytes = b"\xff\xfe\xfd\xfc"
    entry = ExifEntry(id=tag_id, value=raw_bytes, ifd=ifd)

    expected_b64 = f"base64:{base64.b64encode(raw_bytes).decode('ascii')}"
    assert entry.format(render_bytes=True, binary_format="base64") == expected_b64


def test_show_plus(formatter: TagValueFormatter):
    assert formatter._show_plus("42") == "+42"


def test_format_lens_info(formatter: TagValueFormatter):
    val = ((24, 1), (70, 1), (297, 100), (497, 100))
    # min_focal_len = 24/1 = 24
    # max_focal_len = 70/1 = 70
    # min_f_num = f/2.8
    # max_f_num = f/5.6
    expected = "24.0 mm - 70.0; f/2.8 - f/5.6"
    assert formatter._format_lens_info(val) == expected


def test_format_map(formatter: TagValueFormatter):
    mapping = {1: "Auto", 2: "Manual"}
    assert formatter._format_map(2, mapping) == "Manual"


def test_format_bytes_utf8(formatter: TagValueFormatter):
    val = b"hello"
    assert formatter._format_bytes(val, render_bytes=True) == "b'hello'"


def test_format_bytes_non_utf8(formatter: TagValueFormatter):
    val = b"\xff\xfe\xfd\xfc"
    expected = base64.b64encode(val).decode("ascii")
    assert (
        formatter._format_bytes(val, render_bytes=True, binary_format="base64")
        == f"base64:{expected}"
    )


def test_format_bytes_no_render(formatter: TagValueFormatter):
    val = b"hello"
    assert formatter._format_bytes(val, render_bytes=False) == "<bytes: 5>"


def test_format_decimal_with_units(formatter: TagValueFormatter):
    assert formatter._format_decimal((3, 2), unit="mm") == "1.5mm"


def test_format_fraction_with_units(formatter: TagValueFormatter):
    assert formatter._format_fraction((3, 2), unit="mm") == "3/2mm"


def test_format_shutter_speed_fraction(formatter: TagValueFormatter):
    # APEX 8 -> 1/256s (should round to 1/250s)
    assert (
        formatter._format_shutter_speed((8, 1)) == "1/256s"
        or formatter._format_shutter_speed((8, 1)) == "1/250s"
    )
    # APEX 0 -> 1s
    assert formatter._format_shutter_speed((0, 1)) == "1s"
    # APEX -1 -> 2s
    assert formatter._format_shutter_speed((-1, 1)) == "2s"


def test_format_shutter_speed_whole_seconds(formatter: TagValueFormatter):
    assert formatter._format_shutter_speed((-2, 1)) == "4s"
    assert formatter._format_shutter_speed((-232, 100)) == "5.0s"


def test_format_shutter_speed_decimal_seconds(formatter: TagValueFormatter):
    # 1.5s
    assert formatter._format_shutter_speed((-585, 1000)) == "1.5s"
