class TagkitError(Exception):
    """
    Base exception for all custom tagkit errors.

    Example:
        >>> raise TagkitError('Something went wrong')
    """

    pass


class ValidationError(TagkitError):
    """
    Raised when a validation error occurs in tagkit.

    Example:
        >>> raise ValidationError('Invalid value')
    """

    pass


class ConversionError(TagkitError):
    """
    Raised when a conversion error occurs in tagkit.

    Example:
        >>> raise ConversionError('Failed to convert value')
    """

    pass


class ExifToolError(TagkitError):
    """
    Raised when an error occurs while using an external EXIF tool.

    Example:
        >>> raise ExifToolError('ExifTool failed')
    """

    pass


class BatchProcessingError(TagkitError):
    """
    Raised when an error occurs during batch processing of images.

    Example:
        >>> raise BatchProcessingError('Batch failed')
    """

    pass


class DateTimeError(TagkitError):
    """
    Raised when a date/time parsing or formatting error occurs.

    Example:
        >>> raise DateTimeError('Invalid date format')
    """

    pass


class InvalidTagName(TagkitError):
    """
    Raised when an invalid tag name is used.

    Args:
        tag_name (str): The invalid tag name.

    Example:
        >>> raise InvalidTagName('NotATag')
    """

    def __init__(self, tag_name: str) -> None:
        super().__init__(
            f"Invalid tag name '{tag_name}'. "
            "Evaluate `tag_registry.tag_names` to see all valid aliases."
        )


class InvalidTagId(TagkitError):
    """
    Raised when the supplied tag id isn't valid.

    Args:
        tag_id (int): The invalid tag ID.

    Example:
        >>> raise InvalidTagId(99999)
    """

    def __init__(self, tag_id: int):
        msg = f"Tag ID '{tag_id}' is invalid and not part of the exif specification."
        super().__init__(msg)
