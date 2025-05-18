from typing import Any, Iterable, TypeVar

T = TypeVar("T")


def validate_single_arg_set(
    kwarg_dict: dict[str, Any],
    allow_nothing_set: bool = True,
    strict_none: bool = True,
) -> None:
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
    return ", ".join([f"'{item}'" for item in items])
