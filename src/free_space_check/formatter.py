"""Output formatting for scan results."""

import datetime

from free_space_check.config import ScanConfig
from free_space_check.scanner import FileInfo


def format_size(size_bytes: int | float) -> str:
    """Convert bytes to human-readable string."""
    if size_bytes < 1024:
        return f"{int(size_bytes)} B"
    value = float(size_bytes)
    for unit in ["KB", "MB", "GB", "TB"]:
        value /= 1024
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
    return f"{value:.1f} TB"


def format_time(timestamp: float) -> str:
    """Convert Unix timestamp to readable local time string."""
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def print_results(
    results: list[FileInfo],
    config: ScanConfig,
    elapsed: float,
    scanned: int,
    errors: int,
) -> None:
    """Print formatted table of results."""
    n = len(results)
    print(f"\n=== Top {n} Most Recently Modified Files on {config.drive} ===")
    if config.min_size > 0:
        print(f"(Minimum size filter: {format_size(config.min_size)})")
    print()

    if not results:
        print("No files found matching the criteria.")
        print(f"\nScanned in {elapsed:.1f}s ({errors:,} directories skipped)")
        return

    num_width = len(str(n))
    size_width = max(len(format_size(r.size)) for r in results)
    size_width = max(size_width, 4)

    header = (
        f"{'#':>{num_width}}  "
        f"{'Modified':<19}  "
        f"{'Size':>{size_width}}  "
        f"Path"
    )
    separator = (
        f"{'-' * num_width}  "
        f"{'-' * 19}  "
        f"{'-' * size_width}  "
        f"{'-' * 40}"
    )

    print(header)
    print(separator)
    for i, file_info in enumerate(results, 1):
        print(
            f"{i:>{num_width}}  "
            f"{format_time(file_info.mtime):<19}  "
            f"{format_size(file_info.size):>{size_width}}  "
            f"{file_info.path}"
        )

    print(
        f"\nScanned {scanned:,} files in {elapsed:.1f}s "
        f"({errors:,} directories skipped due to permissions)"
    )


def print_changes(changes: list[tuple[FileInfo, str]]) -> None:
    """Print detected file changes in a compact table."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n--- Changes detected at {now} ---")

    size_width = max(len(format_size(fi.size)) for fi, _ in changes)
    size_width = max(size_width, 4)

    print(
        f"  {'Modified':<19}  "
        f"{'Size':>{size_width}}  "
        f"{'Status':<7}  "
        f"Path"
    )
    for file_info, status in changes:
        print(
            f"  {format_time(file_info.mtime):<19}  "
            f"{format_size(file_info.size):>{size_width}}  "
            f"{status:<7}  "
            f"{file_info.path}"
        )
