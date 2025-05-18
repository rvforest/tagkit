import base64

from rich import print_json


def to_serializable(val):
    """
    Recursively convert objects to types suitable for JSON serialization.

    - Any object with a to_dict() method is converted using that method.
    - Bytes values are displayed as base64-encoded strings if they cannot be decoded as UTF-8.
    - Lists and dicts are processed recursively.
    """
    if hasattr(val, "to_dict") and callable(val.to_dict):
        return to_serializable(val.to_dict())
    elif isinstance(val, bytes):
        try:
            return val.decode("utf-8")
        except UnicodeDecodeError:
            return base64.b64encode(val).decode("ascii")
    elif isinstance(val, dict):
        return {k: to_serializable(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [to_serializable(i) for i in val]
    else:
        return val


def print_exif_json(exif_data):
    """
    Print EXIF data as JSON using rich formatting.

    Args:
        exif_data (dict): EXIF data to print.

    Notes:
        - Any bytes values in the EXIF data will be displayed as base64-encoded strings if they cannot be decoded as UTF-8.

    Example:
        >>> print_exif_json({"img.jpg": {256: ExifEntry(...)}})
    """
    data = to_serializable(exif_data)
    print_json(data=data)
