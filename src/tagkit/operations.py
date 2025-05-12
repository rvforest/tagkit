from typing import Iterable, Optional, Union

from tagkit.exif_entry import ExifEntry
from tagkit.image_exif import ImageExifData
from tagkit.types import FilePath


def get_exif(
    file_paths: Iterable[FilePath],
    tag_filter: Optional[Iterable[Union[str, int]]] = None,
    thumbnail: bool = False,
) -> dict[str, dict[int, ExifEntry]]:
    """
    Get EXIF data for one or more image files.

    Args:
        file_paths (Iterable[FilePath]): Paths to image files.
        tag_filter (Optional[Iterable[Union[str, int]]]): Tags to filter by (names or IDs).
        thumbnail (bool): If True, get tags from the thumbnail IFD.

    Returns:
        dict[str, dict[int, ExifEntry]]: Mapping from file path to tag ID to EXIF entry.

    Example:
        >>> get_exif(['img1.jpg', 'img2.jpg'], tag_filter=['Make', 'Model'])
    """
    # Convert any tag names to tag id's in tag_filter
    result = {
        str(path): ImageExifData(path).get_tags(tag_filter, thumbnail)
        for path in file_paths
    }
    return result
