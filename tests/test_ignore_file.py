"""Tests for ignore_file module."""

from pathlib import Path

from free_space_check.ignore_file import (
    add_ignore_path,
    list_ignore_paths,
    load_ignore_paths,
    remove_ignore_path,
)


class TestLoadIgnorePaths:
    def test_missing_file(self, tmp_path: Path) -> None:
        result = load_ignore_paths(tmp_path / ".ignore")
        assert result == frozenset()

    def test_empty_file(self, tmp_path: Path) -> None:
        ignore = tmp_path / ".ignore"
        ignore.write_text("", encoding="utf-8")
        assert load_ignore_paths(ignore) == frozenset()

    def test_skips_comments_and_blanks(self, tmp_path: Path) -> None:
        ignore = tmp_path / ".ignore"
        ignore.write_text(
            "# comment\n\nC:\\Users\\test\n  \n# another\n",
            encoding="utf-8",
        )
        result = load_ignore_paths(ignore)
        assert result == frozenset({"c:\\users\\test"})

    def test_strips_trailing_slashes(self, tmp_path: Path) -> None:
        ignore = tmp_path / ".ignore"
        ignore.write_text("C:\\Users\\test\\\n", encoding="utf-8")
        result = load_ignore_paths(ignore)
        assert result == frozenset({"c:\\users\\test"})

    def test_normalizes_to_lowercase(self, tmp_path: Path) -> None:
        ignore = tmp_path / ".ignore"
        ignore.write_text("C:\\Users\\XIDA\\AppData\n", encoding="utf-8")
        result = load_ignore_paths(ignore)
        assert "c:\\users\\xida\\appdata" in result

    def test_multiple_paths(self, tmp_path: Path) -> None:
        ignore = tmp_path / ".ignore"
        ignore.write_text("C:\\path1\nD:\\path2\n", encoding="utf-8")
        result = load_ignore_paths(ignore)
        assert len(result) == 2


class TestAddIgnorePath:
    def test_creates_file_and_adds(self, tmp_path: Path) -> None:
        ignore = tmp_path / ".ignore"
        add_ignore_path(ignore, "C:\\Users\\test")
        assert ignore.exists()
        result = load_ignore_paths(ignore)
        assert "c:\\users\\test" in result

    def test_avoids_duplicates(self, tmp_path: Path) -> None:
        ignore = tmp_path / ".ignore"
        add_ignore_path(ignore, "C:\\Users\\test")
        add_ignore_path(ignore, "C:\\Users\\test")
        entries = list_ignore_paths(ignore)
        assert len(entries) == 1

    def test_case_insensitive_duplicate(self, tmp_path: Path) -> None:
        ignore = tmp_path / ".ignore"
        add_ignore_path(ignore, "C:\\Users\\Test")
        add_ignore_path(ignore, "c:\\users\\test")
        entries = list_ignore_paths(ignore)
        assert len(entries) == 1

    def test_strips_trailing_separator(self, tmp_path: Path) -> None:
        ignore = tmp_path / ".ignore"
        add_ignore_path(ignore, "C:\\Users\\test\\")
        entries = list_ignore_paths(ignore)
        assert entries[0] == "C:\\Users\\test"


class TestRemoveIgnorePath:
    def test_removes_existing(self, tmp_path: Path) -> None:
        ignore = tmp_path / ".ignore"
        add_ignore_path(ignore, "C:\\Users\\test")
        remove_ignore_path(ignore, "C:\\Users\\test")
        assert load_ignore_paths(ignore) == frozenset()

    def test_case_insensitive_remove(self, tmp_path: Path) -> None:
        ignore = tmp_path / ".ignore"
        add_ignore_path(ignore, "C:\\Users\\Test")
        remove_ignore_path(ignore, "c:\\users\\test")
        assert load_ignore_paths(ignore) == frozenset()

    def test_missing_file(self, tmp_path: Path, capsys: object) -> None:
        ignore = tmp_path / ".ignore"
        remove_ignore_path(ignore, "C:\\nonexistent")
        # Should not raise

    def test_preserves_other_entries(self, tmp_path: Path) -> None:
        ignore = tmp_path / ".ignore"
        add_ignore_path(ignore, "C:\\path1")
        add_ignore_path(ignore, "C:\\path2")
        remove_ignore_path(ignore, "C:\\path1")
        result = load_ignore_paths(ignore)
        assert "c:\\path2" in result
        assert "c:\\path1" not in result


class TestListIgnorePaths:
    def test_missing_file(self, tmp_path: Path) -> None:
        assert list_ignore_paths(tmp_path / ".ignore") == []

    def test_returns_original_casing(self, tmp_path: Path) -> None:
        ignore = tmp_path / ".ignore"
        ignore.write_text("C:\\Users\\XIDA\\AppData\n", encoding="utf-8")
        entries = list_ignore_paths(ignore)
        assert entries == ["C:\\Users\\XIDA\\AppData"]
