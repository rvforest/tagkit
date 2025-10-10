"""
Collection of EXIF image data for multiple files.

This module provides the ExifImageCollection class for working with EXIF data
from multiple image files.
"""

from datetime import datetime, timedelta
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
            {'image2.jpg': {'Make': {'id': 271, 'value': 'Tagkit', 'ifd': 'IFD0'}, 'DateTime': {'id': 306, 'value': '2025:05:02 14:30:00', 'ifd': 'IFD0'}}, 'image3.jpg': {'Make': {'id': 271, 'value': 'Tagkit', 'ifd': 'IFD0'}}}
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
            11
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

    def _normalize_filenames(self, files: Iterable[FilePath]) -> list[str]:
        """
        Normalize file names to string keys and validate their presence in the collection.

        Args:
            files: Iterable of file paths (can be strings or Path objects).

        Returns:
            List of normalized file names (strings).

        Raises:
            KeyError: If a file is not found in the collection.
        """
        normalized = []
        for fname in files:
            # Normalize fname to string key
            if isinstance(fname, Path):
                fname = fname.name
            if fname not in self.files:
                raise KeyError(f"File '{fname}' not found in collection.")
            normalized.append(fname)
        return normalized

    def write_tag(
        self,
        tag: Union[str, int],
        value: Any,
        ifd: Optional[IfdName] = None,
        files: Optional[Iterable[FilePath]] = None,
    ):
        """
        Set the value of a specific EXIF tag for all or selected images in the collection.

        Args:
            tag: Tag name or tag ID.
            value: Value to set.
            ifd: Specific IFD to use.
            files: Iterable of file names (keys in self.files) to update. If None, update all.

        Raises:
            KeyError: If a file is not found in the collection.
            ValueError: If the tag or IFD is invalid.

        Example:
            >>> from tagkit.image.collection import ExifImageCollection
            >>> collection = ExifImageCollection(["image1.jpg", "image2.jpg"])
            >>> collection.write_tag('Artist', 'John Doe', ifd='IFD0')
        """
        targets = (
            self.files.keys() if files is None else self._normalize_filenames(files)
        )
        for fname in targets:
            self.files[fname].write_tag(tag, value, ifd=ifd)

    def write_tags(
        self,
        tags: dict[Union[str, int], Any],
        ifd: Optional[IfdName] = None,
        files: Optional[Iterable[FilePath]] = None,
    ):
        """
        Set multiple EXIF tags for all or selected images in the collection.

        Args:
            tags: A dictionary mapping tag names or IDs to values.
            ifd: Specific IFD to use for all tags.
            files: Iterable of file names (keys in self.files) to update. If None, update all.

        Example:
            >>> collection = ExifImageCollection(["image1.jpg", "image2.jpg"])
            >>> collection.write_tags({'Artist': 'Jane', 'Copyright': '2025 John'})
        """
        targets = (
            self.files.keys() if files is None else self._normalize_filenames(files)
        )
        for fname in targets:
            self.files[fname].write_tags(tags, ifd=ifd)

    def delete_tag(
        self,
        tag_key: Union[str, int],
        ifd: Optional[IfdName] = None,
        files: Optional[Iterable[FilePath]] = None,
    ):
        """
        Remove a specific EXIF tag from all or selected images in the collection.
        If a file does not contain the tag, it is silently ignored.

        Args:
            tag_key: Tag name or tag ID.
            ifd: Specific IFD to use.
            files: Iterable of file names (keys in self.files) to update. If None, update all.

        Raises:
            KeyError: If a file is not found in the collection.
            ValueError: If the tag or IFD is invalid.

        Example:
            >>> from tagkit.image.collection import ExifImageCollection
            >>> collection = ExifImageCollection(["image1.jpg", "image2.jpg"])
            >>> collection.write_tag('Artist', 'John Doe', ifd='IFD0')
            >>> collection.delete_tag('Artist', ifd='IFD0')
        """
        targets = (
            self.files.keys() if files is None else self._normalize_filenames(files)
        )
        for fname in targets:
            try:
                self.files[fname].delete_tag(tag_key, ifd=ifd)
            except KeyError:
                pass  # Ignore if tag is missing

    def delete_tags(
        self,
        tags: list[Union[str, int]],
        ifd: Optional[IfdName] = None,
        files: Optional[Iterable[FilePath]] = None,
    ):
        """
        Remove multiple EXIF tags from all or selected images in the collection.
        If a file does not contain a tag, it is silently ignored.

        Args:
            tags: A list of tag names or tag IDs to remove.
            ifd: Specific IFD to use for all tags.
            files: Iterable of file names (keys in self.files) to update. If None, update all.

        Example:
            >>> collection = ExifImageCollection(["image1.jpg", "image2.jpg"])
            >>> collection.delete_tags(['Artist', 'Copyright'])
        """
        targets = (
            self.files.keys() if files is None else self._normalize_filenames(files)
        )
        for fname in targets:
            self.files[fname].delete_tags(tags, ifd=ifd)

    def save_all(self, create_backup: bool = False):
        """
        Save all modified EXIF data back to their respective image files.

        Args:
            create_backup: If True, create a backup of each file before saving.

        Example:
            >>> from tagkit.image.collection import ExifImageCollection
            >>> collection = ExifImageCollection(["image1.jpg", "image2.jpg"])
            >>> collection.write_tag('Artist', 'John Doe')
            >>> collection.save_all(create_backup=True)
        """
        for exif in self.files.values():
            exif.save(create_backup=create_backup)

    # DateTime operations

    def get_datetime(
        self,
        files: Optional[Iterable[FilePath]] = None,
        tag: Optional[str] = None,
        use_precedence: bool = True,
    ) -> dict[str, Optional[datetime]]:
        """
        Get datetime from EXIF tags for all or selected images in the collection.

        Args:
            files: Iterable of file names to query. If None, queries all files.
            tag: Optional specific datetime tag name to retrieve.
            use_precedence: If True and tag is None, uses precedence order.

        Returns:
            Dictionary mapping file names to datetime objects (or None if not found).

        Example:
            >>> collection = ExifImageCollection(['image1.jpg', 'image2.jpg'])
            >>> datetimes = collection.get_datetime()
            >>> for filename, dt in datetimes.items():
            ...     print(f"{filename}: {dt}")
            image1.jpg: 2025-05-01 14:30:00
            image2.jpg: 2025-05-02 14:30:00
        """
        targets = self.files.keys() if files is None else files
        result = {}

        for fname in targets:
            if isinstance(fname, Path):
                fname = fname.name
            if fname not in self.files:
                raise KeyError(f"File '{fname}' not found in collection.")
            result[fname] = self.files[fname].get_datetime(
                tag=tag, use_precedence=use_precedence
            )

        return result

    def set_datetime(
        self,
        dt: datetime,
        tags: Optional[list[str]] = None,
        files: Optional[Iterable[FilePath]] = None,
    ) -> None:
        """
        Set datetime EXIF tags for all or selected images (in-memory, not saved).

        Args:
            dt: Datetime object to set.
            tags: Optional list of specific datetime tag names to update. If None, updates all three datetime tags.
            files: Iterable of file names to update. If None, updates all files.

        Example:
            >>> from datetime import datetime
            >>> collection = ExifImageCollection(['image1.jpg', 'image2.jpg'])
            >>> collection.set_datetime(datetime(2025, 6, 15, 10, 30, 0))
            >>> collection.save_all()
        """
        targets = self.files.keys() if files is None else files

        for fname in targets:
            if isinstance(fname, Path):
                fname = fname.name
            if fname not in self.files:
                raise KeyError(f"File '{fname}' not found in collection.")
            self.files[fname].set_datetime(dt, tags=tags)

    def offset_datetime(
        self,
        delta: timedelta,
        tags: Optional[list[str]] = None,
        files: Optional[Iterable[FilePath]] = None,
    ) -> None:
        """
        Offset datetime EXIF tags by a timedelta for all or selected images (in-memory).

        Args:
            delta: Timedelta to add to existing datetime values.
            tags: Optional list of specific datetime tag names to offset. If None, offsets all present datetime tags.
            files: Iterable of file names to update. If None, updates all files.

        Example:
            >>> from datetime import timedelta
            >>> collection = ExifImageCollection(['image1.jpg', 'image2.jpg'])
            >>> collection.offset_datetime(timedelta(hours=-5))
            >>> collection.save_all()
        """
        targets = self.files.keys() if files is None else files

        for fname in targets:
            if isinstance(fname, Path):
                fname = fname.name
            if fname not in self.files:
                raise KeyError(f"File '{fname}' not found in collection.")
            self.files[fname].offset_datetime(delta, tags=tags)

    def get_all_datetimes(
        self, files: Optional[Iterable[FilePath]] = None
    ) -> dict[str, dict[str, datetime]]:
        """
        Get all datetime EXIF tags for all or selected images in the collection.

        Args:
            files: Iterable of file names to query. If None, queries all files.

        Returns:
            Dictionary mapping file names to dictionaries of datetime tags.

        Example:
            >>> collection = ExifImageCollection(['image1.jpg', 'image2.jpg'])
            >>> all_datetimes = collection.get_all_datetimes()
            >>> for filename, datetimes in all_datetimes.items():
            ...     print(f"{filename}:")
            ...     for tag_name, dt in datetimes.items():
            ...         print(f"  {tag_name}: {dt}")
            image1.jpg:
              DateTime: 2025-05-01 14:30:00
              DateTimeOriginal: 2025-05-01 14:30:00
            image2.jpg:
              DateTime: 2025-05-02 14:30:00
        """
        targets = self.files.keys() if files is None else files
        result = {}

        for fname in targets:
            if isinstance(fname, Path):
                fname = fname.name
            if fname not in self.files:
                raise KeyError(f"File '{fname}' not found in collection.")
            result[fname] = self.files[fname].get_all_datetimes()

        return result
