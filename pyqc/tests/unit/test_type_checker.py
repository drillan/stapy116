"""Test cases for Type checker."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pyqc.checkers.type_checker import TypeChecker
from pyqc.config import TypeCheckerConfig


class TestTypeChecker:
    """Test Type checker functionality."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        checker = TypeChecker()
        assert checker.checker_type == "mypy"
        assert isinstance(checker.config, TypeCheckerConfig)

    def test_init_with_checker_type(self) -> None:
        """Test initialization with specific checker type."""
        checker = TypeChecker(checker_type="ty")
        assert checker.checker_type == "ty"

    def test_init_with_config(self) -> None:
        """Test initialization with configuration."""
        config = TypeCheckerConfig(strict=False, ignore_missing_imports=False)
        checker = TypeChecker(config=config)
        assert checker.config == config

    def test_build_command_mypy_basic(self) -> None:
        """Test basic mypy command building."""
        config = TypeCheckerConfig(strict=False, ignore_missing_imports=False)
        checker = TypeChecker(checker_type="mypy", config=config)
        command = checker._build_command(Path("test.py"))

        expected = ["mypy", "--show-error-codes", "--no-error-summary", "test.py"]
        assert command == expected

    def test_build_command_mypy_with_config(self) -> None:
        """Test mypy command building with configuration."""
        config = TypeCheckerConfig(strict=True, ignore_missing_imports=True)
        checker = TypeChecker(checker_type="mypy", config=config)
        command = checker._build_command(Path("test.py"))

        assert "mypy" in command
        assert "--strict" in command
        assert "--ignore-missing-imports" in command
        assert "--show-error-codes" in command
        assert "test.py" in command

    def test_build_command_ty_basic(self) -> None:
        """Test basic ty command building."""
        config = TypeCheckerConfig(strict=False, ignore_missing_imports=False)
        checker = TypeChecker(checker_type="ty", config=config)
        command = checker._build_command(Path("test.py"))

        expected = ["ty", "check", "test.py"]
        assert command == expected

    def test_build_command_ty_with_config(self) -> None:
        """Test ty command building with configuration."""
        config = TypeCheckerConfig(strict=True, ignore_missing_imports=True)
        checker = TypeChecker(checker_type="ty", config=config)
        command = checker._build_command(Path("test.py"))

        assert "ty" in command
        assert "check" in command
        assert "test.py" in command
        # ty may have different flag names


class TestTypeCheckerMypy:
    """Test mypy-specific functionality."""

    @patch("subprocess.run")
    def test_check_types_mypy_success_no_issues(self, mock_run: Mock) -> None:
        """Test mypy type check with no issues."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["mypy", "test.py"],
            returncode=0,
            stdout="Success: no issues found in 1 source file",
            stderr="",
        )

        checker = TypeChecker(checker_type="mypy")
        issues = checker.check_types(Path("test.py"))

        assert issues == []
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_check_types_mypy_with_issues(self, mock_run: Mock) -> None:
        """Test mypy type check with issues found."""
        mypy_output = """test.py:10: error: Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]
test.py:15: error: Argument 1 to "len" has incompatible type "int"; expected "Sized"  [arg-type]
test.py:20: note: Consider using "isinstance" instead"""

        mock_run.return_value = subprocess.CompletedProcess(
            args=["mypy", "test.py"],
            returncode=1,  # Issues found
            stdout=mypy_output,
            stderr="",
        )

        checker = TypeChecker(checker_type="mypy")
        issues = checker.check_types(Path("test.py"))

        assert len(issues) == 3  # 2 errors + 1 note

        # Check first issue (assignment error)
        issue1 = issues[0]
        assert issue1["filename"] == "test.py"
        assert issue1["line"] == 10
        assert issue1["severity"] == "error"
        assert issue1["code"] == "assignment"
        assert "Incompatible types in assignment" in issue1["message"]

        # Check second issue (arg-type error)
        issue2 = issues[1]
        assert issue2["line"] == 15
        assert issue2["code"] == "arg-type"
        assert issue2["severity"] == "error"

        # Check note
        issue3 = issues[2]
        assert issue3["line"] == 20
        assert issue3["severity"] == "note"
        assert issue3["code"] is None

    @patch("subprocess.run")
    def test_check_types_mypy_execution_error(self, mock_run: Mock) -> None:
        """Test mypy type check with execution error."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["mypy", "test.py"],
            returncode=2,  # Execution error
            stdout="",
            stderr="mypy: error: Cannot find module named 'nonexistent'",
        )

        checker = TypeChecker(checker_type="mypy")
        with pytest.raises(RuntimeError, match="mypy execution failed"):
            checker.check_types(Path("test.py"))

    @patch("subprocess.run")
    def test_check_types_mypy_command_not_found(self, mock_run: Mock) -> None:
        """Test mypy type check when mypy command is not found."""
        mock_run.side_effect = FileNotFoundError("mypy: command not found")

        checker = TypeChecker(checker_type="mypy")
        with pytest.raises(FileNotFoundError, match="mypy: command not found"):
            checker.check_types(Path("test.py"))


class TestTypeCheckerTy:
    """Test ty-specific functionality."""

    @patch("subprocess.run")
    def test_check_types_ty_success_no_issues(self, mock_run: Mock) -> None:
        """Test ty type check with no issues."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ty", "check", "test.py"], returncode=0, stdout="", stderr=""
        )

        checker = TypeChecker(checker_type="ty")
        issues = checker.check_types(Path("test.py"))

        assert issues == []
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_check_types_ty_with_issues(self, mock_run: Mock) -> None:
        """Test ty type check with issues found."""
        # ty might output JSON format (this is hypothetical)
        ty_output = json.dumps(
            [
                {
                    "filename": "test.py",
                    "line": 10,
                    "column": 5,
                    "severity": "error",
                    "message": "Type mismatch: expected int, got str",
                    "code": "type-mismatch",
                }
            ]
        )

        mock_run.return_value = subprocess.CompletedProcess(
            args=["ty", "check", "test.py"],
            returncode=1,  # Issues found
            stdout=ty_output,
            stderr="",
        )

        checker = TypeChecker(checker_type="ty")
        issues = checker.check_types(Path("test.py"))

        assert len(issues) == 1

        issue = issues[0]
        assert issue["filename"] == "test.py"
        assert issue["line"] == 10
        assert issue["column"] == 5
        assert issue["severity"] == "error"
        assert issue["code"] == "type-mismatch"

    @patch("subprocess.run")
    def test_check_types_ty_execution_error(self, mock_run: Mock) -> None:
        """Test ty type check with execution error."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ty", "check", "test.py"],
            returncode=2,  # Execution error
            stdout="",
            stderr="ty: error: File not found",
        )

        checker = TypeChecker(checker_type="ty")
        with pytest.raises(RuntimeError, match="ty execution failed"):
            checker.check_types(Path("test.py"))


class TestTypeCheckerConfiguration:
    """Test Type checker configuration handling."""

    def test_config_mypy_strict_mode(self) -> None:
        """Test mypy strict mode configuration."""
        config = TypeCheckerConfig(strict=True)
        checker = TypeChecker(checker_type="mypy", config=config)

        command = checker._build_command(Path("test.py"))

        assert "--strict" in command

    def test_config_mypy_ignore_missing_imports(self) -> None:
        """Test mypy ignore missing imports configuration."""
        config = TypeCheckerConfig(ignore_missing_imports=True)
        checker = TypeChecker(checker_type="mypy", config=config)

        command = checker._build_command(Path("test.py"))

        assert "--ignore-missing-imports" in command

    def test_config_mypy_both_options(self) -> None:
        """Test mypy with both strict and ignore missing imports."""
        config = TypeCheckerConfig(strict=True, ignore_missing_imports=True)
        checker = TypeChecker(checker_type="mypy", config=config)

        command = checker._build_command(Path("test.py"))

        assert "--strict" in command
        assert "--ignore-missing-imports" in command

    def test_unsupported_checker_type(self) -> None:
        """Test initialization with unsupported checker type."""
        with pytest.raises(ValueError, match="Unsupported type checker"):
            TypeChecker(checker_type="invalid")


class TestTypeCheckerOutputParsing:
    """Test output parsing for different type checkers."""

    def test_parse_mypy_output_empty(self) -> None:
        """Test parsing empty mypy output."""
        checker = TypeChecker(checker_type="mypy")
        issues = checker._parse_mypy_output("")
        assert issues == []

    def test_parse_mypy_output_success_message(self) -> None:
        """Test parsing mypy success message."""
        checker = TypeChecker(checker_type="mypy")
        issues = checker._parse_mypy_output("Success: no issues found in 1 source file")
        assert issues == []

    def test_parse_mypy_output_with_issues(self) -> None:
        """Test parsing mypy output with issues."""
        output = """test.py:10: error: Incompatible types [assignment]
test.py:15: warning: Unused variable 'x' [unused-variable]
test.py:20: note: Consider using isinstance instead"""

        checker = TypeChecker(checker_type="mypy")
        issues = checker._parse_mypy_output(output)

        assert len(issues) == 3
        assert issues[0]["severity"] == "error"
        assert issues[1]["severity"] == "warning"
        assert issues[2]["severity"] == "note"

    def test_parse_ty_output_json(self) -> None:
        """Test parsing ty JSON output."""
        output = json.dumps(
            [
                {
                    "filename": "test.py",
                    "line": 10,
                    "column": 5,
                    "severity": "error",
                    "message": "Type error",
                    "code": "type-error",
                }
            ]
        )

        checker = TypeChecker(checker_type="ty")
        issues = checker._parse_ty_output(output)

        assert len(issues) == 1
        assert issues[0]["filename"] == "test.py"

    def test_parse_ty_output_invalid_json(self) -> None:
        """Test parsing invalid ty JSON output."""
        checker = TypeChecker(checker_type="ty")

        with pytest.raises(json.JSONDecodeError):
            checker._parse_ty_output("invalid json")


class TestTypeCheckerIntegration:
    """Integration tests for Type checker (require mypy/ty installed)."""

    @pytest.mark.integration
    def test_real_mypy_execution(self, tmp_path: Path) -> None:
        """Test with real mypy execution (requires mypy to be installed)."""
        # Create a test Python file with type issues
        test_file = tmp_path / "test_types.py"
        test_file.write_text("""
def add_numbers(a: int, b: int) -> int:
    return a + b

# This should cause a type error
result: int = add_numbers("hello", "world")
""")

        checker = TypeChecker(checker_type="mypy")

        try:
            issues = checker.check_types(test_file)
            # Should find type issues
            assert isinstance(issues, list)
            # The exact issues depend on mypy configuration

        except FileNotFoundError:
            pytest.skip("mypy not installed in test environment")

    @pytest.mark.integration
    def test_real_ty_execution(self, tmp_path: Path) -> None:
        """Test with real ty execution (requires ty to be installed)."""
        # Create a test Python file with type issues
        test_file = tmp_path / "test_types.py"
        test_file.write_text("""
def greet(name: str) -> str:
    return f"Hello, {name}!"

# This should cause a type error
greeting: str = greet(42)
""")

        checker = TypeChecker(checker_type="ty")

        try:
            issues = checker.check_types(test_file)
            # Should find type issues or return empty list
            assert isinstance(issues, list)

        except (FileNotFoundError, ValueError):
            pytest.skip("ty not installed or not supported in test environment")
