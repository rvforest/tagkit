"""
Collection of EXIF image data for multiple files.

This module provides the ExifImageCollection class for working with EXIF data
from multiple image files.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Union, Iterable

from tagkit.core.types import FilePath, IfdName
from tagkit.core.registry import tag_registry
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

    def read_tag(
        self,
        tag: Union[str, int],
        ifd: Optional[IfdName] = None,
        format_value: bool = False,
        binary_format: Optional[str] = None,
        files: Optional[Iterable[FilePath]] = None,
        skip_missing: bool = False,
        default: Any = None,
        raise_on_missing: bool = True,
    ) -> dict[str, Any]:
        """
        Read the value of a specific EXIF tag from all or selected images in the collection.

        Args:
            tag: Tag name or tag ID.
            ifd: Specific IFD to use.
            format_value: If True, return formatted string values; if False, return raw values.
            binary_format: How to format binary data - 'bytes', 'hex', or 'base64'.
                Only used when format_value=True.
            files: Iterable of file names (keys in self.files) to read from. If None, read from all.
            skip_missing: If True, skip files where the tag is missing; if False, use default or raise.
            default: Default value to return for missing tags (only when raise_on_missing=False).
            raise_on_missing: If True, raise KeyError when tag is missing in any file;
                if False, return default for missing tags.

        Returns:
            A dictionary mapping file names to tag values.

        Raises:
            KeyError: If a file is not found in the collection, or if a tag is missing
                (when raise_on_missing=True and skip_missing=False).
            ValueError: If the tag or IFD is invalid.

        Example:
            >>> from tagkit.image.collection import ExifImageCollection
            >>> collection = ExifImageCollection(["image1.jpg", "image2.jpg"])
            >>> collection.read_tag('Make')
            {'image1.jpg': 'Tagkit', 'image2.jpg': 'Tagkit'}
            >>> collection.read_tag('Artist', skip_missing=True)
            {}
        """
        targets = (
            self.files.keys() if files is None else self._normalize_filenames(files)
        )
        result = {}
        for fname in targets:
            try:
                value = self.files[fname].read_tag(
                    tag,
                    ifd=ifd,
                    format_value=format_value,
                    binary_format=binary_format,
                    default=default,
                    raise_on_missing=raise_on_missing,
                )
                if not skip_missing or value != default:
                    result[fname] = value
            except KeyError:
                if not skip_missing:
                    raise
        return result

    def read_tags(
        self,
        tags: list[Union[str, int]],
        ifd: Optional[IfdName] = None,
        format_value: bool = False,
        binary_format: Optional[str] = None,
        files: Optional[Iterable[FilePath]] = None,
        skip_missing: bool = False,
        per_image: bool = False,
    ) -> Union[dict[str, dict[str, Any]], dict[str, Any]]:
        """
        Read multiple EXIF tags from all or selected images in the collection.

        Args:
            tags: A list of tag names or tag IDs to read.
            ifd: Specific IFD to use for all tags.
            format_value: If True, return formatted string values; if False, return raw values.
            binary_format: How to format binary data - 'bytes', 'hex', or 'base64'.
                Only used when format_value=True.
            files: Iterable of file names (keys in self.files) to read from. If None, read from all.
            skip_missing: If True, skip missing tags; if False, only include tags that exist.
            per_image: If True, return data organized by image (nested dict);
                if False, return data organized by tag name.

        Returns:
            If per_image=False (default): Dictionary mapping tag names to dictionaries
                of file names to values: {'Make': {'image1.jpg': 'Canon', 'image2.jpg': 'Nikon'}}
            If per_image=True: Dictionary mapping file names to dictionaries
                of tag names to values: {'image1.jpg': {'Make': 'Canon', 'Model': 'EOS'}}

        Raises:
            KeyError: If a file is not found in the collection.
            ValueError: If a tag or IFD is invalid.

        Example:
            >>> from tagkit.image.collection import ExifImageCollection
            >>> collection = ExifImageCollection(["image1.jpg", "image2.jpg"])
            >>> collection.read_tags(['Make', 'Model'])
            {'Make': {'image1.jpg': 'Tagkit', 'image2.jpg': 'Tagkit'}, 'Model': {'image1.jpg': 'TestModel', 'image2.jpg': 'TestModel'}}
            >>> collection.read_tags(['Make', 'Model'], per_image=True)
            {'image1.jpg': {'Make': 'Tagkit', 'Model': 'TestModel'}, 'image2.jpg': {'Make': 'Tagkit', 'Model': 'TestModel'}}
        """
        from tagkit.core.exceptions import InvalidTagName, InvalidTagId

        targets = (
            self.files.keys() if files is None else self._normalize_filenames(files)
        )

        if per_image:
            # Return data organized by image
            result: dict[str, Any] = {}
            for fname in targets:
                result[fname] = self.files[fname].read_tags(
                    tags,
                    ifd=ifd,
                    format_value=format_value,
                    binary_format=binary_format,
                )
            return result
        else:
            # Return data organized by tag
            result = {}
            for tag in tags:
                try:
                    tag_id = tag_registry.resolve_tag_id(tag)
                    tag_name = tag_registry.resolve_tag_name(tag_id)
                    result[tag_name] = {}
                    for fname in targets:
                        value = self.files[fname].read_tag(
                            tag,
                            ifd=ifd,
                            format_value=format_value,
                            binary_format=binary_format,
                            raise_on_missing=False,
                        )
                        if value is not None or not skip_missing:
                            result[tag_name][fname] = value
                except (ValueError, KeyError, InvalidTagName, InvalidTagId):
                    # Skip invalid tags
                    pass
            return result
