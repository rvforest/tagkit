from dataclasses import dataclass

from tagkit.tag_registry import tag_registry
from tagkit.types import ExifTag, ExifType, IfdName
from tagkit.value_formatting import TagValueFormatter


@dataclass
class ExifEntry:
    id: int
    value: ExifTag
    ifd: IfdName

    def __post_init__(self):
        self.formatter = TagValueFormatter.from_yaml()

    @property
    def name(self) -> str:
        return tag_registry.get_tag_name(self.id)

    @property
    def exif_type(self) -> ExifType:
        return tag_registry.get_exif_type(self.id)

    @property
    def formatted_value(self) -> str:
        return self.formatter.format(self)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "value": self.formatted_value,
            "ifd": self.ifd,
        }
        