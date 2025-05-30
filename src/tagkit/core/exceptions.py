"""
Exception classes for tagkit.

This module contains all custom exceptions used throughout the tagkit package.
"""


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

    pass


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
