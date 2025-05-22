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


class ImageCollection(dict):

    def __init__(
        self,
        files: list[FilePath],
    ):
        """
        Initialize an ImageCollection.
        
        Args:
            files: List of image file paths to include in the collection
        """
        super().__init__({file: ImageExifData(file) for file in files})

    def get_tag(
        self,
        tag: Union[int, str],
        *,
        file: Optional[FilePath] = None,
        thumbnail: Optional[bool] = None,
        ifd: Optional[IfdName] = None,
    ) -> dict[FilePath, ExifEntry]:
        """
        Get a single EXIF tag from one or all images in the collection.

        Args:
            tag: Tag name or tag ID to retrieve.
            file: If provided, get tag only from this file.
            thumbnail: If True, get the tag from the thumbnail IFD. 
                     If None, uses the instance default.
            ifd: Specific IFD to use. If None, uses the instance default.

        Returns:
            Dictionary mapping file paths to ExifEntry objects.

        Example:
            >>> # Get 'Make' tag from all images
            >>> makes = collection.get_tag('Make')
            >>> # Get 'Make' tag from a specific image
            >>> make = collection.get_tag('Make', file='image1.jpg')
        """
        result = self.get_tags(
            [tag], 
            file=file, 
            thumbnail=thumbnail, 
            ifd=ifd
        )
        return {path: tags[tag] for path, tags in result.items() if tag in tags}

    def get_tags(
        self,
        tags: Optional[list[Union[int, str]]] = None,
        *,
        file: Optional[FilePath] = None,
        thumbnail: Optional[bool] = None,
        ifd: Optional[IfdName] = None,
    ) -> dict[FilePath, dict[str, ExifEntry]]:
        """
        Get multiple EXIF tags from one or all images in the collection.

        Args:
            tags: List of tag names or tag IDs. If None, uses default_tags from __init__.
            file: If provided, get tags only from this file.
            thumbnail: If True, get tags from the thumbnail IFD. 
                     If None, uses the instance default.
            ifd: Specific IFD to use. If None, uses the instance default.

        Returns:
            If a specific file is provided, returns a dictionary mapping tag IDs to ExifEntry.
            Otherwise, returns a dictionary mapping file paths to dictionaries of tag data.

        Example:
            >>> # Get multiple tags from all images
            >>> tags = collection.get_tags(['Make', 'Model'])
            >>> # Get multiple tags from a specific image
            >>> image_tags = collection.get_tags(['Make', 'Model'], file='image1.jpg')
            >>> # Get all tags from all images
            >>> all_tags = collection.get_tags()
        """
        validate_single_arg_set({"thumbnail": thumbnail, "ifd": ifd}, strict_none=False)
        
        files = [file] if file is not None else self.keys()
        result = {}
        
        for path in files:
            try:
                if tags is None:
                    # Get all tags if none specified
                    result[path] = self[path].get_tags(thumbnail=thumbnail, ifd=ifd)
                else:
                    # Convert tag names to IDs
                    tag_ids = [tag_registry.get_tag_id(t) for t in tags]
                    result[path] = self[path].get_tags(tag_ids, thumbnail=thumbnail, ifd=ifd)
            except Exception:
                # Skip files that fail to load tags
                continue
                
        return result if file is None else next(iter(result.values()), {})
        
    def to_dict(
        self, 
        include_tags: Optional[list[Union[int, str]]] = None,
        *,
        thumbnail: Optional[bool] = None,
        ifd: Optional[IfdName] = None,
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
            >>> data = collection.to_dict(['Make', 'Model'])  # Get specific tags
            >>> data = collection.to_dict(thumbnail=True)  # Get from thumbnail IFD
        """
        # Use instance defaults if not overridden
        tags = include_tags if include_tags is not None else self.default_tags
        thumbnail = self.thumbnail if thumbnail is None else thumbnail
        ifd = self.default_ifd if ifd is None else ifd
        
        result = {}
        for file_path, exif_data in self.items():
            try:
                # Get tags using the instance defaults
                tags_dict = (
                    exif_data.get_tags(tags, thumbnail=thumbnail, ifd=ifd)
                    if tags is not None
                    else exif_data.get_tags(thumbnail=thumbnail, ifd=ifd)
                )
                
                # Convert ExifEntry objects to dictionaries
                result[str(file_path)] = {
                    tag_name: {
                        'value': entry.value,
                        'type': entry.type_name,
                        'display': str(entry)
                    }
                    for tag_name, entry in tags_dict.items()
                }
            except Exception:
                # Skip files that fail to load
                continue
                
        return result



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
        *,
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
        *,
        thumbnail: bool = False,
    ) -> dict[str, ExifEntry]:
        """
        Return all EXIF tags, optionally filtered by tag IDs or names.

        Args:
            tag_filter (Optional[Iterable[Union[int, str]]]): Tags to filter by.
            thumbnail (bool): If True, return tags from the thumbnail IFD.

        Returns:
            dict[str, ExifEntry]: Mapping of tag names to EXIF entries.

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
            tag_registry.get_tag_name(tag_id): tag
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
        tag_id, ifd = self._get_tag_id_and_ifd(tag, thumbnail, ifd)

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
