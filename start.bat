@echo off
cd /d "%~dp0"
uv run screen-supervisor run --config config.toml
pause
