from tagkit.value_formatting import TagValueFormatter

import pytest


@pytest.fixture
def formatter() -> TagValueFormatter:
    return TagValueFormatter.from_yaml()


def test_yaml_load(formatter):
    pass


def test_decimal(formatter):
    input_val = (100, 200)
    expected = "0.5"
    assert formatter._format_decimal(input_val) == expected


def test_f_number_format(formatter):
    input_val = (28, 10)
    expected = "f/2.8"
    assert formatter._format_f_number(input_val) == expected
