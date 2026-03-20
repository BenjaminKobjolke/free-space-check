"""Tests for formatter module."""

from free_space_check.formatter import format_size, format_time


class TestFormatSize:
    def test_zero_bytes(self) -> None:
        assert format_size(0) == "0 B"

    def test_small_bytes(self) -> None:
        assert format_size(512) == "512 B"

    def test_one_kb(self) -> None:
        assert format_size(1024) == "1.0 KB"

    def test_megabytes(self) -> None:
        assert format_size(1024 * 1024) == "1.0 MB"

    def test_gigabytes(self) -> None:
        assert format_size(1024 ** 3) == "1.0 GB"

    def test_terabytes(self) -> None:
        assert format_size(1024 ** 4) == "1.0 TB"

    def test_fractional_mb(self) -> None:
        result = format_size(int(1.5 * 1024 * 1024))
        assert result == "1.5 MB"

    def test_just_under_kb(self) -> None:
        assert format_size(1023) == "1023 B"


class TestFormatTime:
    def test_known_timestamp(self) -> None:
        # 2024-01-01 00:00:00 UTC = 1704067200
        result = format_time(1704067200.0)
        # Just check format, not exact value (timezone dependent)
        assert len(result) == 19
        assert result[4] == "-"
        assert result[7] == "-"
        assert result[10] == " "
        assert result[13] == ":"
        assert result[16] == ":"
