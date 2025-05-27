import pytest

from tagkit.core.utils import validate_single_arg_set


class TestValidateSingleArgSet:
    def test_allow_none_set_true(self):
        """Test that no exception is raised when args are not set and
        allow_none_set is True
        """
        validate_single_arg_set({"a": None, "b": None}, allow_nothing_set=True)

    def test_allow_none_set_false(self):
        """Test that exception is raised when args are not set and
        allow_none_set is False
        """
        with pytest.raises(ValueError):
            validate_single_arg_set({"a": None, "b": None}, allow_nothing_set=False)

    def test_single_args_set(self):
        """Tests that no exception is raised when a single arg is set"""
        validate_single_arg_set({"a": 1, "b": None, "c": None})

    def test_multiple_args_set(self):
        """Tests that exception is raised when a multiple args are set"""
        with pytest.raises(ValueError):
            validate_single_arg_set({"a": 1, "b": 2, "c": None})

    def test_strict_mode_false(self):
        """Test that falsiness is used when strict mode is False"""
        validate_single_arg_set({"a": "", "b": 0, "c": 1}, strict_none=False)

    def test_strict_mode_true(self):
        """Test that falsiness is not used and exception is raised when strict mode is
        False and falsy values are used
        """
        with pytest.raises(ValueError):
            validate_single_arg_set({"a": "", "b": 0, "c": 1})
