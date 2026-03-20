"""Core directory scanning logic using os.scandir."""

import logging
import os
import sys
from dataclasses import dataclass

from free_space_check.config import PROGRESS_INTERVAL, ScanConfig, ScanStats

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FileInfo:
    """Information about a scanned file."""

    path: str
    size: int
    mtime: float


@dataclass
class ScanResult:
    """Result of a directory scan."""

    files: list[FileInfo]
    scanned_count: int
    error_count: int


def _is_ignored(path: str, ignore_paths: frozenset[str]) -> bool:
    """Check if a full path matches any ignored path prefix."""
    if not ignore_paths:
        return False
    normalized = path.lower()
    return any(
        normalized == ip or normalized.startswith(ip + "\\")
        or normalized.startswith(ip + "/")
        for ip in ignore_paths
    )


def scan_directory(config: ScanConfig) -> ScanResult:
    """Scan directory tree iteratively using os.scandir for speed."""
    results: list[FileInfo] = []
    stats = ScanStats()
    stack: list[str] = [config.drive]

    while stack:
        directory = stack.pop()
        try:
            entries = os.scandir(directory)
        except (PermissionError, OSError):
            stats.error_count += 1
            continue

        with entries:
            for entry in entries:
                try:
                    if entry.is_dir(follow_symlinks=False):
                        if entry.name.lower() in config.skip_dirs:
                            continue
                        if _is_ignored(entry.path, config.ignore_paths):
                            continue
                        stack.append(entry.path)
                    elif entry.is_file(follow_symlinks=False):
                        st = entry.stat(follow_symlinks=False)
                        if st.st_size < config.min_size:
                            continue
                        if config.extensions:
                            ext = os.path.splitext(entry.name)[1].lower()
                            if ext not in config.extensions:
                                continue
                        results.append(
                            FileInfo(
                                path=entry.path,
                                size=st.st_size,
                                mtime=st.st_mtime,
                            )
                        )
                        stats.scanned_count += 1
                        if stats.scanned_count % PROGRESS_INTERVAL == 0:
                            print(
                                f"\r[Progress] {stats.scanned_count:,} files, "
                                f"{stats.error_count:,} errors",
                                end="", flush=True, file=sys.stderr,
                            )
                except (PermissionError, OSError):
                    stats.error_count += 1

    print(
        f"\r[Done] {stats.scanned_count:,} files, "
        f"{stats.error_count:,} errors" + " " * 20,
        file=sys.stderr,
    )
    return ScanResult(
        files=results,
        scanned_count=stats.scanned_count,
        error_count=stats.error_count,
    )
