"""
Tag value formatting utilities.

This module provides the ValueFormatter class for formatting EXIF tag values
according to configuration rules.
"""

import base64
from pathlib import Path
from typing import Callable, Optional, Self, TYPE_CHECKING, Union
import math

if TYPE_CHECKING:
    from tagkit.core.tag import ExifTag  # pragma: no cover  # noqa: F401

import yaml

Rational = tuple[int, int]
Rational3 = tuple[Rational, Rational, Rational]
Rational4 = tuple[Rational, Rational, Rational, Rational]


class ValueFormatter:
    """
    Formats EXIF tag values according to configuration rules.

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
        """
        if file is None:
            prj_root = Path(__file__).parents[2]
            file = prj_root / "tagkit/conf/formatting.yaml"
        with open(file, "r") as f:
            conf = yaml.safe_load(f)
        return cls(conf)

    def _get_format_handler(self, format_type: str) -> Optional[Callable]:
        """Get the appropriate handler method for the given format type."""
        handler_map = {
            "show_plus": lambda v, c: self._show_plus(str(v)),
            "decimal": lambda v, c: self._format_decimal(v, c.get("unit")),
            "fraction": lambda v, c: self._format_fraction(v, c.get("unit")),
            "f_number": lambda v, c: self._format_f_number(v),
            "percent": lambda v, c: self._format_percent(v),
            "coordinates": lambda v, c: self._format_coordinates(v),
            "lens_info": lambda v, c: self._format_lens_info(v),
            "map": lambda v, c: self._format_map(v, c.get("mapping")),
            "shutter_speed": lambda v, c: self._format_shutter_speed(v),
        }
        return handler_map.get(format_type)

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

    def _format_bytes(self, val: bytes, binary_format: Optional[str] = None) -> str:
        """
        Format bytes as a string.

        Args:
            val: The bytes to format
            binary_format: How to format binary data - 'bytes', 'hex', or 'base64'

        Returns:
            Formatted string representation of the bytes
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
        Format as a decimal value with a plus sign.

        Args:
            val (str): The decimal as a string.

        Returns:
            str: The formatted decimal with a plus sign (e.g., '+1.5').
        """
        return f"+{val}"

    def _format_decimal(self, val: Rational, unit: Optional[str] = None) -> str:
        """
        Format as a decimal value.

        Args:
            val (Rational): The decimal as a rational (numerator, denominator).

        Returns:
            str: The formatted decimal (e.g., '1.5').
        """
        result = str(val[0] / val[1])
        if unit is not None:
            result += f"{unit}"
        return result

    def _format_fraction(self, val: Rational, unit: Optional[str] = None) -> str:
        """
        Format as a reduced fraction value.

        Args:
            val (Rational): The fraction as a rational (numerator, denominator).

        Returns:
            str: The formatted reduced fraction (e.g., '3/2').
        """
        num, denom = val
        gcd = math.gcd(num, denom)
        num //= gcd
        denom //= gcd
        result = f"{num}/{denom}"
        if unit is not None:
            result += f"{unit}"
        return result

    def _format_f_number(self, val: Rational) -> str:
        """
        Format an f-number value in a photographer-friendly way.

        Args:
            val (Rational): The f-number as a rational APEX value.

        Returns:
            str: The formatted f-number (e.g., 'f/2.8').
        """
        f_number = math.sqrt(2 ** (val[0] / val[1]))
        return f"f/{f_number:.1f}"

    def _format_percent(self, val: Rational) -> str:
        """
        Format as a percent value.

        Args:
            val (Rational): The percent as a rational (numerator, denominator).

        Returns:
            str: The formatted percent (e.g., '50%').
        """
        return f"{val[0] / val[1]:.0%}"

    def _format_coordinates(self, val: Rational3) -> str:
        """
        Format as a coordinate value.

        Args:
            val (Rational3): The coordinate as a tuple of tuples (degrees, minutes, seconds).

        Returns:
            str: The formatted coordinate (e.g., '1°2.03\'').
        """
        degrees = val[0][0]
        minutes = val[1][0]
        has_seconds = val[2][1] == 1
        coords = f"{degrees}°{minutes}"
        MIN = "'"
        SEC = '"'
        if has_seconds:
            seconds = val[2][0]
            coords += f"{MIN}{seconds}{SEC}"
        else:
            fractional_min = str(val[2][0] / val[2][1]).lstrip("0")
            coords += f"{fractional_min}{MIN}"
        return coords

    def _format_lens_info(self, val: Rational4) -> str:
        """
        Format as a lens info value.

        Args:
            val (Rational4): The lens info as a tuple of tuples (min_focal_len, max_focal_len, min_f_num, max_f_num).

        Returns:
            str: The formatted lens info (e.g., '1.5 mm - 2.0 mm; f/2.8 - f/5.6').
        """
        min_focal_len = self._format_decimal(val[0])
        max_focal_len = self._format_decimal(val[1])
        min_f_num = self._format_f_number(val[2])
        max_f_num = self._format_f_number(val[3])
        return f"{min_focal_len} mm - {max_focal_len}; {min_f_num} - {max_f_num}"

    def _format_map(self, val: int, mapping: dict[int, str]) -> str:
        """
        Map tag values to strings.

        Args:
            val (int): The value to format.
            mapping (dict[int, str]): The mapping of values to strings.

        Returns:
            str: The formatted value (e.g., 'Auto').
        """
        return mapping[val]

    def _format_shutter_speed(self, val: tuple[int, int]) -> str:
        """
        Format a shutter speed value (APEX) in a photographer-friendly way.

        Args:
            val (tuple[int, int]): The shutter speed as a rational (numerator, denominator).

        Returns:
            str: The formatted shutter speed (e.g., '1/250s', '2s').
        """
        seconds = 2 ** (-val[0] / val[1])
        if seconds >= 1:
            # Show as whole seconds, rounded to 1 decimal if needed
            if seconds == int(seconds):
                return f"{int(seconds)}s"
            else:
                return f"{seconds:.1f}s"
        else:
            # For small values, try to find a denominator
            for denom in [8000, 4000, 2000, 1000, 500, 250, 125, 60, 30, 15, 8, 4, 2]:
                num = seconds * denom
                if abs(round(num) - num) < 1e-3:
                    return self._format_fraction((int(round(num)), denom), unit="s")

            # Fallback
            denominator = round(1 / seconds)
            return f"1/{denominator}s"
