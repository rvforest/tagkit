import base64
from pathlib import Path
from typing import Callable, Optional, Self, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from tagkit.exif_entry import ExifEntry  # pragma: no cover

import yaml

Rational = tuple[int, int]
Rational3 = tuple[Rational, Rational, Rational]
Rational4 = tuple[Rational, Rational, Rational, Rational]


class TagValueFormatter:
    """
    Formats EXIF tag values according to configuration rules.

    Args:
        conf (dict[str, dict]): Formatting configuration for tag values.

    Example:
        >>> formatter = TagValueFormatter.from_yaml()
        >>> formatter.format(tag_entry)
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
            TagValueFormatter: Formatter instance with loaded config.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            yaml.YAMLError: If the YAML file is invalid.

        Example:
            >>> TagValueFormatter.from_yaml('conf.yaml')
        """
        if file is None:
            prj_root = Path(__file__).parents[1]
            file = prj_root / "tagkit/conf/tag_value_format.yaml"
        with open(file, "r") as f:
            conf = yaml.safe_load(f)
        return cls(conf)

    def _get_format_handler(self, format_type: str) -> Optional[Callable]:
        """Get the appropriate handler method for the given format type."""
        handler_map = {
            "show_plus": lambda v, c: self._show_plus(str(v)),
            "decimal": lambda v, c: self._format_decimal(v, c.get("units")),
            "fraction": lambda v, c: self._format_fraction(v, c.get("units")),
            "f_number": lambda v, c: self._format_f_number(v),
            "percent": lambda v, c: self._format_percent(v),
            "coordinates": lambda v, c: self._format_coordinates(v),
            "lens_info": lambda v, c: self._format_lens_info(v),
            "map": lambda v, c: self._format_map(v, c.get("mapping")),
        }
        return handler_map.get(format_type)

    def format(self, tag: 'ExifEntry') -> str:
        """
        Format the tag value according to its configuration.

        Args:
            tag (ExifEntry): The EXIF entry to format.

        Returns:
            str: The formatted value as a string.

        Notes:
            - If the tag value is bytes, it will be displayed as a base64-encoded string if it cannot be decoded as UTF-8.

        Example:
            >>> formatter.format(tag_entry)
        """
        conf = self.conf.get(tag.name)

        if conf is not None:
            handler = self._get_format_handler(conf["display"])
            if handler:
                return handler(tag.value, conf)

        if isinstance(tag.value, bytes):
            tag.value = self._format_bytes(tag.value)

        return str(tag.value)

    def _format_bytes(self, val: bytes) -> str:
        try:
            return val.decode("utf-8")
        except UnicodeDecodeError:
            return base64.b64encode(val).decode('ascii')


    def _show_plus(self, val: str) -> str:
        return f"+{val}"

    def _format_decimal(self, val: Rational, units: Optional[str] = None) -> str:
        result = str(val[0] / val[1])
        if units is not None:
            result += f" {units}"
        return result

    def _format_fraction(self, val: Rational, units: Optional[str] = None) -> str:
        result = f"{val[0]}/{val[1]}"
        if units is not None:
            result += f" {units}"
        return result

    def _format_f_number(self, val: Rational) -> str:
        decimal = self._format_decimal(val)
        return f"f/{decimal}"

    def _format_percent(self, val: Rational) -> str:
        return f"{val[0] / val[1]:.0%}"

    def _format_coordinates(self, val: Rational3) -> str:
        degrees = val[0][0]
        minutes = val[1][0]
        has_seconds = val[2][1] == 1
        coords = f"{degrees}°{minutes}"
        MIN = "'"
        SEC = '"'
        if has_seconds:
            seconds = val[2][0]
            coords += f'{MIN}{seconds}{SEC}'
        else:
            fractional_min = str(val[2][0] / val[2][1]).lstrip("0")
            coords += f"{fractional_min}{MIN}"
        return coords

    def _format_lens_info(self, val: Rational4) -> str:
        min_focal_len = self._format_decimal(val[0])
        max_focal_len = self._format_decimal(val[1])
        min_f_num = self._format_f_number(val[2])
        max_f_num = self._format_f_number(val[3])
        return f"{min_focal_len} mm - {max_focal_len}; {min_f_num} - {max_f_num}"

    def _format_map(self, val: int, mapping: dict[int, str]) -> str:
        return mapping[val]
