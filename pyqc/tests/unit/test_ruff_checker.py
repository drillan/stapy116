"""Test cases for Ruff checker."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pyqc.checkers.ruff_checker import RuffChecker
from pyqc.config import RuffConfig


class TestRuffChecker:
    """Test Ruff checker functionality."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        checker = RuffChecker()
        assert isinstance(checker.config, RuffConfig)
        assert checker.config.line_length == 88
        assert checker.config.extend_select == ["I", "N", "UP"]
        assert checker.config.ignore == ["E501"]

    def test_init_with_config(self) -> None:
        """Test initialization with configuration."""
        config = RuffConfig(line_length=100, extend_select=["E", "F"])
        checker = RuffChecker(config)
        assert checker.config == config

    def test_build_command_basic(self) -> None:
        """Test basic command building."""
        # Use empty config to test minimal command
        config = RuffConfig(extend_select=[], ignore=[])
        checker = RuffChecker(config)
        command = checker._build_command("check", Path("test.py"))

        expected = ["ruff", "check", "--output-format=json", "test.py"]
        assert command == expected

    def test_build_command_with_config(self) -> None:
        """Test command building with configuration."""
        config = RuffConfig(
            line_length=100, extend_select=["E", "F", "I"], ignore=["E501", "F401"]
        )
        checker = RuffChecker(config)
        command = checker._build_command("check", Path("test.py"))

        assert "ruff" in command
        assert "check" in command
        assert "--output-format=json" in command
        assert "--line-length=100" in command
        assert "--extend-select=E,F,I" in command
        assert "--ignore=E501,F401" in command
        assert "test.py" in command


class TestRuffCheckerLint:
    """Test Ruff lint functionality."""

    @patch("subprocess.run")
    def test_check_lint_success_no_issues(self, mock_run: Mock) -> None:
        """Test lint check with no issues."""
        # Mock successful ruff execution with no issues
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check"], returncode=0, stdout="[]", stderr=""
        )

        checker = RuffChecker()
        issues = checker.check_lint(Path("test.py"))

        assert issues == []
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_check_lint_with_issues(self, mock_run: Mock) -> None:
        """Test lint check with issues found."""
        # Mock ruff output with issues
        ruff_output = [
            {
                "filename": "test.py",
                "code": "E501",
                "message": "Line too long (92 > 88 characters)",
                "location": {"row": 10, "column": 1},
                "end_location": {"row": 10, "column": 93},
                "fix": None,
                "severity": "warning",
            },
            {
                "filename": "test.py",
                "code": "F401",
                "message": "'os' imported but unused",
                "location": {"row": 1, "column": 1},
                "end_location": {"row": 1, "column": 9},
                "fix": {"message": "Remove unused import", "edits": []},
                "severity": "error",
            },
        ]

        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check"],
            returncode=1,  # Issues found
            stdout=json.dumps(ruff_output),
            stderr="",
        )

        checker = RuffChecker()
        issues = checker.check_lint(Path("test.py"))

        assert len(issues) == 2

        # Check first issue (E501)
        issue1 = issues[0]
        assert issue1["code"] == "E501"
        assert issue1["message"] == "Line too long (92 > 88 characters)"
        assert issue1["filename"] == "test.py"
        assert issue1["location"]["row"] == 10
        assert issue1["severity"] == "warning"

        # Check second issue (F401)
        issue2 = issues[1]
        assert issue2["code"] == "F401"
        assert issue2["message"] == "'os' imported but unused"
        assert issue2["severity"] == "error"
        assert issue2["fix"] is not None

    @patch("subprocess.run")
    def test_check_lint_execution_error(self, mock_run: Mock) -> None:
        """Test lint check with execution error."""
        # Mock ruff execution failure
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check"],
            returncode=2,  # Execution error
            stdout="",
            stderr="ruff: error: No such file or directory",
        )

        checker = RuffChecker()
        with pytest.raises(RuntimeError, match="Ruff execution failed"):
            checker.check_lint(Path("nonexistent.py"))

    @patch("subprocess.run")
    def test_check_lint_command_not_found(self, mock_run: Mock) -> None:
        """Test lint check when ruff command is not found."""
        mock_run.side_effect = FileNotFoundError("ruff: command not found")

        checker = RuffChecker()
        with pytest.raises(FileNotFoundError, match="ruff: command not found"):
            checker.check_lint(Path("test.py"))

    @patch("subprocess.run")
    def test_check_lint_invalid_json(self, mock_run: Mock) -> None:
        """Test lint check with invalid JSON output."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check"],
            returncode=1,
            stdout="invalid json output",
            stderr="",
        )

        checker = RuffChecker()
        with pytest.raises(json.JSONDecodeError):
            checker.check_lint(Path("test.py"))


class TestRuffCheckerFormat:
    """Test Ruff formatting functionality."""

    @patch("subprocess.run")
    def test_check_format_no_issues(self, mock_run: Mock) -> None:
        """Test format check with no formatting issues."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "format", "--check"], returncode=0, stdout="", stderr=""
        )

        checker = RuffChecker()
        issues = checker.check_format(Path("test.py"))

        assert issues == []

    @patch("subprocess.run")
    def test_check_format_with_issues(self, mock_run: Mock) -> None:
        """Test format check with formatting issues."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "format", "--check"],
            returncode=1,  # Would reformat
            stdout="Would reformat: test.py",
            stderr="",
        )

        checker = RuffChecker()
        issues = checker.check_format(Path("test.py"))

        assert len(issues) == 1
        issue = issues[0]
        assert issue["type"] == "format"
        assert issue["message"] == "File would be reformatted"
        assert issue["filename"] == "test.py"

    @patch("subprocess.run")
    def test_fix_format_dry_run(self, mock_run: Mock) -> None:
        """Test format fix in dry-run mode."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "format", "--check"],
            returncode=1,
            stdout="Would reformat: test.py",
            stderr="",
        )

        checker = RuffChecker()
        result = checker.fix_format(Path("test.py"), dry_run=True)

        assert result is True
        # Should call format with --check flag in dry-run
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "--check" in args

    @patch("subprocess.run")
    def test_fix_format_actual(self, mock_run: Mock) -> None:
        """Test actual format fix."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "format"], returncode=0, stdout="", stderr=""
        )

        checker = RuffChecker()
        result = checker.fix_format(Path("test.py"), dry_run=False)

        assert result is True
        # Should call format without --check flag for actual fix
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "--check" not in args


class TestRuffCheckerConfiguration:
    """Test Ruff checker configuration handling."""

    def test_config_serialization(self) -> None:
        """Test configuration serialization for command line."""
        config = RuffConfig(
            line_length=120,
            extend_select=["E", "F", "I", "N"],
            ignore=["E501", "F401", "I001"],
        )
        checker = RuffChecker(config)

        command = checker._build_command("check", Path("test.py"))

        # Check that all configuration options are included
        command_str = " ".join(command)
        assert "--line-length=120" in command_str
        assert "--extend-select=E,F,I,N" in command_str
        assert "--ignore=E501,F401,I001" in command_str

    def test_empty_config_lists(self) -> None:
        """Test handling of empty configuration lists."""
        config = RuffConfig(extend_select=[], ignore=[])
        checker = RuffChecker(config)

        command = checker._build_command("check", Path("test.py"))
        command_str = " ".join(command)

        # Empty lists should not add options
        assert "--extend-select=" not in command_str
        assert "--ignore=" not in command_str


class TestRuffCheckerIntegration:
    """Integration tests for Ruff checker (require ruff installed)."""

    @pytest.mark.integration
    def test_real_ruff_execution(self, tmp_path: Path) -> None:
        """Test with real ruff execution (requires ruff to be installed)."""
        # Create a test Python file with known issues
        test_file = tmp_path / "test_code.py"
        test_file.write_text("""
import os
import sys

def hello(  name  ):
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(hello("World"))
""")

        checker = RuffChecker()

        try:
            issues = checker.check_lint(test_file)
            # Should find some issues (spacing, unused import, etc.)
            # The exact issues depend on ruff configuration, but there should be some
            assert isinstance(issues, list)

            # Test format check
            format_issues = checker.check_format(test_file)
            assert isinstance(format_issues, list)

        except FileNotFoundError:
            pytest.skip("ruff not installed in test environment")
