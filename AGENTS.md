# Repository Guidelines

## Project Structure & Module Organization
`src/screen_supervisor/` contains the application code: `cli.py` is the Typer entrypoint, `config.py` loads TOML and environment overrides, `capturer.py` handles screen capture, `storage.py` persists images, `scheduler.py` runs the interval loop, and `supervisor.py` ties the flow together. Keep new runtime modules under `src/screen_supervisor/`.

`tests/` mirrors the package with `test_*.py` files. `configs/config.example.toml` is the template for local setup. `captures/` holds generated archives and should be treated as runtime output, not source. `docs/` stores architecture and configuration notes. Avoid editing `src/screen_supervisor.egg-info/` by hand.

## Build, Test, and Development Commands
Use `uv` for dependency and command management:

- `uv sync` installs runtime and dev dependencies.
- `Copy-Item configs/config.example.toml config.toml` creates a local config.
- `uv run screen-supervisor run --config config.toml` starts the capture loop.
- `uv run screen-supervisor info --config config.toml` prints the active config and storage stats.
- `uv run pytest` runs the test suite.
- `uv run ruff check src tests` runs lint checks.
- `uv run ruff format src tests` formats Python files.

If `uv` is blocked in your shell, the local fallback is `.venv\Scripts\python.exe -m pytest` or `.venv\Scripts\ruff.exe check src tests`.

GitHub CLI commands (`gh ...`) require escalated permissions in this environment. When repository settings or remote metadata need to be changed through `gh`, run those commands with approval instead of the default sandbox.

## Coding Style & Naming Conventions
Follow the existing Python style: 4-space indentation, type hints on public functions, and small focused modules. Use `snake_case` for modules, functions, config keys, and tests; use `PascalCase` for classes such as `SupervisorConfig` and `StorageManager`. Prefer `pathlib.Path`, keep CLI subcommands concise, and let `ruff` own formatting.

## Testing Guidelines
Write tests with `pytest` under `tests/`, using names like `test_config.py` and `test_cleanup_old_directories`. Cover config precedence, date-based storage behavior, and CLI-facing edge cases when behavior changes. Favor `tmp_path` and deterministic timestamps over real capture output.

## Commit & Pull Request Guidelines
This checkout does not include a `.git` directory, so no local history is available to infer a strict convention. Use short, imperative commit messages with an optional prefix, for example `fix: handle invalid log level` or `docs: clarify config override order`.

Pull requests should describe the behavior change, list the commands you ran, and call out config or retention impacts. Do not include real captured images or machine-specific paths unless they are required to explain a bug.
