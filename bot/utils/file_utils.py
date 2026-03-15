from pathlib import Path


def ensure_file_dir_exists(file_path: Path) -> None:
    """Create all parent directories for the given file path if they do not exist.

    Args:
        file_path: The path to the file whose parent directories should be created.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)


def ensure_file_exists(file_path: Path) -> None:
    """Ensure the given file exists, creating it and its parent directories if necessary.

    Args:
        file_path: The path to the file that should exist.
    """
    ensure_file_dir_exists(file_path)
    file_path.touch(exist_ok=True)
