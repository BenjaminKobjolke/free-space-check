"""CSV export for scan results."""

import csv

from free_space_check.formatter import format_size, format_time
from free_space_check.scanner import FileInfo


def write_csv(results: list[FileInfo], csv_path: str) -> None:
    """Write results to a CSV file."""
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Rank", "Modified", "Size_Bytes", "Size_Human", "Path"])
        for i, file_info in enumerate(results, 1):
            writer.writerow([
                i,
                format_time(file_info.mtime),
                file_info.size,
                format_size(file_info.size),
                file_info.path,
            ])
    print(f"\nResults written to {csv_path}")
