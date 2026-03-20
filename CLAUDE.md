# CLAUDE.md

## Project Overview

CLI tool to find recently modified files on a Windows drive. Uses `os.scandir` for fast recursive scanning. No runtime dependencies — stdlib only.

## Project Structure

```
src/free_space_check/
  __main__.py    — CLI entry point, argparse
  config.py      — ScanConfig dataclass, constants, parse_size/parse_extensions
  scanner.py     — FileInfo/ScanResult dataclasses, scan_directory()
  formatter.py   — format_size, format_time, print_results, print_changes
  csv_export.py  — write_csv()
  watcher.py     — watch_loop()
  logging_setup.py — setup_logging()
tests/           — pytest unit tests
tests/integration/ — integration tests
```

## Commands

- `install.bat` — initial setup (uv sync)
- `start.bat` — run one-shot scan
- `watch.bat` — run in watch mode
- `tools\run_tests.bat` — run unit tests
- `tools\run_integration_tests.bat` — run integration tests
- `update.bat` — update dependencies + lint + test

## Rules

### Common Rules
- Use objects (dataclasses) for related values, not loose parameters
- Max 300 lines per file
- Centralize string constants
- Structured logging (Python `logging` module), not `print` to stderr
- DRY: extract shared logic into reusable modules
- No god classes — single responsibility per class
- Input validation at boundaries (argparse type functions)
- Security: never commit secrets, validate all user input

### Python Rules
- `uv` + `pyproject.toml` as single source of truth
- Type hints on all public APIs
- `ruff` for linting/formatting, `mypy` for type checking
- `pytest` for tests (unit + integration)
- Frozen dataclasses for config/value objects
- `spec=` with MagicMock in tests
