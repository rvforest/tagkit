from typing import Optional, overload


@overload
def tag_ids_to_int(tags: None) -> None: ...


@overload
def tag_ids_to_int(tags: str) -> list[int]: ...


def tag_ids_to_int(tags: Optional[str]) -> Optional[list[int]]:
    if tags is None:
        return None
    result: list[int] = []
    for tag_str in tags.split(","):
        try:
            tag = int(tag_str)
        except ValueError:
            continue
        finally:
            result.append(tag)
    return result
