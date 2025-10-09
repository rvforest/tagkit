from importlib.metadata import PackageNotFoundError
import importlib
from unittest.mock import patch


def test_failed_version_lookup():
    with patch("importlib.metadata.version", side_effect=PackageNotFoundError):
        import tagkit

        importlib.reload(tagkit)
        assert tagkit.__version__ == "0+unknown"
