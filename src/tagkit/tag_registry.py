from pathlib import Path
from typing import Literal, Optional, Self, TypedDict, Union

import yaml

from tagkit.exceptions import InvalidTagId, InvalidTagName
from tagkit.types import ExifType, IfdName


class RegistryConfValue(TypedDict):
    name: str
    type: ExifType


RegistryConfKey = Literal["Image", "Exif", "GPS", "Interop"]
RegistryConf = dict[RegistryConfKey, dict[int, RegistryConfValue]]


class _ExifRegistry:
    """
    Registry of all EXIF tags compatible with tagkit.

    Do not directly instantiate this class. Instead, use:
        from tagkit import tag_registry

    Args:
        registry_conf (RegistryConf): The EXIF tag registry configuration.
    """

    def __init__(self, registry_conf: RegistryConf):
        self.tags = registry_conf

        name_to_id = {}
        name_to_type = {}
        for ifd_tags in self.tags.values():
            name_to_id.update({tag["name"]: tag_id for tag_id, tag in ifd_tags.items()})
            name_to_type.update({tag["name"]: tag["type"] for tag in ifd_tags.values()})
        self._name_to_id = name_to_id
        self._name_to_type = name_to_type
        self._tag_ids = {tag_id for exif_tags in registry_conf.values() for tag_id in exif_tags}

    @classmethod
    def from_yaml(cls, path: Union[Path, str, None] = None) -> Self:
        """
        Load the EXIF tag registry from a YAML file.

        Args:
            path (Union[Path, str, None]): Path to the YAML file. If None, uses default.

        Returns:
            _ExifRegistry: The loaded registry instance.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            yaml.YAMLError: If the YAML file is invalid.

        Example:
            >>> _ExifRegistry.from_yaml('conf.yaml')
        """
        if path is None:
            here = Path(__file__).parents[0]
            path = here / "conf/tag_registry.yaml"
        with open(path, "r") as f:
            conf = yaml.safe_load(f)
        return cls(conf)

    @property
    def tag_names(self) -> list[str]:
        """
        List all tag names in the registry.

        Returns:
            list[str]: All tag names.

        Example:
            >>> tag_registry.tag_names
        """
        return list(self._name_to_id)

    # TODO: Add a warning if a tag is in multiple ifd's.
    def get_ifd(self, tag_key: Union[int, str], thumbnail: bool = False) -> IfdName:
        """
        Get the IFD (Image File Directory) for a tag.

        Args:
            tag_key (Union[int, str]): Tag name or tag ID.
            thumbnail (bool): If True, return the thumbnail IFD.

        Returns:
            IfdName: The IFD name.

        Raises:
            ValueError: If the tag or IFD is invalid.

        Example:
            >>> tag_registry.get_ifd('Make')
        """
        tag_id = self.get_tag_id(tag_key)

        if thumbnail:
            return "IFD1"

        for ifd_category, tags in self.tags.items():
            if tag_id in tags:
                ifd = "IFD0" if ifd_category == "Image" else ifd_category
                return ifd

        # Execution shouldn't make it this far because if tag_id is in self
        # then there should always be a result. However, as a guardrail we
        # raise here anyway.
        raise ValueError(f"Could not find ifd for tag '{tag_key}'")  # pragma: no cover

    def get_tag_id(self, tag_key: Union[int, str]) -> int:
        """
        Get tag ID for a given tag name or return the ID unchanged if already an int.

        Args:
            tag_key (Union[int, str]): Tag name or tag ID.

        Returns:
            int: Tag ID for the given tag name.

        Raises:
            InvalidTagName: If the tag name is invalid.
            InvalidTagId: If the tag ID is invalid.

        Example:
            >>> tag_registry.get_tag_id('Make')
        """
        if isinstance(tag_key, int):
            self._validate_tag_id(tag_key)
            return tag_key

        self._validate_tag_name(tag_key)
        return self._name_to_id[tag_key]

    def get_tag_name(
        self, tag_key: Union[int, str], ifd: Optional[IfdName] = None
    ) -> str:
        """
        Get tag name for a given tag name or tag ID. If given a tag ID, returns the name.

        Args:
            tag_key (Union[int, str]): Tag name or tag ID.
            ifd (Optional[IfdName]): Specific IFD to use.

        Returns:
            str: Tag name for the given tag ID.

        Raises:
            InvalidTagName: If the tag name is invalid.
            InvalidTagId: If the tag ID is invalid.
            ValueError: If the tag or IFD is invalid.

        Example:
            >>> tag_registry.get_tag_name(271)
        """
        if isinstance(tag_key, str):
            self._validate_tag_name(tag_key)
            return tag_key

        self._validate_tag_id(tag_key)

        ifd_key = "Image" if ifd in ("IFD0", "IFD1") else ifd
        if ifd_key is not None:
            return self.tags[ifd_key][tag_key]["name"]

        # If IFD not given then try all IFD's
        for ifd_tags in self.tags.values():
            if tag_key in ifd_tags:
                return ifd_tags[tag_key]["name"]

        # Execution shouldn't make it this far because if tag_id is in self
        # then there should always be a result. However, as a guardrail we
        # raise here anyway.
        raise ValueError(f"Could not find ifd for tag '{tag_key}'")  # pragma: no cover

    def _validate_tag_id(self, tag_id: int) -> None:
        if tag_id not in self._tag_ids:
            raise InvalidTagId(tag_id)

    def _validate_tag_name(self, tag_name: str) -> None:
        if tag_name not in self._name_to_id:
            raise InvalidTagName(tag_name)

    def get_exif_type(self, tag_key: Union[int, str]) -> ExifType:
        """
        Get the EXIF type for a tag.

        Args:
            tag_key (Union[int, str]): Tag name or tag ID.

        Returns:
            ExifType: The EXIF type for the tag.

        Raises:
            InvalidTagName: If the tag name is invalid.
            InvalidTagId: If the tag ID is invalid.

        Example:
            >>> tag_registry.get_exif_type('Make')
        """
        tag_name = self.get_tag_name(tag_key)
        return self._name_to_type[tag_name]


tag_registry = _ExifRegistry.from_yaml()
