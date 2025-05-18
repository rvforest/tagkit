"""
Provides the ImageExifData class for reading, modifying, and removing EXIF tags from
a single image.

Example:
    >>> exif = ImageExifData('image.jpg')
    >>> exif.get_tag('Make')
    >>> exif.set_tag('Artist', 'John Doe')
    >>> exif.remove_tag('Artist')
"""

from typing import Iterable, Optional, Union

import piexif

from tagkit.tag_io.base import ExifIOBackend
from tagkit.tag_io.piexif_io import PiexifBackend
from tagkit.exif_entry import ExifEntry
from tagkit.tag_registry import tag_registry
from tagkit.types import ExifTag, FilePath, IfdName
from tagkit.utils import validate_single_arg_set


class ImageExifData:
    """
    Handler for reading, modifying, and removing EXIF tags from a single image file.

    Args:
        file_path (FilePath): Path to the image file.
        create_backup_on_mod (bool): If True, creates a backup before modifying the file.
        io_backend (Optional[ExifIOBackend]): Custom backend for EXIF IO. Defaults to piexif.

    Example:
        >>> exif = ImageExifData('image.jpg')
        >>> exif.get_tag('Make')
    """

    def __init__(
        self,
        file_path: FilePath,
        create_backup_on_mod: bool = False,
        io_backend: Optional[ExifIOBackend] = None,
    ):
        if io_backend is None:
            io_backend = PiexifBackend()

        self.file_path = str(file_path)
        self.create_backup = create_backup_on_mod
        self._io_backend = io_backend

        self.tags = self._io_backend.load_tags(file_path)

    def get_tag(
        self,
        tag_key: Union[int, str],
        thumbnail: bool = False,
        ifd: Optional[IfdName] = None,
    ) -> ExifEntry:
        """
        Get the value of a specific EXIF tag.

        Args:
            tag_key (Union[int, str]): Tag name or tag ID.
            thumbnail (bool): If True, get the tag from the thumbnail IFD.
            ifd (Optional[IfdName]): Specific IFD to use.

        Returns:
            ExifEntry: The EXIF entry for the tag.

        Raises:
            KeyError: If the tag is not found.
            ValueError: If the tag or IFD is invalid.

        Example:
            >>> exif.get_tag('Make')
        """
        validate_single_arg_set({"thumbnail": thumbnail, "ifd": ifd}, strict_none=False)

        # Convert tag names to tag id's
        tag_id = tag_registry.get_tag_id(tag_key)

        if thumbnail:
            ifd = "IFD1"
        if ifd is not None:
            return self.tags[tag_id, ifd]

        return self.tags[tag_id]

    def get_tags(
        self,
        tag_filter: Optional[Iterable[Union[int, str]]] = None,
        thumbnail: bool = False,
    ) -> dict[int, ExifEntry]:
        """
        Return all EXIF tags, optionally filtered by tag IDs or names.

        Args:
            tag_filter (Optional[Iterable[Union[int, str]]]): Tags to filter by.
            thumbnail (bool): If True, return tags from the thumbnail IFD.

        Returns:
            dict[int, ExifEntry]: Mapping of tag IDs to EXIF entries.

        Example:
            >>> exif.get_tags()
            >>> exif.get_tags(['Make', 'Model'])
        """
        # Convert tag names to tag IDs only if a filter is provided
        tag_filter_set = (
            {tag_registry.get_tag_id(tag) for tag in tag_filter}
            if tag_filter is not None
            else None
        )

        # Determine the IFD filter based on the thumbnail flag
        ifd_filter = "IFD1" if thumbnail else None

        # Filter tags
        return {
            tag_id: tag
            for (tag_id, ifd), tag in self.tags.items()
            if (tag_filter_set is None or tag_id in tag_filter_set)
            and (ifd_filter is None or ifd == ifd_filter)
        }

    def set_tag(
        self,
        tag: Union[str, int],
        value: ExifTag,
        thumbnail: bool = False,
        ifd: Optional[IfdName] = None,
    ):
        """
        Set the value of a specific EXIF tag.

        Args:
            tag (Union[str, int]): Tag name or tag ID.
            value (ExifTag): Value to set.
            thumbnail (bool): If True, set the tag in the thumbnail IFD.
            ifd (Optional[IfdName]): Specific IFD to use.

        Raises:
            KeyError: If the tag is not found.
            ValueError: If the tag or IFD is invalid.

        Example:
            >>> exif.set_tag('Artist', 'John Doe')
        """
        validate_single_arg_set({"thumbnail": thumbnail, "ifd": ifd}, strict_none=False)
        tag_id = tag_registry.get_tag_id(tag)
        if not ifd:
            ifd = tag_registry.get_ifd(tag_id, thumbnail=thumbnail)
        self.tags[tag_id, ifd] = ExifEntry(tag_id, value, ifd)
        self._save()

    def remove_tag(
        self,
        tag: Union[str, int],
        thumbnail: bool = False,
        ifd: Optional[IfdName] = None,
    ):
        """
        Remove a specific EXIF tag if it exists.

        Args:
            tag (Union[str, int]): Tag name or tag ID.
            thumbnail (bool): If True, remove the tag from the thumbnail IFD.
            ifd (Optional[IfdName]): Specific IFD to use.

        Raises:
            KeyError: If the tag is not found.
            ValueError: If the tag or IFD is invalid.

        Example:
            >>> exif.remove_tag('Artist')
        """
        validate_single_arg_set({"thumbnail": thumbnail, "ifd": ifd}, strict_none=False)
        tag_id = tag_registry.get_tag_id(tag)
        ifd = tag_registry.get_ifd(tag_id, thumbnail=thumbnail)

        del self.tags[tag_id, ifd]
        self._save()

    def _save(self):
        """
        Write the modified EXIF data back to the image file.

        Raises:
            IOError: If writing to the file fails.
        """
        exif_bytes = piexif.dump(self.tags)
        if self.create_backup:
            import shutil

            shutil.copy2(self.file_path, self.file_path + ".bak")
        piexif.insert(exif_bytes, self.file_path)
