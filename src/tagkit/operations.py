from typing import Iterable, Optional, Union

from tagkit.image_exif import ImageCollection
from tagkit.types import FilePath


def get_exif(
    file_paths: Iterable[FilePath],
    tag_filter: Optional[Iterable[Union[str, int]]] = None,
    thumbnail: bool = False,
) -> ImageCollection:
    """
    Get EXIF data for one or more image files.

    Args:
        file_paths (Iterable[FilePath]): Paths to image files.
        tag_filter (Optional[Iterable[Union[str, int]]]): Tags to filter by (names or IDs).
        thumbnail (bool): If True, get tags from the thumbnail IFD.

    Returns:
        ImageCollection: Collection of EXIF data for the given files.

    Example:
        >>> get_exif(['img1.jpg', 'img2.jpg'], tag_filter=['Make', 'Model'])
    """
    # Convert any tag names to tag id's in tag_filter
    return ImageCollection(file_paths, tag_filter=tag_filter, thumbnail=thumbnail)
