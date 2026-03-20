"""Configuration, constants, and input parsing."""

import argparse
import re
from dataclasses import dataclass, field

SKIP_DIRS: frozenset[str] = frozenset({
    "$recycle.bin",
    "system volume information",
    "recovery",
    "config.msi",
    "$winreagent",
    "$sysreset",
})

PROGRESS_INTERVAL: int = 5000

DEFAULT_DRIVE: str = "C:\\"
DEFAULT_TOP_N: int = 50
DEFAULT_MIN_SIZE: int = 0

SIZE_MULTIPLIERS: dict[str, int] = {
    "B": 1,
    "KB": 1024,
    "MB": 1024 ** 2,
    "GB": 1024 ** 3,
    "TB": 1024 ** 4,
}


@dataclass(frozen=True)
class ScanConfig:
    """Immutable configuration for a scan operation."""

    drive: str = DEFAULT_DRIVE
    top_n: int = DEFAULT_TOP_N
    min_size: int = DEFAULT_MIN_SIZE
    extensions: frozenset[str] | None = None
    skip_dirs: frozenset[str] = SKIP_DIRS
    ignore_paths: frozenset[str] = frozenset()
    watch_interval: int | None = None
    csv_path: str | None = None


def parse_size(size_str: str) -> int:
    """Convert human-readable size string (e.g. '100MB') to bytes."""
    size_str = size_str.strip().upper()
    match = re.match(r"^(\d+(?:\.\d+)?)\s*(B|KB|MB|GB|TB)?$", size_str)
    if not match:
        raise argparse.ArgumentTypeError(
            f"Invalid size: '{size_str}'. Use format like 100MB, 1GB, 500KB"
        )
    value = float(match.group(1))
    unit = match.group(2) or "B"
    return int(value * SIZE_MULTIPLIERS[unit])


def parse_extensions(ext_str: str) -> frozenset[str]:
    """Parse comma-separated extension string into a frozenset."""
    result: set[str] = set()
    for ext in ext_str.split(","):
        ext = ext.strip().lower()
        if not ext.startswith("."):
            ext = f".{ext}"
        result.add(ext)
    return frozenset(result)


@dataclass
class ScanStats:
    """Mutable counters for scan progress tracking."""

    scanned_count: int = 0
    error_count: int = 0
    dirs_with_errors: list[str] = field(default_factory=list)
