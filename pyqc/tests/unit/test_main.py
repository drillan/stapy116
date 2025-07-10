"""Tests for __main__ module."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_main_module_execution() -> None:
    """Test that python -m pyqc works correctly."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent

    # Test that the module can be executed
    result = subprocess.run(
        [sys.executable, "-m", "pyqc", "--help"],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0
    assert "Python Quality Checker" in result.stdout
    assert "check" in result.stdout
    assert "fix" in result.stdout
    assert "config" in result.stdout
    assert "init" in result.stdout


def test_main_module_invalid_command() -> None:
    """Test that invalid commands are handled correctly."""
    project_root = Path(__file__).parent.parent.parent

    result = subprocess.run(
        [sys.executable, "-m", "pyqc", "invalid-command"],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Should fail with non-zero exit code
    assert result.returncode != 0
