"""Entry point for the free-space-check CLI."""

import argparse
import logging
import os
import sys
import time

from free_space_check.config import (
    DEFAULT_DRIVE,
    DEFAULT_TOP_N,
    ScanConfig,
    parse_extensions,
    parse_size,
)
from free_space_check.csv_export import write_csv
from free_space_check.formatter import print_results
from free_space_check.ignore_file import (
    add_ignore_path,
    get_ignore_file_path,
    list_ignore_paths,
    load_ignore_paths,
    remove_ignore_path,
)
from free_space_check.logging_setup import setup_logging
from free_space_check.scanner import scan_directory
from free_space_check.watcher import watch_loop

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Find the most recently modified files on a drive.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  free-space-check\n"
            "  free-space-check -n 20 -s 100MB\n"
            '  free-space-check -d "D:\\\\" -s 500MB --csv results.csv\n'
            '  free-space-check -e ".log,.tmp" -s 10MB\n'
            "  free-space-check -w 30 -s 100MB"
        ),
    )
    parser.add_argument(
        "-d", "--drive", default=DEFAULT_DRIVE,
        help=f"Root path to scan (default: {DEFAULT_DRIVE})",
    )
    parser.add_argument(
        "-n", "--top", type=int, default=DEFAULT_TOP_N,
        help=f"Number of results to display (default: {DEFAULT_TOP_N})",
    )
    parser.add_argument(
        "-s", "--min-size", type=parse_size, default=0,
        help="Minimum file size filter, e.g. 100MB, 1GB (default: 0)",
    )
    parser.add_argument(
        "-e", "--extensions", default=None,
        help="Comma-separated extensions to include, e.g. .log,.tmp,.iso",
    )
    parser.add_argument(
        "--csv", default=None, metavar="FILE",
        help="Export results to a CSV file",
    )
    parser.add_argument(
        "-w", "--watch", type=int, nargs="?", const=60, default=None,
        metavar="SECONDS",
        help="Watch mode: re-scan every N seconds showing only changes (default: 60)",
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--add-ignore", metavar="PATH",
        help="Add a directory path to .ignore and exit",
    )
    parser.add_argument(
        "--remove-ignore", metavar="PATH",
        help="Remove a directory path from .ignore and exit",
    )
    parser.add_argument(
        "--list-ignores", action="store_true",
        help="List all ignored paths from .ignore and exit",
    )
    return parser


def main() -> None:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    setup_logging(debug=args.debug)

    # Handle ignore management commands
    ignore_path = get_ignore_file_path()
    if args.add_ignore:
        add_ignore_path(ignore_path, args.add_ignore)
        sys.exit(0)
    if args.remove_ignore:
        remove_ignore_path(ignore_path, args.remove_ignore)
        sys.exit(0)
    if args.list_ignores:
        entries = list_ignore_paths(ignore_path)
        if entries:
            print("Ignored paths:")
            for entry in entries:
                print(f"  {entry}")
        else:
            print("No ignored paths configured.")
        sys.exit(0)

    extensions = parse_extensions(args.extensions) if args.extensions else None
    ignore_paths = load_ignore_paths(ignore_path)

    config = ScanConfig(
        drive=args.drive,
        top_n=args.top,
        min_size=args.min_size,
        extensions=extensions,
        ignore_paths=ignore_paths,
        watch_interval=args.watch,
        csv_path=args.csv,
    )

    if not os.path.isdir(config.drive):
        logger.error("'%s' is not a valid directory.", config.drive)
        sys.exit(1)

    try:
        if config.watch_interval is not None:
            watch_loop(config)
        else:
            logger.info("Scanning %s ...", config.drive)
            start_time = time.time()
            result = scan_directory(config)

            result.files.sort(key=lambda f: f.mtime, reverse=True)
            top_results = result.files[: config.top_n]
            elapsed = time.time() - start_time

            print_results(
                top_results, config, elapsed,
                result.scanned_count, result.error_count,
            )

            if config.csv_path:
                write_csv(top_results, config.csv_path)
    except KeyboardInterrupt:
        print("\n\nStopped.", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
