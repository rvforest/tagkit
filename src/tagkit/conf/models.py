"""
Pydantic models for validating tagkit configuration files.

This module defines Pydantic models for validating all configuration files:
- registry.yaml: EXIF tag registry configuration
- formatting.yaml: Tag value formatting configuration
- test-img-metadata.json: Test image metadata configuration
- doctest-img-metadata.json: Doctest image metadata configuration
"""

from typing import Any, Literal, Union

from pydantic import BaseModel, Field, RootModel, field_validator


# ========================== Registry Configuration ==========================


class RegistryTagEntry(BaseModel):
    """Entry for a single EXIF tag in the registry."""

    name: str = Field(description="Tag name (e.g., 'Make', 'Model')")
    type: Literal["ASCII", "BYTE", "RATIONAL", "SRATIONAL", "SHORT", "LONG", "UNDEFINED", "FLOAT"] = Field(
        description="EXIF data type"
    )

    model_config = {"extra": "forbid"}


class RegistryIfdSection(RootModel[dict[int, RegistryTagEntry]]):
    """
    IFD section in the registry, mapping tag IDs to tag entries.
    
    Each key is a tag ID (integer), and each value is a RegistryTagEntry.
    """

    root: dict[int, RegistryTagEntry]


class RegistryConfig(BaseModel):
    """
    Complete registry configuration for EXIF tags.
    
    Contains sections for Image (IFD0/IFD1), Exif, GPS, and Interop tags.
    All sections are optional to allow partial configurations for testing.
    """

    Image: RegistryIfdSection = Field(
        default_factory=lambda: RegistryIfdSection.model_validate({}),
        description="Image IFD tags (IFD0/IFD1)",
    )
    Exif: RegistryIfdSection = Field(
        default_factory=lambda: RegistryIfdSection.model_validate({}),
        description="Exif IFD tags",
    )
    GPS: RegistryIfdSection = Field(
        default_factory=lambda: RegistryIfdSection.model_validate({}),
        description="GPS IFD tags",
    )
    Interop: RegistryIfdSection = Field(
        default_factory=lambda: RegistryIfdSection.model_validate({}),
        description="Interop IFD tags",
    )

    model_config = {"extra": "forbid"}


# ======================== Formatting Configuration ========================


class FormattingTagConfig(BaseModel):
    """Configuration for formatting a specific tag's value."""

    display: str | None = Field(
        None,
        description="Display format (e.g., 'fraction', 'decimal', 'f_number', 'shutter_speed')",
    )
    unit: str | None = Field(None, description="Unit to display (e.g., 's', 'mm', 'dpi')")
    show_plus: bool | None = Field(None, description="Whether to show '+' for positive values")
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
    ifd: Literal["0th", "1st", "Exif", "GPS"] = Field(description="IFD location")

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
    def validate_filenames(cls, v: dict[str, ImageMetadata]) -> dict[str, ImageMetadata]:
        """Validate that all filenames end with .jpg or .jpeg."""
        for filename in v.keys():
            if not (filename.endswith(".jpg") or filename.endswith(".jpeg")):
                raise ValueError(
                    f"Invalid filename '{filename}': must end with .jpg or .jpeg"
                )
        return v
