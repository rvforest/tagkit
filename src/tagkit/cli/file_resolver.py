import glob
import re
from pathlib import Path
from typing import List

import typer


class FileResolver:
    """
    Resolves file paths from a string, glob, or regex pattern.
    Raises an error if both glob_mode and regex_mode are set.

    Args:
        file_or_pattern (str): File path, glob, or regex pattern.
        glob_mode (bool): If True, use glob matching.
        regex_mode (bool): If True, use regex matching.

    Example:
        >>> resolver = FileResolver('*.jpg', glob_mode=True)
        >>> resolver.files
    """

    def __init__(
        self,
        file_or_pattern: str,
        glob_mode: bool = False,
        regex_mode: bool = False,
    ):
        self.files = self._resolve(file_or_pattern, glob_mode, regex_mode)

    def _resolve(
        self, file_or_pattern: str, glob_mode: bool, regex_mode: bool
    ) -> List[Path]:
        """
        Resolve files based on the provided pattern and mode.
        Raises a Typer.BadParameter if both glob_mode and regex_mode are set.

        Args:
            file_or_pattern (str): File path, glob, or regex pattern.
            glob_mode (bool): If True, use glob matching.
            regex_mode (bool): If True, use regex matching.

        Returns:
            List[Path]: List of resolved file paths.
        """
        if glob_mode and regex_mode:
            raise typer.BadParameter(
                "Cannot specify both --glob and --regex. Please choose only one."
            )
        if glob_mode:
            return [Path(p) for p in glob.glob(file_or_pattern, recursive=True)]
        if regex_mode:
            regex = re.compile(file_or_pattern)
            return [path for path in Path(".").rglob("*") if regex.match(str(path))]

        # Default: try file first
        f = Path(file_or_pattern)
        if f.exists():
            return [f]
        matches = glob.glob(file_or_pattern, recursive=True)
        if matches:
            return [Path(m) for m in matches]
        regex = re.compile(file_or_pattern)
        return [path for path in Path(".").rglob("*") if regex.match(str(path))]
