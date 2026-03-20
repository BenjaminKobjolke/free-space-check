"""Tests for scanner module."""

import os
import tempfile

from free_space_check.config import ScanConfig
from free_space_check.scanner import scan_directory


class TestScanDirectory:
    def test_scan_empty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ScanConfig(drive=tmpdir)
            result = scan_directory(config)
            assert result.files == []
            assert result.scanned_count == 0
            assert result.error_count == 0

    def test_scan_finds_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            for name in ["a.txt", "b.txt", "c.log"]:
                path = os.path.join(tmpdir, name)
                with open(path, "w") as f:
                    f.write("x" * 100)

            config = ScanConfig(drive=tmpdir)
            result = scan_directory(config)
            assert result.scanned_count == 3
            assert len(result.files) == 3

    def test_scan_min_size_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Small file
            small = os.path.join(tmpdir, "small.txt")
            with open(small, "w") as f:
                f.write("x")
            # Large file
            large = os.path.join(tmpdir, "large.txt")
            with open(large, "w") as f:
                f.write("x" * 1000)

            config = ScanConfig(drive=tmpdir, min_size=500)
            result = scan_directory(config)
            assert result.scanned_count == 1
            assert result.files[0].path == large

    def test_scan_extension_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ["a.txt", "b.log", "c.txt"]:
                path = os.path.join(tmpdir, name)
                with open(path, "w") as f:
                    f.write("content")

            config = ScanConfig(
                drive=tmpdir,
                extensions=frozenset({".txt"}),
            )
            result = scan_directory(config)
            assert result.scanned_count == 2
            assert all(f.path.endswith(".txt") for f in result.files)

    def test_scan_nested_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "sub")
            os.makedirs(subdir)
            with open(os.path.join(tmpdir, "root.txt"), "w") as f:
                f.write("root")
            with open(os.path.join(subdir, "nested.txt"), "w") as f:
                f.write("nested")

            config = ScanConfig(drive=tmpdir)
            result = scan_directory(config)
            assert result.scanned_count == 2

    def test_scan_skips_configured_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skip = os.path.join(tmpdir, "skipme")
            os.makedirs(skip)
            with open(os.path.join(skip, "hidden.txt"), "w") as f:
                f.write("should not appear")
            with open(os.path.join(tmpdir, "visible.txt"), "w") as f:
                f.write("should appear")

            config = ScanConfig(
                drive=tmpdir,
                skip_dirs=frozenset({"skipme"}),
            )
            result = scan_directory(config)
            assert result.scanned_count == 1
            assert result.files[0].path.endswith("visible.txt")

    def test_scan_skips_ignore_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            ignored = os.path.join(tmpdir, "ignored_dir")
            os.makedirs(ignored)
            nested = os.path.join(ignored, "sub")
            os.makedirs(nested)
            with open(os.path.join(nested, "deep.txt"), "w") as f:
                f.write("should not appear")
            with open(os.path.join(tmpdir, "visible.txt"), "w") as f:
                f.write("should appear")

            config = ScanConfig(
                drive=tmpdir,
                ignore_paths=frozenset({ignored.lower()}),
            )
            result = scan_directory(config)
            assert result.scanned_count == 1
            assert result.files[0].path.endswith("visible.txt")
