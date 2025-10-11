"""
EXIF image handling functionality.

This module provides classes for reading, modifying, and removing EXIF tags from
image files.
"""

from typing import Any, Iterable, Optional, Union

from tagkit.core.tag import ExifTag
from tagkit.core.registry import tag_registry
from tagkit.core.types import TagValue, FilePath, IfdName
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

    def write_tags(
        self,
        tags: dict[Union[str, int], TagValue],
        ifd: Optional[IfdName] = None,
    ):
        """
        Set multiple EXIF tags at once.

        Args:
            tags: A dictionary mapping tag names or IDs to values.
            ifd: Specific IFD to use for all tags (overrides default logic).

        Example:
            >>> exif = ExifImage('image1.jpg')
            >>> exif.write_tags({'Artist': 'Jane', 'Copyright': '2025 John'})
        """
        for tag, value in tags.items():
            self.write_tag(tag, value, ifd=ifd)

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
            ValueError: If the tag or IFD is invalid.

        Example:
            >>> exif = ExifImage('image10.jpg')
            >>> exif.delete_tag('Make', ifd='IFD0')
        """
        tag_id = tag_registry.resolve_tag_id(tag_key)
        if ifd is None:
            ifd = tag_registry.get_ifd(tag_id)
        # Only delete if present; do not raise if missing
        if (tag_id, ifd) in self._tag_dict:
            del self._tag_dict[tag_id, ifd]

    def delete_tags(
        self,
        tags: list[Union[str, int]],
        ifd: Optional[IfdName] = None,
    ):
        """
        Remove multiple EXIF tags at once.

        Args:
            tags: A list of tag names or tag IDs to remove.
            ifd: Specific IFD to use for all tags (overrides default logic).

        Example:
            >>> exif = ExifImage('image1.jpg')
            >>> exif.delete_tags(['Artist', 'Copyright'])
        """
        for tag in tags:
            self.delete_tag(tag, ifd=ifd)

    def read_tag(
        self,
        tag: Union[str, int],
        ifd: Optional[IfdName] = None,
        format_value: bool = False,
        binary_format: Optional[str] = None,
    ) -> Any:
        """
        Read the value of a specific EXIF tag.

        Args:
            tag: Tag name or tag ID.
            ifd: Specific IFD to use.
            format_value: If True, return formatted string value; if False, return raw value.
            binary_format: How to format binary data - 'bytes', 'hex', or 'base64'.
                Only used when format_value=True.

        Returns:
            The tag value (formatted or raw depending on format_value parameter).

        Raises:
            KeyError: If the tag is not present in the image.
            InvalidTagName, InvalidTagId: If the provided tag name or id is invalid.
            ValueError: If the tag or IFD is invalid or if `binary_format` is unsupported.

        Example:
            >>> exif = ExifImage('image1.jpg')
            >>> exif.read_tag('Make')
            'Tagkit'
            >>> exif.read_tag('Make', format_value=False)
            'Tagkit'
            >>> exif.read_tag('NonExistentTag')
            Traceback (most recent call last):
                ...
            tagkit.core.exceptions.InvalidTagName: 'NonExistentTag'
        """
        # Validate binary_format early to provide a clear error if invalid
        if binary_format is not None and binary_format not in (
            "bytes",
            "hex",
            "base64",
        ):
            raise ValueError(
                "binary_format must be one of 'bytes', 'hex', 'base64' or None"
            )

        tag_id = tag_registry.resolve_tag_id(tag)
        if ifd is None:
            ifd = tag_registry.get_ifd(tag_id)

        # Check if tag exists in the image
        if (tag_id, ifd) not in self._tag_dict:
            tag_name = tag_registry.resolve_tag_name(tag_id)
            raise KeyError(f"Tag '{tag_name}' not found in image")

        exif_tag = self._tag_dict[tag_id, ifd]

        if format_value:
            return exif_tag.format(binary_format=binary_format)
        return exif_tag.value

    def read_tags(
        self,
        tags: list[Union[str, int]],
        ifd: Optional[IfdName] = None,
        format_value: bool = False,
        binary_format: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Read multiple EXIF tags at once.

        Args:
            tags: A list of tag names or tag IDs to read.
            ifd: Specific IFD to use for all tags (overrides default logic).
            format_value: If True, return formatted string values; if False, return raw values.
            binary_format: How to format binary data - 'bytes', 'hex', or 'base64'.
                Only used when format_value=True.

        Returns:
            A dictionary mapping tag names to their values.
            Only tags that exist in the image are included in the result.

        Example:
            >>> exif = ExifImage('image1.jpg')
            >>> exif.read_tags(['Make', 'Model'])
            {'Make': 'Tagkit', 'Model': 'TestModel'}
        """
        from tagkit.core.exceptions import InvalidTagName, InvalidTagId

        # Validate binary_format early
        if binary_format is not None and binary_format not in (
            "bytes",
            "hex",
            "base64",
        ):
            raise ValueError(
                "binary_format must be one of 'bytes', 'hex', 'base64' or None"
            )

        result: dict[str, Any] = {}

        # Pre-resolve tag names and ids to avoid repeated lookups and to handle
        # invalid tags according to a single policy (skip silently here).
        resolved: list[tuple[Union[str, int], str]] = []
        for tag in tags:
            try:
                tag_name = tag_registry.resolve_tag_name(tag)
                # Keep original tag (for resolving id when reading) and resolved name
                resolved.append((tag, tag_name))
            except (ValueError, InvalidTagName, InvalidTagId):
                # Skip invalid/unknown tags
                continue

        for tag, tag_name in resolved:
            try:
                value = self.read_tag(
                    tag,
                    ifd=ifd,
                    format_value=format_value,
                    binary_format=binary_format,
                )
                if value is not None:
                    result[tag_name] = value
            except KeyError:
                # Tag not present in this image, skip
                continue
        return result

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
        if create_backup:
            import shutil

            shutil.copy2(self.file_path, self.file_path + ".bak")
        self._io_backend.save_tags(self.file_path, self._tag_dict)

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
