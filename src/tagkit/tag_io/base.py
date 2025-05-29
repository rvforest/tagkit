from abc import ABC, abstractmethod

from tagkit.core.tag import ExifTag
from tagkit.core.types import FilePath, IfdName

ExifTagDict = dict[tuple[int, IfdName], ExifTag]


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
