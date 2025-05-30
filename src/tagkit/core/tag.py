"""
EXIF tag representation.

This module provides the ExifTag class which represents a single EXIF tag
with its ID, value, and IFD location.
"""

from dataclasses import dataclass
from typing import Optional

from tagkit.core.registry import tag_registry
from tagkit.core.types import TagValue, ExifType, IfdName
from tagkit.core.formatting import ValueFormatter


@dataclass
class ExifTag:
    """
    Represents a single EXIF tag entry with its ID, value, and IFD location.

    Args:
        id: The EXIF tag ID
        value: The tag value
        ifd: The Image File Directory containing this tag
    """

    id: int
    value: TagValue
    ifd: IfdName

    def __post_init__(self):
        self.formatter = ValueFormatter.from_yaml()

    @property
    def name(self) -> str:
        """Get the human-readable name of this tag."""
        return tag_registry.resolve_tag_name(self.id)

    @property
    def exif_type(self) -> ExifType:
        """Get the EXIF data type of this tag."""
        return tag_registry.get_exif_type(self.id)

    def format(self, binary_format: Optional[str] = None) -> str:
        """
        Format the tag value as a string.

        Args:
            binary_format: How to format binary data - 'bytes', 'hex', or 'base64'.
                If None, <bytes: N> will be shown as a placeholder.

        Returns:
            The formatted value as a string.

        Examples:
            >>> entry = ExifTag(id=0x010f, value="Canon", ifd='IFD0')
            >>> entry.format()
            'Canon'

            >>> entry = ExifTag(id=0x9286, value=b'\\x89PNG\\r\\n', ifd='Exif')
            >>> entry.format()
            '<bytes: 6>'

            >>> entry.format(binary_format="hex")
            'hex:89504e470d0a'

            >>> entry.format(binary_format="base64")
            'base64:iVBORw0K'

            >>> entry.format(binary_format=None)
            '<bytes: 6>'
        """
        return self.formatter.format_value(self, binary_format=binary_format)

    def as_dict(self, binary_format: Optional[str] = None) -> dict:
        """
        Convert the EXIF entry to a dictionary.

        Args:
            binary_format: How to format binary data. One of:
                - 'bytes': Python bytes literal (e.g., b'data')
                - 'hex': Hex-encoded string with 'hex:' prefix
                - 'base64': Base64-encoded string with 'base64:' prefix

        Returns:
            Dictionary with these keys:
                - id (int): The EXIF tag ID
                - name (str): The tag's human-readable name
                - value: The formatted tag value
                - ifd (str): The Image File Directory containing this tag

        Examples:

            >>> from tagkit.core.tag import ExifTag
            >>> entry = ExifTag(id=0x010f, value='Canon', ifd='IFD0')
            >>> entry.as_dict()
            {'id': 271, 'name': 'Make', 'value': 'Canon', 'ifd': 'IFD0'}

            >>> entry = ExifTag(id=0x9286, value=b'\\x89PNG\\r\\n', ifd='Exif')
            >>> entry.as_dict(binary_format="hex")
            {'id': 37510, 'name': 'UserComment', 'value': 'hex:89504e470d0a', 'ifd': 'Exif'}

            >>> entry.as_dict(binary_format="base64")
            {'id': 37510, 'name': 'UserComment', 'value': 'base64:iVBORw0K', 'ifd': 'Exif'}
        """
        return {
            "id": self.id,
            "name": self.name,
            "value": self.format(binary_format=binary_format),
            "ifd": self.ifd,
        }
