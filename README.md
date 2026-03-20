# free-space-check

Find the most recently modified files on a drive or directory to identify what's consuming disk space.

Scans recursively and reports files sorted by modification time, with human-readable sizes. Includes a watch mode to continuously monitor for new/changed files and an ignore list to exclude directories.

## Installation

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.11+.

```bash
install.bat
```

## Usage

### One-shot scan

```bash
# Find 20 most recent files over 100MB on C:
start.bat

# Or run directly
uv run free-space-check -n 20 -s 100MB

# Scan a specific folder (not just whole drives)
uv run free-space-check -d "C:\Users\XIDA\AppData" -s 50MB

# Scan D: drive
uv run free-space-check -d "D:\" -s 500MB

# Filter by extensions
uv run free-space-check -e ".log,.tmp" -s 10MB

# Export to CSV
uv run free-space-check -s 100MB --csv results.csv
```

### Watch mode

Monitor for new/changed files every 30 seconds. After the initial scan, only new or changed files are shown.

```bash
watch.bat

# Or run directly
uv run free-space-check -w 30 -s 100MB

# Watch a specific folder
uv run free-space-check -d "C:\Users\XIDA\Downloads" -w 30
```

### Ignore paths

Exclude directories from scanning. Ignored paths are stored in a `.ignore` file and persist across runs. The watcher reloads `.ignore` before each cycle, so you can add ignores while it's running.

```bash
# Add a path to the ignore list
add_ignore.bat C:\Users\XIDA\AppData\Local\BraveSoftware

# Or run directly
uv run free-space-check --add-ignore "C:\Users\XIDA\AppData\Local\BraveSoftware"

# List all ignored paths
uv run free-space-check --list-ignores

# Remove a path from the ignore list
uv run free-space-check --remove-ignore "C:\Users\XIDA\AppData\Local\BraveSoftware"
```

### CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `-d / --drive` | `C:\` | Root directory or folder to scan |
| `-n / --top` | `50` | Number of results |
| `-s / --min-size` | `0` | Min file size (e.g. `100MB`, `1GB`) |
| `-e / --extensions` | all | Filter by extensions (e.g. `.log,.tmp`) |
| `--csv FILE` | none | Export results to CSV |
| `-w / --watch [SEC]` | off | Watch mode interval (default: 60s) |
| `--add-ignore PATH` | - | Add a directory to `.ignore` and exit |
| `--remove-ignore PATH` | - | Remove a directory from `.ignore` and exit |
| `--list-ignores` | - | List all ignored paths and exit |
| `--debug` | off | Enable debug logging |

### Batch files

| File | Description |
|------|-------------|
| `start.bat` | One-shot scan: top 20 files over 100MB on C: |
| `watch.bat` | Watch mode: re-scan every 30s, any file size |
| `add_ignore.bat PATH` | Add a path to the ignore list |
| `install.bat` | Initial project setup |
| `update.bat` | Update dependencies + lint + test |

## Development

```bash
# Run tests
tools\run_tests.bat

# Run integration tests
tools\run_integration_tests.bat

# Update dependencies
update.bat
```

## Dependencies

No runtime dependencies. Standard library only (Python 3.11+).

Dev dependencies: ruff, mypy, pytest.
