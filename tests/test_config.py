"""Tests for config module."""

import argparse

import pytest

from free_space_check.config import ScanConfig, parse_extensions, parse_size


class TestParseSize:
    def test_bytes_implicit(self) -> None:
        assert parse_size("1024") == 1024

    def test_bytes_explicit(self) -> None:
        assert parse_size("512B") == 512

    def test_kilobytes(self) -> None:
        assert parse_size("1KB") == 1024

    def test_megabytes(self) -> None:
        assert parse_size("100MB") == 100 * 1024 ** 2

    def test_gigabytes(self) -> None:
        assert parse_size("2GB") == 2 * 1024 ** 3

    def test_terabytes(self) -> None:
        assert parse_size("1TB") == 1024 ** 4

    def test_fractional(self) -> None:
        assert parse_size("1.5GB") == int(1.5 * 1024 ** 3)

    def test_with_whitespace(self) -> None:
        assert parse_size("  100MB  ") == 100 * 1024 ** 2

    def test_case_insensitive(self) -> None:
        assert parse_size("100mb") == 100 * 1024 ** 2

    def test_invalid_raises(self) -> None:
        with pytest.raises(argparse.ArgumentTypeError):
            parse_size("not_a_size")

    def test_empty_raises(self) -> None:
        with pytest.raises(argparse.ArgumentTypeError):
            parse_size("")

    def test_zero(self) -> None:
        assert parse_size("0") == 0


class TestParseExtensions:
    def test_single(self) -> None:
        assert parse_extensions(".log") == frozenset({".log"})

    def test_multiple(self) -> None:
        result = parse_extensions(".log,.tmp,.iso")
        assert result == frozenset({".log", ".tmp", ".iso"})

    def test_without_dot(self) -> None:
        result = parse_extensions("log,tmp")
        assert result == frozenset({".log", ".tmp"})

    def test_with_spaces(self) -> None:
        result = parse_extensions(" .log , .tmp ")
        assert result == frozenset({".log", ".tmp"})

    def test_case_normalized(self) -> None:
        result = parse_extensions(".LOG,.TMP")
        assert result == frozenset({".log", ".tmp"})


class TestScanConfig:
    def test_defaults(self) -> None:
        config = ScanConfig()
        assert config.drive == "C:\\"
        assert config.top_n == 50
        assert config.min_size == 0
        assert config.extensions is None
        assert config.watch_interval is None
        assert config.csv_path is None

    def test_custom_values(self) -> None:
        config = ScanConfig(
            drive="D:\\",
            top_n=20,
            min_size=1024,
            extensions=frozenset({".log"}),
            watch_interval=30,
            csv_path="results.csv",
        )
        assert config.drive == "D:\\"
        assert config.top_n == 20
        assert config.min_size == 1024
        assert config.extensions == frozenset({".log"})
        assert config.watch_interval == 30
        assert config.csv_path == "results.csv"

    def test_frozen(self) -> None:
        config = ScanConfig()
        with pytest.raises(AttributeError):
            config.drive = "D:\\"  # type: ignore[misc]
