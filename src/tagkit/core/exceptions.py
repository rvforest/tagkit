"""
Exception classes for tagkit.

This module contains all custom exceptions used throughout the tagkit package.
"""

from typing import Any, Iterable, Union


class TagkitError(Exception):
    """Base exception for all custom tagkit errors."""

    pass


class ValidationError(TagkitError):
    """Raised when a validation error occurs in tagkit."""

    pass


class ConversionError(TagkitError):
    """Raised when a conversion error occurs in tagkit."""

    pass


class ExifToolError(TagkitError):
    """Raised when an error occurs while using an external EXIF tool."""

    pass


class BatchProcessingError(TagkitError):
    """Raised when an error occurs during batch processing of images."""

    pass


class DateTimeError(TagkitError):
    """Raised when a date/time parsing or formatting error occurs."""

    def __init__(self, value: Any) -> None:
        super().__init__(
            f"Tag value is not a valid datetime: '{value}'. "
            "Expected format is 'YYYY:MM:DD HH:MM:SS'."
        )


class InvalidTagName(TagkitError):
    """Raised when an invalid tag name is used.

    Args:
        tag_name (str): The invalid tag name.
    """

    def __init__(self, tag_name: str) -> None:
        super().__init__(
            f"Invalid tag name '{tag_name}'. "
            "Evaluate `tag_registry.tag_names` to see all valid aliases."
        )


class InvalidTagId(TagkitError):
    """Raised when the supplied tag id isn't valid.

    Args:
        tag_id (int): The invalid tag ID.
    """

    def __init__(self, tag_id: int):
        msg = f"Tag ID '{tag_id}' is invalid and not part of the exif specification."
        super().__init__(msg)


class TagNotFound(TagkitError):
    """Raised when a specified tag is not found in an image.

    Args:
        tag_name (str): The name of the tag that was not found.
    """

    def __init__(self, tag_name: Union[str, Iterable[str]]):
        first_word = "Tag" if isinstance(tag_name, str) else "Tags"
        if isinstance(tag_name, list):
            tag_name = ", ".join(tag_name)
        super().__init__(f"{first_word} '{tag_name}' not found in image.")


class FileNotInCollection(TagkitError):
    """Raised when a filename requested is not present in an ExifImageCollection."""

    def __init__(self, file_name: str) -> None:
        super().__init__(f"File not found in ExifImageCollection: '{file_name}'")


class TagTypeError(ValidationError):
    """Raised when a tag value has an invalid type for the tag's EXIF type.

    Args:
        tag_id: The tag ID.
        tag_name: The tag name.
        exif_type: The expected EXIF type.
        value: The invalid value provided.
        detail: Additional detail about the validation error.
    """

    def __init__(
        self,
        tag_id: int,
        tag_name: str,
        exif_type: str,
        value: Any,
        detail: str,
    ) -> None:
        super().__init__(
            f"Invalid value type for tag '{tag_name}' (ID: {tag_id}, Type: {exif_type}). "
            f"Received: {type(value).__name__}. {detail}"
        )
