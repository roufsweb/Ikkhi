"""
Cross-platform path resolution engine for development and frozen PyInstaller runtimes.
"""

import os
import sys
from pathlib import Path


def is_frozen() -> bool:
    """Determine whether the application is running inside a PyInstaller frozen binary."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def get_bundle_dir() -> Path:
    """
    Acquire the base directory of the bundled resources.
    In frozen state, this maps to sys._MEIPASS; otherwise, the repository root.
    """
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent.parent


def get_executable_dir() -> Path:
    """
    Acquire the directory containing the running executable or python script.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent.parent


def get_resource_path(relative_path: str | Path) -> Path:
    """
    Resolve a static read-only asset (e.g., config templates, icons, default profiles).
    """
    return get_bundle_dir() / relative_path


def get_storage_dir() -> Path:
    """
    Acquire a guaranteed writable directory for user-specific databases and profiles.
    In frozen distribution, defaults to %APPDATA%/Ikkhi/storage to prevent permission errors.
    """
    if getattr(sys, "frozen", False):
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) / "Ikkhi" / "storage" if appdata else get_executable_dir() / "storage"
    else:
        base = get_bundle_dir() / "storage"

    base.mkdir(parents=True, exist_ok=True)
    return base


def get_profiles_dir() -> Path:
    """Acquire the writable directory dedicated to adaptive application profiles."""
    profiles_dir = get_storage_dir() / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    return profiles_dir


def resolve_config_path(explicit_path: str | Path = "config.yaml") -> Path:
    """
    Determine the optimal configuration file path.
    Prioritizes:
    1. Explicit path if it exists on disk.
    2. Local config.yaml adjacent to the executable.
    3. Storage-based config.yaml in %APPDATA%/Ikkhi.
    4. Bundled fallback template within sys._MEIPASS.
    """
    target = Path(explicit_path)
    if target.is_file():
        return target

    exe_adjacent = get_executable_dir() / "config.yaml"
    if exe_adjacent.is_file():
        return exe_adjacent

    storage_cfg = get_storage_dir().parent / "config.yaml"
    if storage_cfg.is_file():
        return storage_cfg

    bundled_cfg = get_resource_path("config.yaml")
    if bundled_cfg.is_file():
        return bundled_cfg

    return target
