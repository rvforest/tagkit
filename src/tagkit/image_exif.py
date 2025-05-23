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


class ExifImageCollection:
    def __init__(
        self,
        files: Iterable[FilePath],
        *,
        tag_filter: Optional[list[Union[int, str]]] = None,
        thumbnail: Optional[bool] = None,
        ifd: Optional[IfdName] = None,
        create_backup_on_mod: bool = False,
    ):
        """
        Initialize an ImageCollection.

        Args:
            files: List of image file paths to include in the collection
        """
        self.tag_filter = tag_filter
        self.thumbnail = thumbnail
        self.ifd = ifd
        self.files = {
            file: ImageExifData(
                file,
                tag_filter=tag_filter,
                thumbnail=thumbnail,
                ifd=ifd,
                create_backup_on_mod=create_backup_on_mod,
            )
            for file in files
        }

    def to_dict(
        self, render_bytes: bool = True, binary_format: Optional[str] = None
    ) -> dict[str, dict[str, dict]]:
        """
        Convert the image collection to a nested dictionary structure.

        The structure is:
        {
            'file1.jpg': {
                'Make': {
                    'value': 'Canon',
                    'type': 'Ascii',
                    'display': 'Canon'
                },
                'Model': {
                    'value': 'EOS 5D Mark IV',
                    'type': 'Ascii',
                    'display': 'EOS 5D Mark IV'
                },
                ...
            },
            'file2.jpg': {
                ...
            },
            ...
        }

        Args:
            include_tags: List of tag names or IDs to include. If None, uses default_tags from __init__.
            thumbnail: If True, get tags from the thumbnail IFD.
                     If None, uses the instance default.
            ifd: Specific IFD to use. If None, uses the instance default.

        Returns:
            dict: A nested dictionary containing the EXIF data for all images in the collection.

        Example:
            >>> collection = ImageCollection(['image1.jpg', 'image2.jpg'])
            >>> data = collection.to_dict()  # Get default tags for all images
        """
        # Use instance defaults if not overridden
        return {
            str(file_path): exif_data.to_dict(render_bytes, binary_format)
            for file_path, exif_data in self.files.items()
        }

    def n_files(self) -> int:
        """
        Return the number of files in the collection.
        """
        return len(self.files)

    def n_tags(self) -> int:
        """
        Return the total number of tags in the collection.
        """
        return sum(len(exif_data.tags) for exif_data in self.files.values())


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
        tag_filter: Optional[Iterable[Union[int, str]]] = None,
        thumbnail: Optional[bool] = None,
        ifd: Optional[IfdName] = None,
        create_backup_on_mod: bool = False,
        io_backend: Optional[ExifIOBackend] = None,
    ):
        self.file_path = str(file_path)
        self.tag_filter = tag_filter
        self.thumbnail = thumbnail
        self.ifd = ifd
        self.create_backup = create_backup_on_mod
        if io_backend is None:
            io_backend = PiexifBackend()
        self._io_backend = io_backend

        self._tag_dict = self._io_backend.load_tags(file_path)

    def __len__(self) -> int:
        return len(self.tags)

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
        self._tag_dict[tag_id, ifd] = ExifEntry(tag_id, value, ifd)
        self._save()

    def remove_tag(
        self,
        tag_key: Union[str, int],
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
        tag_id = tag_registry.get_tag_id(tag_key)
        ifd = tag_registry.get_ifd(tag_id, thumbnail=thumbnail)

        del self._tag_dict[tag_id, ifd]
        self._save()

    @property
    def tags(self) -> dict[str, ExifEntry]:
        """
        Get the filtered tags based on tag_filter and ifd settings.

        Returns:
            dict: A dictionary of filtered tags with tag names as keys.
        """
        tag_filter_set = (
            {tag_registry.get_tag_id(tag) for tag in self.tag_filter}
            if self.tag_filter is not None
            else None
        )

        return {
            tag_registry.get_tag_name(tag_id): tag
            for (tag_id, ifd), tag in self._tag_dict.items()
            if (tag_filter_set is None or tag_id in tag_filter_set)
            and (self.ifd is None or ifd == self.ifd)
        }

    def _save(self):
        """
        Write the modified EXIF data back to the image file.

        Raises:
            IOError: If writing to the file fails.
        """
        exif_bytes = piexif.dump(self._tag_dict)
        if self.create_backup:
            import shutil

            shutil.copy2(self.file_path, self.file_path + ".bak")
        piexif.insert(exif_bytes, self.file_path)

    def to_dict(
        self, render_bytes: bool = True, binary_format: Optional[str] = None
    ) -> dict[str, dict[str, dict]]:
        """
        Convert the image data to a nested dictionary structure.

        Returns:
            dict: A nested dictionary containing the EXIF data for the image.
        """
        return {
            tag_name: tag.to_dict(render_bytes, binary_format)
            for tag_name, tag in self.tags.items()
        }
