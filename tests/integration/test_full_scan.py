"""Integration tests for full scan workflow."""

import os
import tempfile
import time

from free_space_check.config import ScanConfig
from free_space_check.scanner import scan_directory


class TestFullScanWorkflow:
    def test_scan_sort_and_truncate(self) -> None:
        """End-to-end: scan, sort by mtime descending, and truncate to top_n."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files with distinct mtimes
            for i in range(5):
                path = os.path.join(tmpdir, f"file_{i}.txt")
                with open(path, "w") as f:
                    f.write(f"content {i}" * 100)
                # Ensure distinct mtimes
                time.sleep(0.05)

            config = ScanConfig(drive=tmpdir, top_n=3)
            result = scan_directory(config)

            assert result.scanned_count == 5

            # Sort by mtime descending and truncate
            result.files.sort(key=lambda f: f.mtime, reverse=True)
            top = result.files[: config.top_n]

            assert len(top) == 3
            # Verify descending order
            assert top[0].mtime >= top[1].mtime >= top[2].mtime
            # Most recent should be file_4
            assert top[0].path.endswith("file_4.txt")

    def test_scan_with_mixed_sizes_and_extensions(self) -> None:
        """Test combined size + extension filtering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Small .txt
            with open(os.path.join(tmpdir, "small.txt"), "w") as f:
                f.write("x")
            # Large .txt
            with open(os.path.join(tmpdir, "large.txt"), "w") as f:
                f.write("x" * 2000)
            # Large .log
            with open(os.path.join(tmpdir, "large.log"), "w") as f:
                f.write("x" * 2000)
            # Small .log
            with open(os.path.join(tmpdir, "small.log"), "w") as f:
                f.write("x")

            config = ScanConfig(
                drive=tmpdir,
                min_size=1000,
                extensions=frozenset({".txt"}),
            )
            result = scan_directory(config)

            assert result.scanned_count == 1
            assert result.files[0].path.endswith("large.txt")

    def test_scan_deeply_nested_structure(self) -> None:
        """Test scanning a deeply nested directory tree."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure: a/b/c/d/e/file.txt
            current = tmpdir
            for name in ["a", "b", "c", "d", "e"]:
                current = os.path.join(current, name)
                os.makedirs(current, exist_ok=True)

            with open(os.path.join(current, "deep.txt"), "w") as f:
                f.write("deep content")

            config = ScanConfig(drive=tmpdir)
            result = scan_directory(config)

            assert result.scanned_count == 1
            assert result.files[0].path.endswith("deep.txt")
