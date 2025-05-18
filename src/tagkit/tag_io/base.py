from abc import ABC, abstractmethod
from typing import Mapping, Optional, Union, overload

from tagkit.exif_entry import ExifEntry
from tagkit.types import FilePath


class ExifTagDict(dict):
    """
    A dictionary for EXIF tag values indexed by (tag_id, ifd_name) tuples.

    This subclass of `dict` allows accessing EXIF tag values using either the full key
    as a tuple `(tag_id, ifd_name)` or just the `tag_id`. When only a `tag_id` is
    provided, the lookup will succeed only if there is exactly one key in the dictionary
    that matches that `tag_id` across all IFDs. Otherwise, a KeyError is raised to
    signal ambiguity or absence.

    Key Format:
        Keys must be tuples of the form (tag_id: int, ifd_name: str).
        Values must be ExifEntry instances representing the associated tag value.

    Examples:
        >>> exif = ExifTagDict()
        >>> exif[(256, '0th')] = ExifEntry(256, 1024, '0th')
        >>> exif[(256, 'Exif')] = ExifEntry(256, 2048, 'Exif')
        >>> exif[(257, '0th')] = ExifEntry(257, 768, '0th')

        >>> exif[256, '0th']
        ExifEntry(...)

        >>> exif[257]
        ExifEntry(...)

        >>> exif[256]
        KeyError: "Ambiguous tag_id 256; multiple matches: [(256, '0th'), (256, 'Exif')]"

    Raises:
        KeyError: If the tag_id is not found or matches multiple IFD entries.
        TypeError: If the key or value types are invalid.
    """

    def __init__(
        self, data: Optional[Mapping[tuple[int, str], ExifEntry]] = None, **kwargs
    ):
        if kwargs:
            raise AttributeError(kwargs)
        super().__init__()
        if data:
            self.update(data)

    @overload
    def __getitem__(self, key: tuple[int, str]) -> ExifEntry: ...

    @overload
    def __getitem__(self, key: int) -> ExifEntry: ...

    def __getitem__(self, key: Union[int, tuple[int, str]]) -> ExifEntry:
        """
        Retrieve an EXIF entry by (tag_id, ifd_name) tuple or by tag_id only.

        Args:
            key (Union[int, tuple[int, str]]): The key to look up. If int, must be unique.

        Returns:
            ExifEntry: The EXIF entry for the given key.

        Raises:
            KeyError: If the tag_id is not found or is ambiguous.
        """
        if isinstance(key, tuple):
            return super().__getitem__(key)

        matches = [
            (k, v)
            for k, v in self.items()
            if isinstance(k, tuple) and len(k) == 2 and k[0] == key
        ]

        if not matches:
            raise KeyError(f"No tag found with tag_id {key}")
        elif len(matches) > 1:
            raise KeyError(
                f"Ambiguous tag_id {key}; multiple matches: {[k for k, _ in matches]}"
            )

        return matches[0][1]

    def __setitem__(self, key: tuple[int, str], value: ExifEntry):
        """
        Set an EXIF entry for a (tag_id, ifd_name) tuple.

        Args:
            key (tuple[int, str]): The key tuple.
            value (ExifEntry): The EXIF entry to set.

        Raises:
            TypeError: If the key or value types are invalid.
        """
        if not isinstance(value, ExifEntry):
            raise TypeError(
                f"Value must be an ExifEntry instance, got {type(value).__name__}"
            )
        if not (
            isinstance(key, tuple)
            and len(key) == 2
            and isinstance(key[0], int)
            and isinstance(key[1], str)
        ):
            raise TypeError(
                "Key must be a tuple of the form (tag_id: int, ifd_name: str)"
            )
        super().__setitem__(key, value)

    def update(self, *args, **kwargs):
        """
        Update the dictionary with another dictionary of EXIF entries.

        Raises:
            NotImplementedError: If called with unsupported arguments.
        """
        if len(args) == 0 and not kwargs:
            # Allow update() with no arguments
            return super().update()
        elif len(args) == 1 and isinstance(args[0], dict) and not kwargs:
            # Allow update(dict)
            return super().update(args[0])
        else:
            raise NotImplementedError("Update only takes a dict or no arguments")


class ExifIOBackend(ABC):
    """
    Abstract base class for EXIF IO backends.
    """

    @abstractmethod
    def load_tags(self, image_path: FilePath) -> ExifTagDict:
        """
        Load EXIF tags from an image file.

        Args:
            image_path (FilePath): Path to the image file.

        Returns:
            ExifTagDict: Dictionary of EXIF tags.
        """
        pass  # pragma: no cover

    @abstractmethod
    def save_tags(self, image_path: FilePath, tags: ExifTagDict) -> None:
        """
        Save EXIF tags to an image file.

        Args:
            image_path (FilePath): Path to the image file.
            tags (ExifTagDict): Dictionary of EXIF tags to save.
        """
        pass  # pragma: no cover
