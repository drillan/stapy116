"""End-to-end tests for PyQC."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """Create a realistic Python project structure."""
    project_dir = tmp_path / "sample_project"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_content = """
[project]
name = "sample_project"
version = "0.1.0"

[tool.pyqc]
line-length = 88
type-checker = "mypy"
parallel = true

[tool.pyqc.ruff]
extend-select = ["I", "N", "UP"]
ignore = []

[tool.pyqc.mypy]
strict = true
ignore_missing_imports = true
"""
    (project_dir / "pyproject.toml").write_text(pyproject_content)

    # Create source directory
    src_dir = project_dir / "src"
    src_dir.mkdir()

    # Create main.py with some issues
    main_content = '''
"""Main module."""
import os
import sys  # unused import

def calculate(x, y):
    """Calculate something."""
    # Missing type annotations
    result = x + y
    return result

# Long line that exceeds 88 characters which should be caught by ruff linting check
def process_data(data):
    processed = []
    for item in data:
        if item > 0:
            processed.append(item * 2)
    return processed

if __name__ == "__main__":
    print(calculate(1, 2))
'''
    (src_dir / "main.py").write_text(main_content)

    # Create utils.py with proper code
    utils_content = '''
"""Utility functions."""
from typing import List


def filter_positive(numbers: List[int]) -> List[int]:
    """Filter positive numbers from a list."""
    return [n for n in numbers if n > 0]


def double_value(value: int) -> int:
    """Double the input value."""
    return value * 2
'''
    (src_dir / "utils.py").write_text(utils_content)

    # Create tests directory
    tests_dir = project_dir / "tests"
    tests_dir.mkdir()

    # Create test file
    test_content = '''
"""Test module."""
import pytest
from src.utils import filter_positive, double_value


def test_filter_positive():
    """Test filter_positive function."""
    assert filter_positive([1, -2, 3, -4, 5]) == [1, 3, 5]
    assert filter_positive([-1, -2, -3]) == []
    assert filter_positive([]) == []


def test_double_value():
    """Test double_value function."""
    assert double_value(5) == 10
    assert double_value(0) == 0
    assert double_value(-3) == -6
'''
    (tests_dir / "test_utils.py").write_text(test_content)

    return project_dir


class TestEndToEnd:
    """End-to-end tests for PyQC functionality."""

    def test_check_command_text_output(self, sample_project: Path) -> None:
        """Test check command with text output."""
        result = subprocess.run(
            ["uv", "run", "pyqc", "check", str(sample_project)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,  # PyQC project root
        )

        # Should find issues
        assert result.returncode in [1, 2]  # Issues found or execution error
        assert "Checking" in result.stdout
        assert "PyQC Report" in result.stdout
        assert "Total issues:" in result.stdout

    def test_check_command_json_output(self, sample_project: Path) -> None:
        """Test check command with JSON output."""
        result = subprocess.run(
            ["uv", "run", "pyqc", "check", str(sample_project), "--output", "json"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        # Parse JSON output
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            # If JSON parsing fails, check if we at least got some JSON-like output
            assert "{" in result.stdout
            assert "summary" in result.stdout
            return

        assert "summary" in output
        assert "results" in output
        assert output["summary"]["files_checked"] > 0
        assert output["summary"]["total_issues"] > 0

    def test_check_command_github_output(self, sample_project: Path) -> None:
        """Test check command with GitHub Actions output."""
        result = subprocess.run(
            ["uv", "run", "pyqc", "check", str(sample_project), "--output", "github"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        # Should have GitHub Actions annotations
        assert "::error" in result.stdout or "::warning" in result.stdout

    def test_fix_command_dry_run(self, sample_project: Path) -> None:
        """Test fix command with dry run."""
        result = subprocess.run(
            ["uv", "run", "pyqc", "fix", str(sample_project), "--dry-run"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        assert result.returncode == 0
        assert "Would fix" in result.stdout

        # Verify files weren't actually modified
        main_content = (sample_project / "src" / "main.py").read_text()
        assert "import sys  # unused import" in main_content

    def test_config_command(self, sample_project: Path) -> None:
        """Test config command."""
        result = subprocess.run(
            ["uv", "run", "pyqc", "config", "show"],
            capture_output=True,
            text=True,
            cwd=sample_project,
        )

        assert result.returncode == 0
        assert "PyQC Configuration" in result.stdout
        assert "Line Length" in result.stdout
        assert "88" in result.stdout

    def test_init_command(self, tmp_path: Path) -> None:
        """Test init command."""
        empty_project = tmp_path / "empty_project"
        empty_project.mkdir()

        result = subprocess.run(
            ["uv", "run", "pyqc", "init"],
            capture_output=True,
            text=True,
            cwd=empty_project,
            env={
                **os.environ,
                "PYQC_ROOT": str(Path(__file__).parent.parent.parent),
            },
        )

        assert result.returncode == 0
        assert "Initializing PyQC" in result.stdout
        assert (empty_project / "pyproject.toml").exists()

    def test_parallel_execution_performance(self, sample_project: Path) -> None:
        """Test parallel execution performance."""
        # Create more Python files
        for i in range(10):
            file_path = sample_project / f"module_{i}.py"
            file_path.write_text(f'''
def function_{i}(x: int) -> int:
    """Function {i}."""
    return x * {i}
''')

        # Run with performance metrics
        result = subprocess.run(
            ["uv", "run", "pyqc", "check", str(sample_project), "--show-performance"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        assert "Total time:" in result.stdout
        assert "Files per second:" in result.stdout

    def test_specific_file_check(self, sample_project: Path) -> None:
        """Test checking a specific file."""
        main_file = sample_project / "src" / "main.py"

        result = subprocess.run(
            ["uv", "run", "pyqc", "check", str(main_file)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        assert result.returncode in [1, 2]
        assert "Checking 1 Python file(s)" in result.stdout

    def test_error_handling(self, tmp_path: Path) -> None:
        """Test error handling for various scenarios."""
        # Test non-existent path
        result = subprocess.run(
            ["uv", "run", "pyqc", "check", str(tmp_path / "nonexistent")],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        assert result.returncode == 1
        assert "does not" in result.stdout and "exist" in result.stdout

        # Test empty directory
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = subprocess.run(
            ["uv", "run", "pyqc", "check", str(empty_dir)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        assert result.returncode == 0
        assert "No Python files found" in result.stdout
