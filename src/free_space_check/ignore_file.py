"""Manage the .ignore file for persisted path exclusions."""

import os
from pathlib import Path

IGNORE_FILE_NAME: str = ".ignore"


def get_ignore_file_path() -> Path:
    """Return the path to the .ignore file in the project root."""
    return Path(__file__).resolve().parent.parent.parent / IGNORE_FILE_NAME


def _normalize_path(dir_path: str) -> str:
    """Normalize a path for consistent comparison."""
    return dir_path.strip().rstrip("\\/").lower()


def load_ignore_paths(ignore_path: Path) -> frozenset[str]:
    """Load ignored paths from the .ignore file, normalized to lowercase."""
    if not ignore_path.exists():
        return frozenset()
    lines = ignore_path.read_text(encoding="utf-8").splitlines()
    paths: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        paths.add(_normalize_path(stripped))
    return frozenset(paths)


def add_ignore_path(ignore_path: Path, dir_path: str) -> None:
    """Add a path to the .ignore file. Avoids duplicates."""
    normalized = _normalize_path(dir_path)
    existing = load_ignore_paths(ignore_path)
    if normalized in existing:
        print(f"Already ignored: {dir_path}")
        return
    with open(ignore_path, "a", encoding="utf-8") as f:
        if not ignore_path.exists() or ignore_path.stat().st_size == 0:
            f.write("# Ignored paths\n")
        f.write(f"{dir_path.strip().rstrip(os.sep)}\n")
    print(f"Added to .ignore: {dir_path.strip().rstrip(os.sep)}")


def remove_ignore_path(ignore_path: Path, dir_path: str) -> None:
    """Remove a path from the .ignore file."""
    normalized = _normalize_path(dir_path)
    if not ignore_path.exists():
        print(f"Not found in .ignore: {dir_path}")
        return
    lines = ignore_path.read_text(encoding="utf-8").splitlines()
    new_lines: list[str] = []
    found = False
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            if _normalize_path(stripped) == normalized:
                found = True
                continue
        new_lines.append(line)
    if found:
        ignore_path.write_text(
            "\n".join(new_lines) + "\n", encoding="utf-8"
        )
        print(f"Removed from .ignore: {dir_path}")
    else:
        print(f"Not found in .ignore: {dir_path}")


def list_ignore_paths(ignore_path: Path) -> list[str]:
    """Return current entries from the .ignore file (original casing)."""
    if not ignore_path.exists():
        return []
    lines = ignore_path.read_text(encoding="utf-8").splitlines()
    entries: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            entries.append(stripped)
    return entries
