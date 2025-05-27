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
        # Organize tags back into the piexif structure
        exif_dict: dict[PiexifIfdName, dict[int, ExifTag]] = {
            ifd: {} for ifd in tagkit_to_piexif_ifd_map.values()
        }
        for tag in tags.values():
            if tag.ifd in exif_dict:
                # Encode if ascii
                val = (
                    cast(str, tag.value).encode(STR_ENCODING)
                    if _tag_is_ascii(tag) and isinstance(tag.value, str)
                    else tag.value
                )
                piexif_ifd = tagkit_to_piexif_ifd_map[tag.ifd]
                exif_dict[piexif_ifd][tag.id] = val

        exif_bytes = piexif.dump(exif_dict)
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
