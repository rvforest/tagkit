"""
Utility functions for tagkit.

This module provides general utility functions used throughout the tagkit package.
"""

from typing import Any, Iterable, TypeVar

T = TypeVar("T")


def validate_single_arg_set(
    kwarg_dict: dict[str, Any],
    allow_nothing_set: bool = True,
    strict_none: bool = True,
) -> None:
    """
    Validate that only one of the given keyword arguments is set.

    Args:
        kwarg_dict: Dictionary of keyword arguments to validate
        allow_nothing_set: If True, allows no arguments to be set
        strict_none: If True, considers None values as not set

    Raises:
        ValueError: If more than one argument is set, or if no arguments are set
            and allow_nothing_set is False
    """
    if strict_none:
        set_kwargs = [kwarg for kwarg, val in kwarg_dict.items() if val is not None]
    else:
        set_kwargs = [kwarg for kwarg, val in kwarg_dict.items() if val]

    if not allow_nothing_set and (len(set_kwargs) == 0):
        raise ValueError(
            f"One of the following must be set: {_quoted_comma_sep_list(kwarg_dict)}. "
            "None are currently set."
        )
    if len(set_kwargs) > 1:
        raise ValueError(
            f"{_quoted_comma_sep_list(set_kwargs)} are set. "
            f"Only one of the following should be set: {kwarg_dict}."
        )


def _quoted_comma_sep_list(items: Iterable[str]) -> str:
    """
    Format a list of strings as a comma-separated list with each item in quotes.

    Args:
        items: Iterable of strings to format

    Returns:
        A string with each item in quotes, separated by commas
    """
    return ", ".join([f"'{item}'" for item in items])
