from typing import Union, cast
import piexif

from tagkit.tag_io.base import ExifIOBackend, ExifTagDict
from tagkit.core.tag import ExifTag
from tagkit.core.registry import tag_registry
from tagkit.core.types import TagValue, FilePath, IfdName, Literal

# While the exif standard only allows ascii, utf-8 is commonly used
STR_ENCODING = "utf-8"

PiexifIfdName = Literal["0th", "1st", "Exif", "GPS", "Interop"]
PiexifTags = dict[PiexifIfdName, dict[int, TagValue]]


tagkit_to_piexif_ifd_map: dict[IfdName, PiexifIfdName] = {
    "IFD0": "0th",
    "IFD1": "1st",
    "GPS": "GPS",
    "Exif": "Exif",
    "Interop": "Interop",
}


class PiexifBackend(ExifIOBackend):
    def load_tags(self, image_path: FilePath) -> ExifTagDict:
        raw_exif = piexif.load(str(image_path))
        raw_exif = cast(PiexifTags, raw_exif)
        conformed_dict = _conform_ifd_names(raw_exif)
        result_dict = {}
        for ifd, ifd_tags in conformed_dict.items():
            for tag_id, val in ifd_tags.items():
                # Decode if ascii
                val = (
                    cast(bytes, val).decode(STR_ENCODING)
                    if _tag_is_ascii(tag_id)
                    else val
                )
                result_dict[tag_id, ifd] = ExifTag(tag_id, val, ifd)

        return ExifTagDict(result_dict)

    def save_tags(self, image_path: FilePath, tags: ExifTagDict) -> None:
        """
        Save EXIF tags to an image file using the piexif library.

        This method converts tagkit's internal tag representation to the format
        expected by piexif, then writes the tags to the specified image file.

        Args:
            image_path: Path to the image file
            tags: Dictionary of EXIF tags to save
        """
        # Initialize the piexif data structure (nested dictionaries by IFD)
        piexif_data: dict[PiexifIfdName, dict[int, TagValue]] = {
            piexif_ifd: {} for piexif_ifd in tagkit_to_piexif_ifd_map.values()
        }

        # Process each tag from the tagkit dictionary
        for tag in tags.values():
            # Get the corresponding piexif IFD name (e.g., "IFD0" -> "0th")
            if tag.ifd not in tagkit_to_piexif_ifd_map:
                raise ValueError(
                    f"Unknown IFD '{tag.ifd}' for tag ID {tag.id}. "
                    f"Known IFDs: {', '.join(tagkit_to_piexif_ifd_map.keys())}"
                )

            piexif_ifd = tagkit_to_piexif_ifd_map[tag.ifd]

            # Prepare the tag value - encode strings for ASCII tags
            tag_value = tag.value
            if _tag_is_ascii(tag.id) and isinstance(tag_value, str):
                tag_value = cast(str, tag_value).encode(STR_ENCODING)

            # Add the tag to the piexif data structure
            piexif_data[piexif_ifd][tag.id] = tag_value

        # Convert the structured data to EXIF bytes
        exif_bytes = piexif.dump(piexif_data)

        # Write the EXIF data to the image file
        piexif.insert(exif_bytes, str(image_path))


def _tag_is_ascii(tag: Union[ExifTag, int]) -> bool:
    if isinstance(tag, ExifTag):
        tag = tag.id
    return tag_registry.get_exif_type(tag) == "ASCII"


def _conform_ifd_names(raw_piexif: PiexifTags) -> dict[IfdName, dict[int, TagValue]]:
    # Rename IFD to match tagkit standards.
    output: dict[IfdName, dict[int, TagValue]] = {}
    for tagkit_key, piexif_key in tagkit_to_piexif_ifd_map.items():
        if piexif_key in raw_piexif:
            output[tagkit_key] = raw_piexif[piexif_key]

    return output
