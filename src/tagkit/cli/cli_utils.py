from typing import Optional

def tag_ids_to_int(tags: Optional[str]) -> Optional[list]:
    if tags is None:
        return None
    result = []
    for tag in tags.split(","):
        try:
            tag = int(tag)
        except ValueError:
            pass
        result.append(tag)
    return result 