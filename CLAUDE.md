# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Cortex CLI** (`cortexapps-cli`), a command-line interface for interacting with the Cortex API (https://cortex.io). The CLI is built with Python 3.11+ using the Typer framework and provides commands for managing catalog entities, scorecards, teams, workflows, integrations, and other Cortex resources.

## Development Commands

### Setup
```bash
# Install dependencies
poetry install

# Set required environment variables for testing
export CORTEX_API_KEY=<your-api-key>
export CORTEX_BASE_URL=https://api.getcortexapp.com  # optional, defaults to this
export CORTEX_API_KEY_VIEWER=<viewer-api-key>  # for viewer permission tests
```

### Testing
The project uses [just](https://just.systems/) for task automation:

```bash
# Run all available recipes
just

# Run all tests (requires prior test-import)
just test-all

# Run import test (prerequisite for other tests - loads test data)
just test-import

# Run a single test file
just test tests/test_catalog.py
```

### Manual Testing
```bash
# Run the CLI locally
poetry run cortex <command>

# Examples:
poetry run cortex catalog list
poetry run cortex -t my-tenant catalog list
```

### Linting & Formatting
Not currently configured in this project.

## Architecture

### Entry Point & CLI Structure
- **Main entry point**: `cortexapps_cli/cli.py` - Defines the main Typer app and global options
- **Command structure**: Each major resource has its own command module in `cortexapps_cli/commands/`
- **Subcommands**: Some commands have nested subcommands in subdirectories (e.g., `backup_commands/`, `integrations_commands/`, `packages_commands/`, `scorecards_commands/`)

### Global Options
All commands inherit global options defined in `cli.py:global_callback()`:
- `-k, --api-key`: API key (or `CORTEX_API_KEY` env var)
- `-u, --url`: Base URL (or `CORTEX_BASE_URL` env var)
- `-c, --config`: Config file path (defaults to `~/.cortex/config`)
- `-t, --tenant`: Tenant alias (defaults to "default")
- `-l, --log-level`: Logging level (defaults to INFO)

### Configuration
The CLI supports two authentication methods:
1. **Config file** (`~/.cortex/config`): INI-style file with sections per tenant
2. **Environment variables**: `CORTEX_API_KEY` and `CORTEX_BASE_URL`

Environment variables take precedence over config file values.

### Client Architecture
- **`CortexClient`** (`cortexapps_cli/cortex_client.py`): Core HTTP client that handles all API requests
  - Provides `get()`, `post()`, `put()`, `patch()`, `delete()` methods
  - `fetch()`: Auto-paginated fetch for list endpoints
  - `fetch_or_get()`: Conditionally fetches all pages or single page based on parameters
  - Error handling with formatted error output using Rich

### Command Patterns
Each command module follows a similar pattern:
1. Creates a Typer app instance
2. Defines command-specific option classes (following `CommandOptions` pattern in `command_options.py`)
3. Implements command functions decorated with `@app.command()`
4. Commands receive `ctx: typer.Context` to access the shared `CortexClient` via `ctx.obj["client"]`
5. Uses utility functions from `utils.py` for output formatting

### Common Options Classes
- **`ListCommandOptions`** (`command_options.py`): Standard options for list commands
  - `--table`, `--csv`: Output format options
  - `--columns, -C`: Select specific columns for table/csv output
  - `--filter, -F`: Filter rows using JSONPath and regex
  - `--sort, -S`: Sort rows by JSONPath fields
  - `--page, -p`, `--page-size, -z`: Pagination controls

- **`CommandOptions`**: Base options (e.g., `--print` for internal testing)

### Output Handling
- Default: JSON output via Rich's `print_json()`
- Table/CSV output: Configurable via `--table` or `--csv` flags with column selection
- Output utilities in `utils.py`:
  - `print_output()`: JSON output
  - `print_output_with_context()`: Formatted output with table/csv support
  - `guess_data_key()`: Infers the data key in paginated responses

### Testing
- **Test framework**: pytest with pytest-cov for coverage
- **Test utilities**: `tests/helpers/utils.py` provides a `cli()` helper that wraps the Typer CLI runner
- **Test data setup**: Tests depend on `test_import.py` running first to load test entities
- Tests use the real Cortex API (not mocked) and require valid `CORTEX_API_KEY`
- Parallel execution: Tests run with `pytest-xdist` (`-n auto`) for speed
- Serial marker: Use `@pytest.mark.serial` for tests that must run sequentially

## Command Naming Style Guide

Follow the conventions in `STYLE.md`:
- **Flags over arguments**: Use named flags for clarity and future compatibility
- **Long and short versions**: All flags should have both (e.g., `--long-version, -l`)
- **Consistent short flags**: Reuse short flags across commands where possible
- **Kebab-case**: Multi-word flags use kebab-case (e.g., `--api-key`)

### Standard Verbs
- **list**: Paginated list of resources (fetch all pages by default)
- **get**: Retrieve full details of a single object
- **create**: Create new object (fails if exists, unless `--replace-existing` or `--update-existing`)
- **delete**: Delete object (interactive prompt unless `--force`)
- **update**: Modify existing object (accepts full or partial definitions)
- **archive/unarchive**: Archive operations
- **add/remove**: Add/remove items from list attributes
- **set/unset**: Set/unset single-value attributes
- **open**: Open resource in browser

## Build & Release Process

### Release Workflow
1. Create feature branch for changes
2. Merge to `staging` branch for testing
3. Merge `staging` to `main` to trigger release
4. Version bumping:
   - Default: Patch version bump
   - `#minor` in commit message: Minor version bump
   - `#major` in commit message: Major version bump
5. Release publishes to:
   - PyPI
   - Docker Hub (`cortexapp/cli:VERSION` and `cortexapp/cli:latest`)
   - Homebrew tap (`cortexapps/homebrew-tap`)

### Commit Message Format
Commits should be prefixed with:
- `add`: New features
- `fix`: Bug fixes
- `change`: Changes to existing features
- `remove`: Removing features

Only commits with these prefixes appear in the auto-generated `HISTORY.md`.

### HISTORY.md Merge Conflicts
The `HISTORY.md` file is auto-generated when `staging` is merged to `main`. This means:
- `main` always has the latest HISTORY.md
- `staging` lags behind until the next release
- Feature branches created from `main` have the updated history

When merging feature branches to `staging`, conflicts in HISTORY.md are expected. Resolve by accepting the incoming version:
```bash
git checkout --theirs HISTORY.md
git add HISTORY.md
```

### GitHub Actions
- **`publish.yml`**: Triggered on push to `main`, handles versioning and multi-platform publishing
- **`test-pr.yml`**: Runs tests on pull requests

## Key Files

- `cli.py`: Main CLI entry point and global callback
- `cortex_client.py`: HTTP client for Cortex API
- `command_options.py`: Reusable command option definitions
- `utils.py`: Output formatting utilities
- `commands/*.py`: Individual command implementations
- `pyproject.toml`: Poetry configuration and dependencies
- `Justfile`: Task automation recipes
- `DEVELOPER.md`: Developer-specific testing and workflow notes
- `STYLE.md`: Command design guidelines
