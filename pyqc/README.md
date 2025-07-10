# PyQC - Python Quality Checker

A unified tool for Python code quality checking and fixing.

## Features

- **Integrated Checking**: Combines ruff (linting/formatting) and mypy/ty (type checking)
- **Auto-fixing**: Automatically fix common code quality issues
- **Flexible Configuration**: Support for pyproject.toml and YAML configuration
- **CI/CD Integration**: GitHub Actions format output and pre-commit hooks
- **Fast Execution**: Parallel checking for better performance

## Installation

```bash
# Install with uv
uv add pyqc

# Or with pip
pip install pyqc
```

## Quick Start

```bash
# Check code quality
uv run pyqc check

# Fix auto-fixable issues
uv run pyqc fix

# Initialize in a project
uv run pyqc init --with-pre-commit --with-hooks
```

## Commands

- `pyqc check` - Run quality checks
- `pyqc fix` - Automatically fix issues
- `pyqc config` - Manage configuration
- `pyqc init` - Initialize in a project

## Configuration

PyQC can be configured via `pyproject.toml`:

```toml
[tool.pyqc]
line-length = 88
type-checker = "mypy"

[tool.pyqc.ruff]
extend-select = ["I", "N", "UP"]
ignore = ["E501"]

[tool.pyqc.mypy]
strict = true
ignore_missing_imports = true
```

## Development Status

This is an MVP implementation demonstrating the practical approach of Claude Code.

## License

MIT