"""
Collection of EXIF image data for multiple files.

This module provides the ExifImageCollection class for working with EXIF data
from multiple image files.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union, Iterable

from tagkit.core.types import FilePath, IfdName
from tagkit.image.exif import ExifImage


class ExifImageCollection:
    """
    A collection of EXIF data for multiple image files.

    This class provides a convenient way to access EXIF data from multiple files.

    Args:
        files: List of paths to image files.
        tag_filter: Optional list of tag names or IDs to filter by.
        ifd: Specific IFD to use.

    Attributes:
        files (Dict[str, ExifImage]): Dictionary mapping file paths to their EXIF data.
    """

    def __init__(
        self,
        files: Iterable[FilePath],
        *,
        tag_filter: Optional[list[Union[int, str]]] = None,
        ifd: Optional[IfdName] = None,
    ):
        """
        Initialize the collection with a list of file paths.

        Args:
            files: List of paths to image files.
            tag_filter: Optional list of tag names or IDs to filter by.
            ifd: Specific IFD to use.
        """
        self.tag_filter = tag_filter
        self.ifd = ifd
        self.files: Dict[str, ExifImage] = {}

        for path in files:
            self.files[Path(path).name] = ExifImage(
                path,
                tag_filter=tag_filter,
                ifd=ifd,
            )

    def as_dict(self, binary_format: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert the collection to a dictionary.

        Args:
            binary_format: Format for binary data ('hex', 'base64', or None for default).
                If None, <bytes: N> will be shown as a placeholder.

        Returns:
            Dictionary mapping file paths to their EXIF data dictionaries.

        Example:
            >>> collection = ExifImageCollection(["image2.jpg", "image3.jpg"])
            >>> collection.as_dict()
            {'image2.jpg': {'Make': {'id': 271, 'value': 'Tagkit', 'ifd': 'IFD0'}}, 'image3.jpg': {'Make': {'id': 271, 'value': 'Tagkit', 'ifd': 'IFD0'}}}
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

        Example:
            >>> collection = ExifImageCollection(["image1.jpg", "image2.jpg"])
            >>> collection.n_tags
            9
        """
        return sum(len(exif) for exif in self.files.values())

    @property
    def n_files(self) -> int:
        """
        Get the number of files in the collection.

        Returns:
            Number of files.

        Example:
            >>> collection = ExifImageCollection(["image1.jpg", "image2.jpg"])
            >>> collection.n_files
            2
        """
        return len(self.files)
