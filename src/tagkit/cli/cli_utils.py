from typing import Optional, overload


@overload
def tag_ids_to_int(tags: None) -> None: ...


@overload
def tag_ids_to_int(tags: str) -> list[int | str]: ...


def tag_ids_to_int(tags: Optional[str]) -> Optional[list[int | str]]:
    if tags is None:
        return None
    result: list[int | str] = []
    for tag_str in tags.split(","):
        try:
            tag = int(tag_str)
            result.append(tag)
        except ValueError:
            # Keep as string if it can't be converted to int
            result.append(tag_str)
    return result
