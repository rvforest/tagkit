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
        >>> os.listdir(img_dir)
        ['foo.txt', 'image1.jpg', 'image10.jpg', 'image2.jpg', 'image3.jpg']

        >>> resolver = FileResolver("image1.jpg")
        >>> [path.name for path in resolver.files]
        ['image1.jpg']

        >>> resolver = FileResolver("*.jpg", glob_mode=True)
        >>> [path.name for path in resolver.files]
        ['image1.jpg', 'image10.jpg', 'image2.jpg', 'image3.jpg']

        >>> resolver = FileResolver("image[12].jpg", regex_mode=True)
        >>> [path.name for path in resolver.files]
        ['image1.jpg', 'image2.jpg']

    """

    def __init__(
        self,
        file_or_pattern: str,
        glob_mode: bool = False,
        regex_mode: bool = False,
    ):
        self.files = sorted(self._resolve(file_or_pattern, glob_mode, regex_mode))

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
        # Validate parameters
        if glob_mode and regex_mode:
            raise typer.BadParameter(
                "Cannot specify both --glob and --regex. Please choose only one."
            )

        # Dispatch to the appropriate resolution method
        if glob_mode:
            return self._resolve_glob(file_or_pattern)
        if regex_mode:
            return self._resolve_regex(file_or_pattern)

        # Default resolution strategy: try direct file, then glob, then regex
        direct_matches = self._resolve_direct_file(file_or_pattern)
        if direct_matches:
            return direct_matches

        glob_matches = self._resolve_glob(file_or_pattern)
        if glob_matches:
            return glob_matches

        return self._resolve_regex(file_or_pattern)

    def _resolve_direct_file(self, file_path: str) -> List[Path]:
        """
        Resolve a direct file path.

        Args:
            file_path (str): Path to a file.

        Returns:
            List[Path]: List containing the file path if it exists, empty list otherwise.
        """
        path = Path(file_path)
        return [path] if path.exists() else []

    def _resolve_glob(self, pattern: str) -> List[Path]:
        """
        Resolve files using glob pattern matching.

        Args:
            pattern (str): Glob pattern to match.

        Returns:
            List[Path]: List of paths matching the glob pattern.
        """
        return [Path(p) for p in glob.glob(pattern, recursive=True)]

    def _resolve_regex(self, pattern: str) -> List[Path]:
        """
        Resolve files using regex pattern matching.

        Args:
            pattern (str): Regex pattern to match.

        Returns:
            List[Path]: List of paths matching the regex pattern.
        """
        # Extract directory and filename pattern from the input
        path_obj = Path(pattern)
        directory = path_obj.parent if str(path_obj.parent) != "." else Path(".")
        filename_pattern = path_obj.name

        # Create regex pattern for just the filename part
        regex = re.compile(filename_pattern)

        # Search in the specified directory
        return [path for path in directory.glob("*") if regex.match(path.name)]
