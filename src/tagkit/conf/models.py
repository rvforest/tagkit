"""
Pydantic models for validating tagkit configuration files.

This module defines Pydantic models for validating all configuration files:
- registry.yaml: EXIF tag registry configuration
- formatting.yaml: Tag value formatting configuration
- test-img-metadata.json: Test image metadata configuration
- doctest-img-metadata.json: Doctest image metadata configuration
"""

from typing import Any, Literal, Union

from pydantic import BaseModel, Field, RootModel, field_validator, model_validator

from typing_extensions import Self

from tagkit.core.types import ExifCount, ExifType, IfdName, NAMESPACE_IFDS, TagNamespace


# ========================== Registry Configuration ==========================


class RegistryTagEntry(BaseModel):
    """Entry for a single EXIF tag in the registry."""

    name: str = Field(description="Tag name (e.g., 'Make', 'Model')")
    type: ExifType | list[ExifType] = Field(description="Allowed EXIF data types")
    count: ExifCount | None = Field(
        default=None,
        description="Fixed count, allowed counts, or 'any' for variable count",
    )

    ifds: list[IfdName] | None = Field(
        default=None,
        min_length=1,
        description="Supported directories; defaults by namespace",
    )
    default_ifd: IfdName | None = Field(
        default=None, description="Default target directory; defaults by namespace"
    )

    @field_validator("type")
    @classmethod
    def validate_type_list(
        cls, v: ExifType | list[ExifType]
    ) -> ExifType | list[ExifType]:
        """Validate that multi-type definitions are not empty."""
        if isinstance(v, list) and not v:
            raise ValueError("type list must contain at least one EXIF type")
        return v

    @field_validator("count")
    @classmethod
    def validate_count(cls, v: ExifCount | None) -> ExifCount | None:
        """Validate fixed counts and lists of permitted counts."""
        if isinstance(v, int) and v <= 0:
            raise ValueError("count must be a positive integer or 'any'")
        if isinstance(v, tuple) and (
            not v or any(count <= 0 for count in v) or len(set(v)) != len(v)
        ):
            raise ValueError("count list must contain distinct positive integers")
        return v

    model_config = {"extra": "forbid"}


class RegistryNamespaceSection(RootModel[dict[int, RegistryTagEntry]]):
    """Tag definitions keyed by numeric ID within one namespace."""

    root: dict[int, RegistryTagEntry]


class RegistryConfig(RootModel[dict[TagNamespace, RegistryNamespaceSection]]):
    """Definitions grouped by namespace, with optional per-tag placement policy.

    Image defaults to IFD0 and supports IFD0/IFD1. Other namespaces default to
    their namesake directory. Explicit placements must stay within the namespace,
    and the effective default must be a supported placement. Partial registries
    are supported.
    """

    root: dict[TagNamespace, RegistryNamespaceSection]

    @model_validator(mode="after")
    def validate_placements(self) -> Self:
        """Reject conflicting namespace, placement, and default declarations."""
        for namespace, section in self.root.items():
            supported = NAMESPACE_IFDS[namespace]
            for tag_id, entry in section.root.items():
                ifds = entry.ifds if entry.ifds is not None else supported
                default_ifd = entry.default_ifd or supported[0]
                if len(set(ifds)) != len(ifds) or not set(ifds).issubset(supported):
                    raise ValueError(f"Invalid placements for {namespace}:{tag_id}")
                if default_ifd not in ifds:
                    raise ValueError(
                        f"Default IFD must be a supported placement for {namespace}:{tag_id}"
                    )
        return self


# ======================== Formatting Configuration ========================


class FormattingTagConfig(BaseModel):
    """Configuration for formatting a specific tag's value."""

    display: str | None = Field(
        None,
        description="Display format (e.g., 'fraction', 'decimal', 'f_number', 'shutter_speed')",
    )
    unit: str | None = Field(
        None, description="Unit to display (e.g., 's', 'mm', 'dpi')"
    )
    show_plus: bool | None = Field(
        None, description="Whether to show '+' for positive values"
    )
    mapping: dict[Union[int, str], str] | None = Field(
        None,
        description="Value mapping for enumerated types (e.g., {1: 'Top-left', 2: 'Top-right'})",
    )

    model_config = {"extra": "forbid"}


class FormattingConfig(RootModel[dict[str, FormattingTagConfig]]):
    """
    Complete formatting configuration.

    Maps tag names to their formatting configuration.
    """

    root: dict[str, FormattingTagConfig]


# ==================== Test Image Metadata Configuration ====================


class ImageMetadataTag(BaseModel):
    """A single EXIF tag to be added to a test image."""

    id: int = Field(description="EXIF tag ID")
    name: str = Field(description="Tag name")
    value: Union[str, int, float, list[Any]] = Field(
        description="Tag value (string, number, or array)"
    )
    ifd: Literal["0th", "1st", "Exif", "GPS", "Interop"] = Field(
        description="IFD location"
    )

    model_config = {"extra": "forbid"}


class ImageMetadata(BaseModel):
    """Metadata for a single test image."""

    tags: list[ImageMetadataTag] = Field(description="List of EXIF tags for this image")
    corrupt: bool | None = Field(
        None, description="Whether to create a corrupt image (for error testing)"
    )

    model_config = {"extra": "forbid"}


class ImageMetadataConfig(RootModel[dict[str, ImageMetadata]]):
    """
    Complete test image metadata configuration.

    Maps image filenames (ending in .jpg or .jpeg) to their metadata.
    """

    root: dict[str, ImageMetadata]

    @field_validator("root")
    @classmethod
    def validate_filenames(
        cls, v: dict[str, ImageMetadata]
    ) -> dict[str, ImageMetadata]:
        """Validate that all filenames end with .jpg or .jpeg."""
        for filename in v.keys():
            if not (filename.endswith(".jpg") or filename.endswith(".jpeg")):
                raise ValueError(
                    f"Invalid filename '{filename}': must end with .jpg or .jpeg"
                )
        return v
