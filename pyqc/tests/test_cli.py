"""Tests for CLI functionality."""

from __future__ import annotations

from typer.testing import CliRunner

from pyqc.cli import app

runner = CliRunner()


def test_cli_check_command() -> None:
    """Test the check command."""
    result = runner.invoke(app, ["check", "."])
    assert result.exit_code == 0
    assert "Checking" in result.stdout


def test_cli_fix_command() -> None:
    """Test the fix command."""
    result = runner.invoke(app, ["fix", "."])
    assert result.exit_code == 0
    assert "Fixing" in result.stdout


def test_cli_config_command() -> None:
    """Test the config command."""
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "Config" in result.stdout


def test_cli_init_command() -> None:
    """Test the init command."""
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Initializing" in result.stdout
