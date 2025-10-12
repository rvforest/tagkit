"""
Tag value formatting utilities.

This module provides the ValueFormatter class for formatting EXIF tag values
according to configuration rules.
"""

import base64
import math
from pathlib import Path
from typing import Any, Callable, Optional, Self, TYPE_CHECKING, Union, cast

import yaml

from tagkit.conf.models import FormattingConfig
from tagkit.core.types import (
    Rational,
    Rational3,
    Rational4,
)

if TYPE_CHECKING:
    from tagkit.core.tag import ExifTag  # pragma: no cover  # noqa: F401

# Constants for coordinate formatting
_MINUTE_SYMBOL = "'"
_SECOND_SYMBOL = '"'


class ValueFormatter:
    """
    Formats EXIF tag values according to configuration rules.

    This class provides flexible formatting of EXIF tag values including
    rationals, sequences, binary data, and specialized formats like coordinates
    and lens information.

    Args:
        conf (dict[str, dict]): Formatting configuration for tag values.

    Example:
        # F-number
        >>> from tagkit.core.tag import ExifTag
        >>> tag_entry = ExifTag(33437, (1, 2), 'Exif')
        >>> formatter = ValueFormatter.from_yaml()
        >>> formatter.format_value(tag_entry)
        'f/1.2'

        # Bytes
        >>> tag_entry = ExifTag(1, b'\\xff\\xfe\\xfd\\xfc', 'Exif')
        >>> formatter.format_value(tag_entry)
        '<bytes: 4>'

        # Base64
        >>> formatter.format_value(tag_entry, binary_format='base64')
        'base64://79/A=='

    """

    def __init__(self, conf: dict[str, dict]) -> None:
        self.conf = conf

    @classmethod
    def from_yaml(cls, file: Union[Path, str, None] = None) -> Self:
        """
        Load formatting configuration from a YAML file and create a formatter.

        Args:
            file (Union[Path, str, None]): Path to the YAML config file. If None, uses default.

        Returns:
            ValueFormatter: Formatter instance with loaded config.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            yaml.YAMLError: If the YAML file is invalid.
            pydantic.ValidationError: If the YAML structure is invalid.
        """
        if file is None:
            prj_root = Path(__file__).parents[2]
            file = prj_root / "tagkit/conf/formatting.yaml"
        with open(file, "r") as f:
            raw_conf = yaml.safe_load(f)
        
        # Validate with Pydantic
        validated_conf = FormattingConfig.model_validate(raw_conf)
        
        # Convert to dict format expected by __init__
        # For RootModel, we need to access .root and convert nested models to dicts
        conf = {
            tag_name: tag_config.model_dump()
            for tag_name, tag_config in validated_conf.root.items()
        }
        return cls(conf)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def format_value(
        self,
        tag: "ExifTag",
        binary_format: Optional[str] = None,
    ) -> str:
        """
        Format a tag value according to its type and configuration.

        Args:
            tag: The tag to format.
            binary_format: How to format binary data - 'bytes', 'hex', or 'base64'.
            If None, <bytes: N> will be shown as a placeholder.

        Returns:
            The formatted value as a string.
        """
        conf = self.conf.get(tag.name)

        if conf is not None:
            handler = self._get_format_handler(conf["display"])
            if handler:
                return handler(tag.value, conf)

        if isinstance(tag.value, bytes):
            return self._format_bytes(tag.value, binary_format)

        return str(tag.value)

    # -------------------------------------------------------------------------
    # Sequence handling utilities
    # -------------------------------------------------------------------------

    def _is_rational_sequence(self, val: Any) -> bool:
        """
        Check if a value is a sequence of rationals.

        A rational is a tuple of two ints: (numerator, denominator).
        A sequence of rationals is a tuple where elements are themselves tuples.

        Args:
            val: The value to check.

        Returns:
            True if val is a sequence of rationals, False otherwise.
        """
        if not isinstance(val, tuple) or len(val) == 0:
            return False
        # Check if first element is a tuple (indicating a sequence of rationals)
        return isinstance(val[0], tuple)

    def _apply_to_sequence_or_single(
        self,
        val: Union[Rational, tuple],
        formatter: Callable[[Rational], str],
    ) -> str:
        """
        Apply a formatter to a value that may be a single rational or a sequence.

        Args:
            val: Either a single rational or a sequence of rationals.
            formatter: Function to apply to each rational.

        Returns:
            Formatted string or list of formatted strings in brackets.
        """
        if self._is_rational_sequence(val):
            formatted = [formatter(cast(Rational, r)) for r in val]
            return "[" + ", ".join(formatted) + "]"
        return formatter(cast(Rational, val))

    # -------------------------------------------------------------------------
    # Format handler mapping
    # -------------------------------------------------------------------------

    def _get_format_handler(self, format_type: str) -> Optional[Callable]:
        """
        Get the appropriate handler method for the given format type.

        Args:
            format_type: The type of formatting to apply.

        Returns:
            A callable that takes (value, config) and returns formatted string,
            or None if no handler exists for the format type.
        """
        handler_map = {
            "show_plus": lambda v, c: self._show_plus(str(v)),
            "decimal": lambda v, c: self._format_decimal_with_sequence_support(
                v, c.get("unit")
            ),
            "fraction": lambda v, c: self._format_fraction_with_sequence_support(
                v, c.get("unit")
            ),
            "f_number": lambda v, c: self._format_f_number_with_sequence_support(v),
            "percent": lambda v, c: self._format_percent_with_sequence_support(v),
            "coordinates": lambda v, c: self._format_coordinates(v),
            "lens_info": lambda v, c: self._format_lens_info(v),
            "map": lambda v, c: self._format_map(v, c.get("mapping")),
            "shutter_speed": lambda v, c: self._format_shutter_speed(v),
        }
        return handler_map.get(format_type)

    # -------------------------------------------------------------------------
    # Sequence-aware formatter wrappers
    # -------------------------------------------------------------------------

    def _format_decimal_with_sequence_support(
        self, val: Union[Rational, tuple], unit: Optional[str] = None
    ) -> str:
        """
        Format as a decimal value, with support for sequences of rationals.

        Args:
            val: Either a single rational or a sequence of rationals.
            unit: Optional unit to append to each formatted value.

        Returns:
            Formatted decimal string or list of formatted decimals.
        """
        return self._apply_to_sequence_or_single(
            val, lambda r: self._format_decimal(r, unit)
        )

    def _format_fraction_with_sequence_support(
        self, val: Union[Rational, tuple], unit: Optional[str] = None
    ) -> str:
        """
        Format as a fraction value, with support for sequences of rationals.

        Args:
            val: Either a single rational or a sequence of rationals.
            unit: Optional unit to append to each formatted value.

        Returns:
            Formatted fraction string or list of formatted fractions.
        """
        return self._apply_to_sequence_or_single(
            val, lambda r: self._format_fraction(r, unit)
        )

    def _format_f_number_with_sequence_support(
        self, val: Union[Rational, tuple]
    ) -> str:
        """
        Format as an f-number value, with support for sequences of rationals.

        Args:
            val: Either a single rational or a sequence of rationals.

        Returns:
            Formatted f-number string or list of formatted f-numbers.
        """
        return self._apply_to_sequence_or_single(val, self._format_f_number)

    def _format_percent_with_sequence_support(self, val: Union[Rational, tuple]) -> str:
        """
        Format as a percent value, with support for sequences of rationals.

        Args:
            val: Either a single rational or a sequence of rationals.

        Returns:
            Formatted percent string or list of formatted percents.
        """
        return self._apply_to_sequence_or_single(val, self._format_percent)

    # -------------------------------------------------------------------------
    # Core formatters (single value)
    # -------------------------------------------------------------------------

    def _format_bytes(self, val: bytes, binary_format: Optional[str] = None) -> str:
        """
        Format bytes as a string.

        Args:
            val: The bytes to format
            binary_format: How to format binary data - 'bytes', 'hex', or 'base64'

        Returns:
            Formatted string representation of the bytes

        Raises:
            ValueError: If an unsupported binary format is specified.
        """
        if binary_format is None:
            return f"<bytes: {len(val)}>"

        if binary_format == "hex":
            return f"hex:{val.hex()}"
        elif binary_format == "base64":
            return f"base64:{base64.b64encode(val).decode('ascii')}"
        elif binary_format == "bytes":
            return repr(val)  # This will give b'...' or b"..." syntax
        else:
            raise ValueError(f"Unsupported binary format: {binary_format}")

    def _show_plus(self, val: str) -> str:
        """
        Add a plus sign prefix to a numeric string.

        Args:
            val: The numeric string.

        Returns:
            The value prefixed with a plus sign (e.g., '+1.5').
        """
        return f"+{val}"

    def _format_decimal(self, val: Rational, unit: Optional[str] = None) -> str:
        """
        Format a rational as a decimal value.

        Args:
            val: The rational (numerator, denominator) to format.
            unit: Optional unit to append to the result.

        Returns:
            The formatted decimal (e.g., '1.5' or '1.5mm').
        """
        result = str(val[0] / val[1])
        if unit is not None:
            result += unit
        return result

    def _format_fraction(self, val: Rational, unit: Optional[str] = None) -> str:
        """
        Format a rational as a reduced fraction.

        Args:
            val: The rational (numerator, denominator) to format.
            unit: Optional unit to append to the result.

        Returns:
            The formatted reduced fraction (e.g., '3/2' or '3/2mm').
        """
        num, denom = val
        gcd = math.gcd(num, denom)
        num //= gcd
        denom //= gcd
        result = f"{num}/{denom}"
        if unit is not None:
            result += unit
        return result

    def _format_f_number(self, val: Rational) -> str:
        """
        Format an APEX f-number value in a photographer-friendly way.

        Args:
            val: The f-number as a rational APEX value.

        Returns:
            The formatted f-number (e.g., 'f/2.8').
        """
        f_number = math.sqrt(2 ** (val[0] / val[1]))
        return f"f/{f_number:.1f}"

    def _format_percent(self, val: Rational) -> str:
        """
        Format a rational as a percentage.

        Args:
            val: The rational (numerator, denominator) to format.

        Returns:
            The formatted percentage (e.g., '50%').
        """
        return f"{val[0] / val[1]:.0%}"

    # -------------------------------------------------------------------------
    # Specialized formatters
    # -------------------------------------------------------------------------

    def _format_coordinates(self, val: Rational3) -> str:
        """
        Format GPS coordinates in degrees, minutes, and seconds.

        Args:
            val: The coordinate as a tuple of tuples (degrees, minutes, seconds).

        Returns:
            The formatted coordinate (e.g., '1°2.03\'').
        """
        degrees = val[0][0]
        minutes = val[1][0]
        has_seconds = val[2][1] == 1
        coords = f"{degrees}°{minutes}"

        if has_seconds:
            seconds = val[2][0]
            coords += f"{_MINUTE_SYMBOL}{seconds}{_SECOND_SYMBOL}"
        else:
            fractional_min = str(val[2][0] / val[2][1]).lstrip("0")
            coords += f"{fractional_min}{_MINUTE_SYMBOL}"
        return coords

    def _format_lens_info(self, val: Rational4) -> str:
        """
        Format lens information (focal length range and aperture range).

        Args:
            val: The lens info as a tuple of tuples
                 (min_focal_len, max_focal_len, min_f_num, max_f_num).

        Returns:
            The formatted lens info (e.g., '24.0 mm - 70.0; f/2.8 - f/5.6').
        """
        min_focal_len = self._format_decimal(val[0])
        max_focal_len = self._format_decimal(val[1])
        min_f_num = self._format_f_number(val[2])
        max_f_num = self._format_f_number(val[3])
        return f"{min_focal_len} mm - {max_focal_len}; {min_f_num} - {max_f_num}"

    def _format_map(self, val: int, mapping: dict[int, str]) -> str:
        """
        Map integer tag values to human-readable strings.

        Args:
            val: The integer value to map.
            mapping: The mapping dictionary from integers to strings.

        Returns:
            The mapped string value (e.g., 'Auto').
        """
        return mapping[val]

    def _format_shutter_speed(self, val: Rational) -> str:
        """
        Format an APEX shutter speed value in a photographer-friendly way.

        Converts APEX shutter speed values to standard notations like '1/250s'
        or '2s', using common shutter speed denominators when appropriate.

        Args:
            val: The shutter speed as a rational APEX value (numerator, denominator).

        Returns:
            The formatted shutter speed (e.g., '1/250s', '2s').
        """
        seconds = 2 ** (-val[0] / val[1])

        if seconds >= 1:
            # Show as whole seconds, rounded to 1 decimal if needed
            if seconds == int(seconds):
                return f"{int(seconds)}s"
            else:
                return f"{seconds:.1f}s"
        else:
            # For fast shutter speeds, try to find a standard denominator
            standard_denominators = [
                8000,
                4000,
                2000,
                1000,
                500,
                250,
                125,
                60,
                30,
                15,
                8,
                4,
                2,
            ]
            for denom in standard_denominators:
                num = seconds * denom
                if abs(round(num) - num) < 1e-3:
                    return self._format_fraction((int(round(num)), denom), unit="s")

            # Fallback to calculated denominator
            denominator = round(1 / seconds)
            return f"1/{denominator}s"
