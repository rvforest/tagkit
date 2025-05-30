import os
import pytest
import typer

from tagkit.cli.file_resolver import FileResolver


@pytest.fixture
def temp_files(tmp_path):
    """Create temporary test files"""
    test_path = tmp_path / "file_resolver_test_files"
    test_path.mkdir()

    # Create test files
    (test_path / "test1.jpg").touch()
    (test_path / "test2.jpg").touch()
    (test_path / "test.txt").touch()
    # Create subdirectory with files
    subdir = test_path / "subdir"
    subdir.mkdir()
    (subdir / "test3.jpg").touch()
    (subdir / "test4.txt").touch()

    cwd = os.getcwd()
    os.chdir(test_path)
    yield test_path
    os.chdir(cwd)


def test_resolve_single_file(temp_files):
    """Test resolving a single file path"""
    file_path = temp_files / "test1.jpg"
    resolver = FileResolver(str(file_path))
    assert len(resolver.files) == 1
    assert resolver.files[0] == file_path


def test_resolve_nonexistent_file(temp_files):
    """Test resolving a nonexistent file path"""
    resolver = FileResolver(str(temp_files / "nonexistent.jpg"))
    assert len(resolver.files) == 0


def test_resolve_glob_explicit(temp_files):
    """Test resolving files using explicit glob mode"""
    resolver = FileResolver(str(temp_files / "*.jpg"), glob_mode=True)
    assert len(resolver.files) == 2
    assert all(f.suffix == ".jpg" for f in resolver.files)


def test_resolve_glob_implicit(temp_files):
    """Test resolving files using implicit glob pattern"""
    resolver = FileResolver(str(temp_files / "*.jpg"))
    assert len(resolver.files) == 2
    assert all(f.suffix == ".jpg" for f in resolver.files)


def test_resolve_glob_recursive(temp_files):
    """Test resolving files using recursive glob pattern"""
    resolver = FileResolver(str(temp_files / "**/*.jpg"), glob_mode=True)
    assert len(resolver.files) == 3  # 2 in root, 1 in subdir
    assert all(f.suffix == ".jpg" for f in resolver.files)


def test_resolve_regex_explicit(temp_files):
    """Test resolving files using explicit regex mode"""
    resolver = FileResolver(r".*\.jpg$", regex_mode=True)
    assert len(resolver.files) == 2  # 2 in root. Regex search is not recursive.
    assert all(f.suffix == ".jpg" for f in resolver.files)


def test_resolve_regex_implicit(temp_files):
    """Test resolving files using implicit regex pattern"""
    # When file doesn't exist and glob fails, regex is tried
    resolver = FileResolver(r"test[0-9]\.jpg")
    assert len(resolver.files) == 2  # test1.jpg, test2.jpg
    assert all(f.name.startswith("test") and f.suffix == ".jpg" for f in resolver.files)


def test_resolve_glob_and_regex_error():
    """Test that specifying both glob and regex modes raises an error"""
    with pytest.raises(
        typer.BadParameter, match="Cannot specify both --glob and --regex"
    ):
        FileResolver("pattern", glob_mode=True, regex_mode=True)


def test_resolve_complex_regex(temp_files):
    """Test resolving files using a more complex regex pattern"""
    resolver = FileResolver(r"test[1-2]?\.(jpg|txt)$", regex_mode=True)
    assert len(resolver.files) == 3  # test1.jpg, test2.jpg, test.txt
    assert all(f.name.startswith("test") for f in resolver.files)


def test_resolve_no_matches(temp_files):
    """Test resolving pattern with no matches"""
    resolver = FileResolver(str(temp_files / "*.png"), glob_mode=True)
    assert len(resolver.files) == 0


def test_resolve_absolute_path(temp_files):
    """Test resolving an absolute file path"""
    file_path = temp_files / "test1.jpg"
    resolver = FileResolver(str(file_path.absolute()))
    assert len(resolver.files) == 1
    assert resolver.files[0] == file_path


def test_resolve_relative_path(temp_files, monkeypatch):
    """Test resolving a relative file path"""
    # Change working directory to temp_files
    monkeypatch.chdir(temp_files)
    resolver = FileResolver("test1.jpg")
    assert len(resolver.files) == 1
    assert resolver.files[0].name == "test1.jpg"


def test_glob_in_other_directory(temp_files, tmp_path):
    """Test glob mode in a directory other than the current working directory"""
    # Create a subdirectory with some files
    other_dir = tmp_path / "other_dir"
    other_dir.mkdir()
    (other_dir / "file1.txt").touch()
    (other_dir / "file2.txt").touch()
    (other_dir / "image.jpg").touch()

    # Use glob mode with a path to the other directory
    resolver = FileResolver(str(other_dir / "*.txt"), glob_mode=True)

    # Verify results
    assert len(resolver.files) == 2
    assert all(f.suffix == ".txt" for f in resolver.files)
    assert all(str(f).startswith(str(other_dir)) for f in resolver.files)


def test_regex_in_other_directory(temp_files, tmp_path):
    """Test regex mode in a directory other than the current working directory"""
    # Create a subdirectory with some files
    other_dir = tmp_path / "regex_dir"
    other_dir.mkdir()
    (other_dir / "test1.jpg").touch()
    (other_dir / "test2.jpg").touch()
    (other_dir / "other.png").touch()

    # Use regex mode with a path to the other directory
    resolver = FileResolver(str(other_dir / r"test[0-9]\.jpg"), regex_mode=True)

    # Verify results
    assert len(resolver.files) == 2
    assert all(f.name.startswith("test") for f in resolver.files)
    assert all(f.suffix == ".jpg" for f in resolver.files)
    assert all(str(f).startswith(str(other_dir)) for f in resolver.files)
