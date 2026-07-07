"""
Registry of EXIF tags and their metadata.

This module provides the ExifRegistry class which maintains information about
supported EXIF tags, their IFD-aware identities, names, types, and counts.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypedDict, Union

from typing_extensions import Self

import yaml

from tagkit.conf.models import RegistryConfig
from tagkit.core.exceptions import AmbiguousTagKey, InvalidTagId, InvalidTagName
from tagkit.core.types import ExifCount, ExifType, IfdName


class RegistryConfValue(TypedDict, total=False):
    name: str
    type: ExifType | list[ExifType]
    count: ExifCount | None


RegistryConfKey = Literal["Image", "Exif", "GPS", "Interop"]
RegistryConf = dict[RegistryConfKey, dict[int, RegistryConfValue]]


@dataclass(frozen=True)
class ExifTagDefinition:
    """IFD-aware EXIF tag definition."""

    ifd: IfdName
    tag_id: int
    name: str
    allowed_types: tuple[ExifType, ...]
    count: ExifCount | None = None

    @property
    def exif_type(self) -> ExifType:
        """Return the primary EXIF type for compatibility helpers."""
        return self.allowed_types[0]


def _registry_ifd_to_tagkit_ifd(ifd: RegistryConfKey) -> IfdName:
    return "IFD0" if ifd == "Image" else ifd


def _tagkit_ifd_to_registry_ifd(ifd: IfdName) -> RegistryConfKey:
    if ifd in ("IFD0", "IFD1"):
        return "Image"
    if ifd == "Exif":
        return "Exif"
    if ifd == "GPS":
        return "GPS"
    return "Interop"


class ExifRegistry:
    """
    Registry of all EXIF tags compatible with tagkit.

    Args:
        registry_conf: The EXIF tag registry configuration.
    """

    def __init__(self, registry_conf: RegistryConf):
        self.tags_by_ifd = registry_conf

        self._definitions_by_key: dict[
            tuple[RegistryConfKey, int], ExifTagDefinition
        ] = {}
        self._definitions_by_name: dict[str, list[ExifTagDefinition]] = {}
        self._definitions_by_id: dict[int, list[ExifTagDefinition]] = {}

        for registry_ifd, ifd_tags in self.tags_by_ifd.items():
            tagkit_ifd = _registry_ifd_to_tagkit_ifd(registry_ifd)
            for tag_id, tag in ifd_tags.items():
                raw_type = tag["type"]
                allowed_types = (
                    tuple(raw_type) if isinstance(raw_type, list) else (raw_type,)
                )
                definition = ExifTagDefinition(
                    ifd=tagkit_ifd,
                    tag_id=tag_id,
                    name=tag["name"],
                    allowed_types=allowed_types,
                    count=tag.get("count"),
                )
                self._definitions_by_key[registry_ifd, tag_id] = definition
                self._definitions_by_name.setdefault(definition.name, []).append(
                    definition
                )
                self._definitions_by_id.setdefault(definition.tag_id, []).append(
                    definition
                )

    @classmethod
    def from_yaml(cls, path: Union[Path, str, None] = None) -> Self:
        """
        Load the EXIF tag registry from a YAML file.

        Args:
            path: Path to the YAML file. If None, uses default.

        Returns:
            The loaded registry instance.
        """
        if path is None:
            here = Path(__file__).parents[1]
            path = here / "conf/registry.yaml"
        with open(path, "r") as f:
            raw_conf = yaml.safe_load(f)

        validated_conf = RegistryConfig.model_validate(raw_conf)
        conf: RegistryConf = validated_conf.model_dump(exclude_defaults=True)  # type: ignore
        return cls(conf)

    @property
    def tag_names(self) -> list[str]:
        """
        List all unique tag names in the registry.

        Returns:
            All tag names.
        """
        return list(self._definitions_by_name)

    def get_definition(
        self, tag_key: Union[int, str], ifd: IfdName | None = None
    ) -> ExifTagDefinition:
        """
        Resolve an IFD-aware tag definition.

        If ``ifd`` is omitted, the lookup succeeds only when the tag key maps to
        exactly one definition.
        """
        if ifd is not None:
            registry_ifd = _tagkit_ifd_to_registry_ifd(ifd)
            tag_id = self.resolve_tag_id(tag_key, ifd=ifd)
            try:
                definition = self._definitions_by_key[registry_ifd, tag_id]
            except KeyError:
                if isinstance(tag_key, int):
                    raise InvalidTagId(tag_key) from None
                raise InvalidTagName(tag_key) from None
            if ifd == "IFD1":
                return ExifTagDefinition(
                    ifd="IFD1",
                    tag_id=definition.tag_id,
                    name=definition.name,
                    allowed_types=definition.allowed_types,
                    count=definition.count,
                )
            return definition

        matches = (
            self._definitions_by_id.get(tag_key, [])
            if isinstance(tag_key, int)
            else self._definitions_by_name.get(tag_key, [])
        )
        if not matches:
            if isinstance(tag_key, int):
                raise InvalidTagId(tag_key)
            raise InvalidTagName(tag_key)
        if len(matches) > 1:
            raise AmbiguousTagKey(
                tag_key,
                [f"{match.ifd}:{match.tag_id} ({match.name})" for match in matches],
            )
        return matches[0]

    def get_ifd(self, tag_key: Union[int, str], thumbnail: bool = False) -> IfdName:
        """
        Get the IFD for an unambiguous tag.

        Args:
            tag_key: Tag name or tag ID.
            thumbnail: If True, return the thumbnail IFD (IFD1).
        """
        if thumbnail:
            self._validate_tag_key(tag_key)
            return "IFD1"
        return self.get_definition(tag_key).ifd

    def resolve_tag_id(
        self, tag_key: Union[int, str], ifd: IfdName | None = None
    ) -> int:
        """
        Get a tag ID for a tag name or return an unambiguous integer ID.
        """
        if isinstance(tag_key, int):
            if ifd is not None:
                registry_ifd = _tagkit_ifd_to_registry_ifd(ifd)
                if (registry_ifd, tag_key) not in self._definitions_by_key:
                    raise InvalidTagId(tag_key)
                return tag_key
            return self.get_definition(tag_key).tag_id

        matches = self._definitions_by_name.get(tag_key, [])
        if not matches:
            raise InvalidTagName(tag_key)
        if ifd is not None:
            registry_ifd = _tagkit_ifd_to_registry_ifd(ifd)
            for definition in matches:
                if _tagkit_ifd_to_registry_ifd(definition.ifd) == registry_ifd:
                    return definition.tag_id
            raise InvalidTagName(tag_key)
        if len(matches) > 1:
            raise AmbiguousTagKey(
                tag_key,
                [f"{match.ifd}:{match.tag_id} ({match.name})" for match in matches],
            )
        return matches[0].tag_id

    def resolve_tag_name(
        self, tag_key: Union[int, str], ifd: IfdName | None = None
    ) -> str:
        """
        Get a tag name for a tag ID or return an unambiguous tag name.
        """
        return self.get_definition(tag_key, ifd=ifd).name

    def get_exif_type(
        self, tag_key: Union[int, str], ifd: IfdName | None = None
    ) -> ExifType:
        """
        Get the primary EXIF type for a tag.
        """
        return self.get_definition(tag_key, ifd=ifd).exif_type

    def _validate_tag_key(self, tag_key: Union[int, str]) -> None:
        if isinstance(tag_key, int):
            self._validate_tag_id(tag_key)
        else:
            self._validate_tag_name(tag_key)

    def _validate_tag_id(self, tag_id: int) -> None:
        if tag_id not in self._definitions_by_id:
            raise InvalidTagId(tag_id)

    def _validate_tag_name(self, tag_name: str) -> None:
        if tag_name not in self._definitions_by_name:
            raise InvalidTagName(tag_name)


tag_registry = ExifRegistry.from_yaml()
