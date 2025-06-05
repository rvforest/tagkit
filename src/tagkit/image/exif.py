"""
EXIF image handling functionality.

This module provides classes for reading, modifying, and removing EXIF tags from
image files.
"""

from typing import Iterable, Optional, Union

import piexif

from tagkit.core.tag import ExifTag
from tagkit.core.registry import tag_registry
from tagkit.core.types import TagValue, FilePath, IfdName
from tagkit.core.utils import validate_single_arg_set
from tagkit.tag_io.base import ExifIOBackend
from tagkit.tag_io.piexif_io import PiexifBackend


class ExifImage:
    """
    Handler for reading, modifying, and removing EXIF tags from a single image file.

    Args:
        file_path: Path to the image file.
        tag_filter: Optional list of tag names or IDs to filter by
        thumbnail: If True, use thumbnail IFD
        ifd: Specific IFD to use
        io_backend: Custom backend for EXIF IO. Defaults to piexif.

    Example:
        >>> exif = ExifImage('image1.jpg')
        >>> exif.tags['Make']
        ExifTag(id=271, value='Tagkit', ifd='IFD0')
    """

    def __init__(
        self,
        file_path: FilePath,
        tag_filter: Optional[Iterable[Union[int, str]]] = None,
        thumbnail: Optional[bool] = None,
        ifd: Optional[IfdName] = None,
        io_backend: Optional[ExifIOBackend] = None,
    ):
        self.file_path = str(file_path)
        self.tag_filter = tag_filter
        self.thumbnail = thumbnail
        self.ifd = ifd
        if io_backend is None:
            io_backend = PiexifBackend()
        self._io_backend = io_backend

        self._tag_dict = self._io_backend.load_tags(file_path)

    def __len__(self) -> int:
        """Return the number of tags in this image."""
        return len(self.tags)

    def write_tag(
        self,
        tag: Union[str, int],
        value: TagValue,
        ifd: Optional[IfdName] = None,
    ):
        """
        Set the value of a specific EXIF tag.

        Args:
            tag: Tag name or tag ID.
            value: Value to set.
            ifd: Specific IFD to use.

        Raises:
            KeyError: If the tag is not found.
            ValueError: If the tag or IFD is invalid.

        Example:
            >>> exif = ExifImage('image1.jpg')
            >>> exif.write_tag('Artist', 'John Doe', ifd='IFD0')
        """
        if ifd is None:
            ifd = tag_registry.get_ifd(tag)
        tag_id = tag_registry.resolve_tag_id(tag)
        self._tag_dict[tag_id, ifd] = ExifTag(tag_id, value, ifd)

    def delete_tag(
        self,
        tag_key: Union[str, int],
        ifd: Optional[IfdName] = None,
    ):
        """
        Remove a specific EXIF tag if it exists.

        Args:
            tag_key: Tag name or tag ID.
            ifd: Specific IFD to use.

        Raises:
            KeyError: If the tag is not found.
            ValueError: If the tag or IFD is invalid.

        Example:
            >>> exif = ExifImage('image10.jpg')
            >>> exif.delete_tag('Make', ifd='IFD0')
        """
        tag_id = tag_registry.resolve_tag_id(tag_key)
        if ifd is None:
            ifd = tag_registry.get_ifd(tag_id)
        if (tag_id, ifd) not in self._tag_dict:
            raise KeyError(f"Tag '{tag_key}' not found in {self.file_path}")

        del self._tag_dict[tag_id, ifd]

    @property
    def tags(self) -> dict[str, ExifTag]:
        """
        Get the filtered tags based on tag_filter and ifd settings.

        Returns:
            dict: A dictionary of filtered tags with tag names as keys.
        """
        tag_filter_set = (
            {tag_registry.resolve_tag_id(tag) for tag in self.tag_filter}
            if self.tag_filter is not None
            else None
        )

        return {
            tag_registry.resolve_tag_name(tag_id): tag
            for (tag_id, ifd), tag in self._tag_dict.items()
            if (tag_filter_set is None or tag_id in tag_filter_set)
            and (self.ifd is None or ifd == self.ifd)
        }

    def save(self, create_backup: bool = False):
        """
        Write the modified EXIF data back to the image file.

        Raises:
            IOError: If writing to the file fails.
        """
        exif_bytes = piexif.dump(self._tag_dict)
        if create_backup:
            import shutil

            shutil.copy2(self.file_path, self.file_path + ".bak")
        piexif.insert(exif_bytes, self.file_path)

    def as_dict(
        self, binary_format: Optional[str] = None
    ) -> dict[str, dict[str, Union[str, int]]]:
        """
        Convert the image data to a nested dictionary structure.

        Args:
            binary_format: How to format binary data - 'bytes', 'hex', or 'base64'
                If None, <bytes: N> will be shown as a placeholder.

        Returns:
            dict: A nested dictionary containing the EXIF data for the image.

        Example:
            >>> exif = ExifImage('image2.jpg')
            >>> exif.as_dict()
            {'Make': {'id': 271, 'value': 'Tagkit', 'ifd': 'IFD0'}}
        """
        return {
            tag_name: {
                "id": tag.id,
                "value": tag.format(binary_format=binary_format),
                "ifd": tag.ifd,
            }
            for tag_name, tag in self.tags.items()
        }
