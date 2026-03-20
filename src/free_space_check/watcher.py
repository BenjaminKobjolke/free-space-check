"""Watch mode: re-scan periodically and show only new/changed files."""

import dataclasses
import logging
import time

from free_space_check.config import ScanConfig
from free_space_check.formatter import print_changes, print_results
from free_space_check.ignore_file import get_ignore_file_path, load_ignore_paths
from free_space_check.scanner import FileInfo, scan_directory

logger = logging.getLogger(__name__)


def watch_loop(config: ScanConfig) -> None:
    """Run initial scan, then re-scan periodically showing only changes."""
    if config.watch_interval is None:
        return

    interval = config.watch_interval

    # Initial scan
    logger.info("Scanning %s ...", config.drive)
    start_time = time.time()
    result = scan_directory(config)

    result.files.sort(key=lambda f: f.mtime, reverse=True)
    top_results = result.files[: config.top_n]
    elapsed = time.time() - start_time
    print_results(
        top_results, config, elapsed, result.scanned_count, result.error_count
    )

    # Build known files dict from ALL results
    known_files: dict[str, tuple[int, float]] = {
        f.path: (f.size, f.mtime) for f in result.files
    }

    # Watch loop
    while True:
        logger.info(
            "Watching... next scan in %ss - press Ctrl+C to stop", interval
        )
        time.sleep(interval)

        # Reload .ignore so changes made in another terminal take effect
        updated_ignores = load_ignore_paths(get_ignore_file_path())
        config = dataclasses.replace(config, ignore_paths=updated_ignores)

        new_result = scan_directory(config)
        new_files_dict: dict[str, tuple[int, float]] = {
            f.path: (f.size, f.mtime) for f in new_result.files
        }
        file_lookup: dict[str, FileInfo] = {f.path: f for f in new_result.files}

        changes: list[tuple[FileInfo, str]] = []
        for path, (size, mtime) in new_files_dict.items():
            if path not in known_files:
                changes.append((file_lookup[path], "NEW"))
            elif known_files[path] != (size, mtime):
                changes.append((file_lookup[path], "CHANGED"))

        if changes:
            changes.sort(key=lambda x: x[0].mtime, reverse=True)
            print_changes(changes)
        else:
            logger.info("No changes detected")

        known_files = new_files_dict
