from dataclasses import dataclass
from typing import Optional

from tagkit.tag_registry import tag_registry
from tagkit.types import ExifTag, ExifType, IfdName
from tagkit.value_formatting import TagValueFormatter


@dataclass
class ExifEntry:
    id: int
    value: ExifTag
    ifd: IfdName

    def __post_init__(self):
        self.formatter = TagValueFormatter.from_yaml()

    @property
    def name(self) -> str:
        return tag_registry.get_tag_name(self.id)

    @property
    def exif_type(self) -> ExifType:
        return tag_registry.get_exif_type(self.id)

    def format(
        self, render_bytes: bool = True, binary_format: Optional[str] = None
    ) -> str:
        """
        Format the tag value as a string.

        Args:
            render_bytes: If False, binary data will be shown as a placeholder.
            binary_format: How to format binary data - 'bytes', 'hex', or 'base64'.

        Returns:
            The formatted value as a string.

        Examples:
            >>> entry = ExifEntry(0x010f, b'Canon', 'IFD0')
            >>> entry.format()  # Returns: "Canon" (UTF-8 decodable)

            >>> entry = ExifEntry(0x9286, b'\\x89PNG\\r\\n', 'Exif')
            >>> entry.format()  # Returns: b'\\x89PNG\\r\\n' (bytes format)
            >>> entry.format(binary_format="hex")  # Returns: "hex:89504e470d0a"
            >>> entry.format(binary_format="base64")  # Returns: "base64:iVBORw0K"
            >>> entry.format(render_bytes=False)  # Returns: "<bytes: 6>"
        """
        return self.formatter.format(self, render_bytes, binary_format)

    def to_dict(
        self, render_bytes: bool = True, binary_format: Optional[str] = None
    ) -> dict:
        """Convert the EXIF entry to a dictionary.

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
            >>> entry = ExifEntry(0x010f, b'Canon', 'IFD0')
            >>> entry.to_dict()
            {'id': 271, 'name': 'Make', 'value': 'Canon', 'ifd': 'IFD0'}

            >>> entry = ExifEntry(0x9286, b'\\x89PNG\\r\\n', 'Exif')
            >>> entry.to_dict(binary_format="hex")
            {'id': 37510, 'name': 'UserComment', 'value': 'hex:89504e470d0a', 'ifd': 'Exif'}

            >>> entry.to_dict(binary_format="base64")
            {'id': 37510, 'name': 'UserComment', 'value': 'base64:iVBORw0K', 'ifd': 'Exif'}
        """
        return {
            "id": self.id,
            "name": self.name,
            "value": self.format(
                render_bytes=render_bytes, binary_format=binary_format
            ),
            "ifd": self.ifd,
        }
