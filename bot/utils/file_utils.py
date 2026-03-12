from pathlib import Path


def ensure_file_dir_exists(file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)


def ensure_file_exists(file_path: Path) -> None:
    ensure_file_dir_exists(file_path)
    file_path.touch(exist_ok=True)
