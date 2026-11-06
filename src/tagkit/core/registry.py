"""Shared EXIF tag definitions and directory resolution policy."""

from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict, Union, cast

import yaml
from typing_extensions import Self

from tagkit.conf.models import RegistryConfig
from tagkit.core.exceptions import AmbiguousTagKey, InvalidTagId, InvalidTagName
from tagkit.core.types import ExifCount, ExifType, IfdName, NAMESPACE_IFDS, TagNamespace


class RegistryConfValue(TypedDict, total=False):
    name: str
    type: ExifType | list[ExifType]
    count: ExifCount | None
    ifds: list[IfdName] | None
    default_ifd: IfdName | None


RegistryConf = dict[TagNamespace, dict[int, RegistryConfValue]]


@dataclass(frozen=True)
class ExifTagDefinition:
    """Shared tag meaning, value constraints, and supported directory placements.

    A definition's identity is its namespace and numeric tag ID. It does not
    describe an occurrence in an image or choose a target directory.
    """

    namespace: TagNamespace
    tag_id: int
    name: str
    allowed_types: tuple[ExifType, ...]
    allowed_ifds: tuple[IfdName, ...]
    count: ExifCount | None = None

    @property
    def exif_type(self) -> ExifType:
        """Return the primary EXIF type for compatibility helpers."""
        return self.allowed_types[0]


@dataclass(frozen=True)
class ResolvedTag:
    """A shared definition paired with a selected directory."""

    definition: ExifTagDefinition
    ifd: IfdName


class ExifRegistry:
    """Registry of shared tag definitions and default directory policy.

    Args:
        registry_conf: Definitions grouped by tag namespace.
    """

    def __init__(self, registry_conf: RegistryConf) -> None:
        config = RegistryConfig.model_validate(registry_conf)
        self.tags_by_namespace = cast(
            RegistryConf, config.model_dump(exclude_none=True)
        )
        self._definitions_by_name: dict[str, list[ExifTagDefinition]] = {}
        self._definitions_by_id: dict[int, list[ExifTagDefinition]] = {}
        self._default_ifds: dict[tuple[TagNamespace, int], IfdName] = {}

        for namespace, section in config.root.items():
            for tag_id, tag in section.root.items():
                allowed_types = (
                    tuple(tag.type) if isinstance(tag.type, list) else (tag.type,)
                )
                definition = ExifTagDefinition(
                    namespace=namespace,
                    tag_id=tag_id,
                    name=tag.name,
                    allowed_types=allowed_types,
                    allowed_ifds=tuple(tag.ifds)
                    if tag.ifds is not None
                    else NAMESPACE_IFDS[namespace],
                    count=tag.count,
                )
                self._default_ifds[namespace, tag_id] = (
                    tag.default_ifd or NAMESPACE_IFDS[namespace][0]
                )
                self._definitions_by_name.setdefault(definition.name, []).append(
                    definition
                )
                self._definitions_by_id.setdefault(tag_id, []).append(definition)

    @classmethod
    def from_yaml(cls, path: Union[Path, str, None] = None) -> Self:
        """Load and validate registry YAML from a custom path or the bundled file.

        Args:
            path: Registry YAML path. None uses the bundled registry.

        Returns:
            The loaded registry.
        """
        if path is None:
            path = Path(__file__).parents[1] / "conf/registry.yaml"
        with open(path) as f:
            return cls(yaml.safe_load(f))

    @property
    def tag_names(self) -> list[str]:
        """Return all unique tag names in the registry."""
        return list(self._definitions_by_name)

    def get_definition(
        self, tag_key: Union[int, str], ifd: IfdName | None = None
    ) -> ExifTagDefinition:
        """Find a shared definition, optionally constrained by directory.

        Args:
            tag_key: Tag name or numeric ID.
            ifd: Supported directory used to disambiguate definitions.

        Returns:
            The same immutable definition for every supported placement.

        Raises:
            InvalidTagId: No definition matches a numeric key and directory.
            InvalidTagName: No definition matches a name and directory.
            AmbiguousTagKey: Multiple definitions match the supplied key.
        """
        matches = (
            self._definitions_by_id.get(tag_key, [])
            if isinstance(tag_key, int)
            else self._definitions_by_name.get(tag_key, [])
        )
        if ifd is not None:
            matches = [
                definition for definition in matches if ifd in definition.allowed_ifds
            ]
        if not matches:
            if isinstance(tag_key, int):
                raise InvalidTagId(tag_key)
            raise InvalidTagName(tag_key)
        if len(matches) > 1:
            raise AmbiguousTagKey(
                tag_key,
                [
                    f"{match.namespace}:{match.tag_id} ({match.name})"
                    for match in matches
                ],
            )
        return matches[0]

    def resolve_tag(
        self, tag_key: Union[int, str], ifd: IfdName | None = None
    ) -> ResolvedTag:
        """Select a definition and a directory using explicit or default policy.

        Args:
            tag_key: Tag name or numeric ID.
            ifd: Explicit directory; None uses the definition's configured default.

        Returns:
            The shared definition and selected directory.
        """
        definition = self.get_definition(tag_key, ifd=ifd)
        target = (
            ifd
            if ifd is not None
            else self._default_ifds[definition.namespace, definition.tag_id]
        )
        return ResolvedTag(definition, target)

    def get_ifd(self, tag_key: Union[int, str], thumbnail: bool = False) -> IfdName:
        """Select a tag's default directory or validate thumbnail placement.

        Args:
            tag_key: Tag name or numeric ID.
            thumbnail: If True, require a definition supporting IFD1.

        Returns:
            The selected directory.
        """
        return self.resolve_tag(tag_key, ifd="IFD1" if thumbnail else None).ifd

    def resolve_tag_id(
        self, tag_key: Union[int, str], ifd: IfdName | None = None
    ) -> int:
        """Return the numeric ID of a matching, unambiguous definition."""
        return self.get_definition(tag_key, ifd=ifd).tag_id

    def resolve_tag_name(
        self, tag_key: Union[int, str], ifd: IfdName | None = None
    ) -> str:
        """Return the name of a matching, unambiguous definition."""
        return self.get_definition(tag_key, ifd=ifd).name

    def get_exif_type(
        self, tag_key: Union[int, str], ifd: IfdName | None = None
    ) -> ExifType:
        """Return the primary EXIF type for a matching definition."""
        return self.get_definition(tag_key, ifd=ifd).exif_type


tag_registry = ExifRegistry.from_yaml()
