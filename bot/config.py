import os
import sys
from pathlib import Path

APP_NAME = "cna"
APP_DESCRIPTION = "CLI assistant for contacts and notes management"

HOME_DIR = Path.home()


def _path_from_env(env_var: str, default: Path) -> Path:
    """Resolve a filesystem path from an environment variable with a fallback.

    Args:
        env_var: Name of the environment variable to read.
        default: Path to use when the environment variable is not set.

    Returns:
        The path obtained from the environment variable (expanded) or *default*.
    """
    return Path(os.environ.get(env_var, default)).expanduser()


def get_data_dir(*, use_xdg_on_macos: bool = False) -> Path:
    """Return the OS-specific directory for persistent app data like pickle files."""
    if sys.platform == "darwin":
        if use_xdg_on_macos:
            # Some CLI tools prefer XDG-style dirs on macOS for consistency with Linux.
            base_dir = _path_from_env("XDG_DATA_HOME", HOME_DIR / ".local" / "share")
            return base_dir / APP_NAME

        # Native macOS app data lives under Application Support.
        return HOME_DIR / "Library" / "Application Support" / APP_NAME

    if os.name == "nt":
        # Windows app-local data belongs in Local AppData.
        base_dir = _path_from_env("LOCALAPPDATA", HOME_DIR / "AppData" / "Local")
        return base_dir / APP_NAME

    # Linux and other Unix-like systems should follow XDG_DATA_HOME.
    base_dir = _path_from_env("XDG_DATA_HOME", HOME_DIR / ".local" / "share")
    return base_dir / APP_NAME


def get_state_dir(*, use_xdg_on_macos: bool = False) -> Path:
    """Return the OS-specific directory for state files like commands history."""
    if sys.platform == "darwin":
        if use_xdg_on_macos:
            # Some CLI tools prefer XDG-style dirs on macOS for consistency with Linux.
            base_dir = _path_from_env("XDG_STATE_HOME", HOME_DIR / ".local" / "state")
            return base_dir / APP_NAME

        # Native macOS commonly stores app state alongside other app support files.
        return HOME_DIR / "Library" / "Application Support" / APP_NAME

    if os.name == "nt":
        # Windows has no direct XDG-style state dir, so Local AppData is the closest fit.
        base_dir = _path_from_env("LOCALAPPDATA", HOME_DIR / "AppData" / "Local")
        return base_dir / APP_NAME

    # Linux and other Unix-like systems should follow XDG_STATE_HOME.
    base_dir = _path_from_env("XDG_STATE_HOME", HOME_DIR / ".local" / "state")
    return base_dir / APP_NAME


DATA_DIR = get_data_dir(use_xdg_on_macos=True)
STATE_DIR = get_state_dir(use_xdg_on_macos=True)

DEFAULT_CONTACTS_FILE = DATA_DIR / "contacts.pkl"
DEFAULT_NOTES_FILE = DATA_DIR / "notes.pkl"
DEFAULT_HISTORY_FILE = STATE_DIR / "history"
