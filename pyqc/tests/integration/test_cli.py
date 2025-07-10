"""Integration tests for CLI commands."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from pyqc.cli import app


@pytest.fixture
def runner() -> CliRunner:
    """CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_python_file(tmp_path: Path) -> Path:
    """Create a sample Python file for testing."""
    file_path = tmp_path / "sample.py"
    file_path.write_text("""
def hello(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(hello("World"))
""")
    return file_path


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """Create a sample project structure."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    # Create sample Python files
    (project_dir / "main.py").write_text("""
import os
def main():
    print("Hello, World!")
""")

    (project_dir / "utils.py").write_text("""
def utility_func(x: int) -> int:
    return x * 2
""")

    return project_dir


class TestCheckCommand:
    """Test the check command."""

    @patch("subprocess.run")
    def test_check_single_file_success(
        self, mock_run: Mock, runner: CliRunner, sample_python_file: Path
    ) -> None:
        """Test checking a single file with no issues."""
        # Mock ruff check (no issues)
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check"], returncode=0, stdout="", stderr=""
        )

        result = runner.invoke(app, ["check", str(sample_python_file)])

        assert result.exit_code == 0
        assert "Checking 1 Python file(s)" in result.stdout
        assert "Total issues: 0" in result.stdout

    @patch("subprocess.run")
    def test_check_single_file_with_issues(
        self, mock_run: Mock, runner: CliRunner, sample_python_file: Path
    ) -> None:
        """Test checking a file with issues."""
        # Mock ruff check (with issues)
        ruff_output = [
            {
                "filename": str(sample_python_file),
                "line": 1,
                "column": 1,
                "message": "Line too long",
                "code": "E501",
                "severity": "error",
            }
        ]

        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check"],
            returncode=1,
            stdout=json.dumps(ruff_output),
            stderr="",
        )

        result = runner.invoke(app, ["check", str(sample_python_file)])

        assert result.exit_code == 1  # Issues found
        assert "Checking 1 Python file(s)" in result.stdout
        assert "Line too long" in result.stdout

    @patch("subprocess.run")
    def test_check_directory(
        self, mock_run: Mock, runner: CliRunner, sample_project: Path
    ) -> None:
        """Test checking a directory."""
        # Mock ruff check (no issues)
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check"], returncode=0, stdout="", stderr=""
        )

        result = runner.invoke(app, ["check", str(sample_project)])

        assert result.exit_code == 0
        assert "Checking 2 Python file(s)" in result.stdout

    def test_check_nonexistent_path(self, runner: CliRunner) -> None:
        """Test checking a non-existent path."""
        result = runner.invoke(app, ["check", "/nonexistent/path"])

        assert result.exit_code == 1
        assert "does not exist" in result.stdout

    @patch("subprocess.run")
    def test_check_json_output(
        self, mock_run: Mock, runner: CliRunner, sample_python_file: Path
    ) -> None:
        """Test JSON output format."""
        # Mock ruff check (no issues)
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check"], returncode=0, stdout="", stderr=""
        )

        result = runner.invoke(
            app, ["check", str(sample_python_file), "--output", "json"]
        )

        assert result.exit_code == 0
        # Should contain JSON output
        assert "{" in result.stdout
        assert "}" in result.stdout

    @patch("subprocess.run")
    def test_check_github_output(
        self, mock_run: Mock, runner: CliRunner, sample_python_file: Path
    ) -> None:
        """Test GitHub Actions output format."""
        # Mock ruff check (with issues)
        ruff_output = [
            {
                "filename": str(sample_python_file),
                "line": 1,
                "column": 1,
                "message": "Line too long",
                "code": "E501",
                "severity": "error",
            }
        ]

        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check"],
            returncode=1,
            stdout=json.dumps(ruff_output),
            stderr="",
        )

        result = runner.invoke(
            app, ["check", str(sample_python_file), "--output", "github"]
        )

        assert result.exit_code == 1
        assert "::error" in result.stdout


class TestFixCommand:
    """Test the fix command."""

    @patch("subprocess.run")
    def test_fix_single_file(
        self, mock_run: Mock, runner: CliRunner, sample_python_file: Path
    ) -> None:
        """Test fixing a single file."""
        # Mock ruff format (successful fix)
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "format"], returncode=0, stdout="", stderr=""
        )

        result = runner.invoke(app, ["fix", str(sample_python_file)])

        assert result.exit_code == 0
        assert "Fixing 1 Python file(s)" in result.stdout

    @patch("subprocess.run")
    def test_fix_dry_run(
        self, mock_run: Mock, runner: CliRunner, sample_python_file: Path
    ) -> None:
        """Test dry run mode."""
        # Mock ruff format (successful fix)
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "format"], returncode=0, stdout="", stderr=""
        )

        result = runner.invoke(app, ["fix", str(sample_python_file), "--dry-run"])

        assert result.exit_code == 0
        assert "Would fix 1 Python file(s)" in result.stdout

    def test_fix_nonexistent_path(self, runner: CliRunner) -> None:
        """Test fixing a non-existent path."""
        result = runner.invoke(app, ["fix", "/nonexistent/path"])

        assert result.exit_code == 1
        assert "does not exist" in result.stdout


class TestConfigCommand:
    """Test the config command."""

    def test_config_show_default(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test showing default configuration."""
        # Change to tmp directory to avoid loading existing config
        import os

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["config", "show"])

            assert result.exit_code == 0
            assert "PyQC Configuration" in result.stdout
            assert "Line Length" in result.stdout
            assert "Type Checker" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_config_init(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test initializing configuration."""
        import os

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["config", "init"])

            assert result.exit_code == 0
            assert "Creating configuration file" in result.stdout
            assert (tmp_path / "pyproject.toml").exists()
        finally:
            os.chdir(original_cwd)

    def test_config_invalid_action(self, runner: CliRunner) -> None:
        """Test invalid config action."""
        result = runner.invoke(app, ["config", "invalid"])

        assert result.exit_code == 1
        assert "Unknown action" in result.stdout


class TestInitCommand:
    """Test the init command."""

    def test_init_basic(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test basic initialization."""
        import os

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["init"])

            assert result.exit_code == 0
            assert "Initializing PyQC" in result.stdout
            assert "initialization completed" in result.stdout
            assert (tmp_path / "pyproject.toml").exists()
        finally:
            os.chdir(original_cwd)

    def test_init_with_pre_commit(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test initialization with pre-commit hooks."""
        import os

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["init", "--with-pre-commit"])

            assert result.exit_code == 0
            assert "Generating pre-commit configuration" in result.stdout
            assert (tmp_path / ".pre-commit-config.yaml").exists()
        finally:
            os.chdir(original_cwd)

    def test_init_with_hooks(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test initialization with Claude Code hooks."""
        import os

        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            result = runner.invoke(app, ["init", "--with-hooks"])

            assert result.exit_code == 0
            assert "Generating Claude Code hooks configuration" in result.stdout
            assert (tmp_path / ".claude" / "hooks.json").exists()
        finally:
            os.chdir(original_cwd)


class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_help_command(self, runner: CliRunner) -> None:
        """Test help command."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Python Quality Checker" in result.stdout
        assert "check" in result.stdout
        assert "fix" in result.stdout
        assert "config" in result.stdout
        assert "init" in result.stdout

    def test_check_help(self, runner: CliRunner) -> None:
        """Test check command help."""
        result = runner.invoke(app, ["check", "--help"])

        assert result.exit_code == 0
        assert "Run quality checks" in result.stdout
        assert "--output" in result.stdout
        assert "--lint" in result.stdout

    def test_fix_help(self, runner: CliRunner) -> None:
        """Test fix command help."""
        result = runner.invoke(app, ["fix", "--help"])

        assert result.exit_code == 0
        assert "Automatically fix" in result.stdout
        assert "--dry-run" in result.stdout
        assert "--backup" in result.stdout
