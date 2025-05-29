"""
Collection of EXIF image data for multiple files.

This module provides the ExifImageCollection class for working with EXIF data
from multiple image files.
"""

from typing import Dict, Any, Optional, Union, Iterable

from tagkit.core.types import FilePath, IfdName
from tagkit.image.exif import ExifImage


class ExifImageCollection:
    """
    A collection of EXIF data for multiple image files.

    This class provides a convenient way to access EXIF data from multiple files.

    Args:
        files: List of paths to image files
        tag_filter: Optional list of tag names or IDs to filter by
        thumbnail: If True, use thumbnail IFD
        ifd: Specific IFD to use
        create_backup_on_mod: If True, create backups before modifying files

    Attributes:
        files (Dict[str, ExifImage]): Dictionary mapping file paths to their EXIF data.
    """

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
        Initialize the collection with a list of file paths.

        Args:
            files: List of paths to image files
            tag_filter: Optional list of tag names or IDs to filter by
            thumbnail: If True, use thumbnail IFD
            ifd: Specific IFD to use
            create_backup_on_mod: If True, create backups before modifying files
        """
        self.tag_filter = tag_filter
        self.thumbnail = thumbnail
        self.ifd = ifd
        self.files: Dict[str, ExifImage] = {}

        for path in files:
            path_str = str(path)
            self.files[path_str] = ExifImage(
                path,
                tag_filter=tag_filter,
                thumbnail=thumbnail,
                ifd=ifd,
                create_backup_on_mod=create_backup_on_mod,
            )

    def as_dict(self, binary_format: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert the collection to a dictionary.

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
            binary_format: Format for binary data ('hex', 'base64', or None for default).
                If None, <bytes: N> will be shown as a placeholder.

        Returns:
            Dictionary mapping file paths to their EXIF data dictionaries.

        Example:
            >>> collection = ExifImageCollection(['image1.jpg', 'image2.jpg'])
            >>> data = collection.as_dict()  # Get default tags for all images
        """
        return {
            path: exif.as_dict(binary_format=binary_format)
            for path, exif in self.files.items()
        }

    @property
    def n_tags(self) -> int:
        """
        Get the total number of tags across all files.

        Returns:
            Total number of tags.
        """
        return sum(len(exif) for exif in self.files.values())

    @property
    def n_files(self) -> int:
        """
        Get the number of files in the collection.

        Returns:
            Number of files.
        """
        return len(self.files)
