"""Test cases for PyQC core functionality."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

from pyqc.config import PyQCConfig
from pyqc.core import CheckResult, Issue, PyQCRunner, ReportGenerator


class TestIssue:
    """Test Issue class."""

    def test_init(self) -> None:
        """Test Issue initialization."""
        issue = Issue(
            filename="test.py",
            line=10,
            column=5,
            severity="error",
            message="Test error",
            code="E123",
            checker="test-checker",
        )

        assert issue.filename == "test.py"
        assert issue.line == 10
        assert issue.column == 5
        assert issue.severity == "error"
        assert issue.message == "Test error"
        assert issue.code == "E123"
        assert issue.checker == "test-checker"
        assert issue.fixable is False

    def test_to_dict(self) -> None:
        """Test Issue to_dict conversion."""
        issue = Issue(
            filename="test.py",
            line=10,
            column=None,
            severity="warning",
            message="Test warning",
            code=None,
            checker="test-checker",
            fixable=True,
        )

        result = issue.to_dict()

        assert result == {
            "filename": "test.py",
            "line": 10,
            "column": None,
            "severity": "warning",
            "message": "Test warning",
            "code": None,
            "checker": "test-checker",
            "fixable": True,
        }

    def test_from_dict(self) -> None:
        """Test Issue from_dict creation."""
        data = {
            "filename": "test.py",
            "line": 15,
            "column": 3,
            "severity": "info",
            "message": "Test info",
            "code": "I001",
            "checker": "test-checker",
            "fixable": False,
        }

        issue = Issue.from_dict(data)

        assert issue.filename == "test.py"
        assert issue.line == 15
        assert issue.column == 3
        assert issue.severity == "info"
        assert issue.message == "Test info"
        assert issue.code == "I001"
        assert issue.checker == "test-checker"
        assert issue.fixable is False


class TestCheckResult:
    """Test CheckResult class."""

    def test_init(self) -> None:
        """Test CheckResult initialization."""
        config = PyQCConfig()
        path = Path("test.py")
        result = CheckResult(path, config)

        assert result.path == path
        assert result.config == config
        assert result.issues == []
        assert result.checks_run == []
        assert result.execution_time == 0.0
        assert result.success is True
        assert result.error_message is None

    def test_add_issues(self) -> None:
        """Test adding issues to result."""
        config = PyQCConfig()
        result = CheckResult(Path("test.py"), config)

        issues_data = [
            {
                "filename": "test.py",
                "line": 10,
                "severity": "error",
                "message": "Error 1",
                "code": "E001",
            },
            {
                "filename": "test.py",
                "line": 20,
                "severity": "warning",
                "message": "Warning 1",
                "fixable": True,
            },
        ]

        result.add_issues(issues_data, "test-checker")

        assert len(result.issues) == 2
        assert result.issues[0].line == 10
        assert result.issues[0].severity == "error"
        assert result.issues[0].checker == "test-checker"
        assert result.issues[1].fixable is True

    def test_get_issue_count_by_severity(self) -> None:
        """Test getting issue counts by severity."""
        config = PyQCConfig()
        result = CheckResult(Path("test.py"), config)

        # Add issues with different severities
        issues_data = [
            {"line": 1, "severity": "error", "message": "Error 1"},
            {"line": 2, "severity": "error", "message": "Error 2"},
            {"line": 3, "severity": "warning", "message": "Warning 1"},
            {"line": 4, "severity": "info", "message": "Info 1"},
            {"line": 5, "severity": "note", "message": "Note 1"},
        ]

        result.add_issues(issues_data, "test")
        counts = result.get_issue_count_by_severity()

        assert counts["error"] == 2
        assert counts["warning"] == 1
        assert counts["info"] == 1
        assert counts["note"] == 1

    def test_get_fixable_issues(self) -> None:
        """Test getting fixable issues."""
        config = PyQCConfig()
        result = CheckResult(Path("test.py"), config)

        issues_data = [
            {"line": 1, "severity": "error", "message": "Not fixable"},
            {"line": 2, "severity": "warning", "message": "Fixable", "fixable": True},
            {"line": 3, "severity": "info", "message": "Also fixable", "fixable": True},
        ]

        result.add_issues(issues_data, "test")
        fixable = result.get_fixable_issues()

        assert len(fixable) == 2
        assert all(issue.fixable for issue in fixable)

    def test_to_dict(self) -> None:
        """Test CheckResult to_dict conversion."""
        config = PyQCConfig()
        result = CheckResult(Path("test.py"), config)
        result.checks_run = ["ruff-lint", "type-check"]
        result.execution_time = 1.5

        issues_data = [{"line": 1, "severity": "error", "message": "Test error"}]
        result.add_issues(issues_data, "test")

        data = result.to_dict()

        assert data["path"] == "test.py"
        assert len(data["issues"]) == 1
        assert data["checks_run"] == ["ruff-lint", "type-check"]
        assert data["execution_time"] == 1.5
        assert data["success"] is True
        assert "summary" in data


class TestPyQCRunner:
    """Test PyQCRunner class."""

    def test_init(self) -> None:
        """Test PyQCRunner initialization."""
        config = PyQCConfig()
        runner = PyQCRunner(config)

        assert runner.config == config
        assert runner.ruff_checker is not None
        assert runner.type_checker is not None

    @patch("pyqc.core.RuffChecker")
    @patch("pyqc.core.TypeChecker")
    def test_check_file_success(
        self, mock_type_checker_class: Mock, mock_ruff_checker_class: Mock
    ) -> None:
        """Test successful file checking."""
        # Setup mocks
        mock_ruff = Mock()
        mock_ruff.check_lint.return_value = [
            {"line": 10, "severity": "error", "message": "Lint error", "code": "E001"}
        ]
        mock_ruff.check_format.return_value = [
            {"line": 5, "severity": "info", "message": "Format issue", "fixable": True}
        ]
        mock_ruff_checker_class.return_value = mock_ruff

        mock_type = Mock()
        mock_type.check_types.return_value = [
            {
                "line": 15,
                "severity": "error",
                "message": "Type error",
                "code": "type-error",
            }
        ]
        mock_type_checker_class.return_value = mock_type

        config = PyQCConfig()
        runner = PyQCRunner(config)
        result = runner.check_file(Path("test.py"))

        assert result.success is True
        assert len(result.issues) == 3
        assert "ruff-lint" in result.checks_run
        assert "ruff-format" in result.checks_run
        assert "type-check" in result.checks_run

    @patch("pyqc.core.RuffChecker")
    @patch("pyqc.core.TypeChecker")
    def test_check_file_with_error(
        self, mock_type_checker_class: Mock, mock_ruff_checker_class: Mock
    ) -> None:
        """Test file checking with checker error."""
        # Setup mocks
        mock_ruff = Mock()
        mock_ruff.check_lint.side_effect = RuntimeError("Ruff failed")
        mock_ruff.check_format.return_value = []
        mock_ruff_checker_class.return_value = mock_ruff

        mock_type = Mock()
        mock_type.check_types.return_value = []
        mock_type_checker_class.return_value = mock_type

        config = PyQCConfig()
        runner = PyQCRunner(config)
        result = runner.check_file(Path("test.py"))

        assert result.success is False
        assert "Ruff lint failed" in result.error_message

    @patch("pyqc.core.RuffChecker")
    def test_fix_file_success(self, mock_ruff_checker_class: Mock) -> None:
        """Test successful file fixing."""
        # Setup mock
        mock_ruff = Mock()
        mock_ruff.fix_format.return_value = True
        mock_ruff_checker_class.return_value = mock_ruff

        config = PyQCConfig()
        runner = PyQCRunner(config)
        result = runner.fix_file(Path("test.py"), dry_run=False)

        assert result.success is True
        assert "ruff-format-fix" in result.checks_run
        mock_ruff.fix_format.assert_called_once_with(Path("test.py"), dry_run=False)

    @patch("pyqc.core.RuffChecker")
    def test_fix_file_dry_run(self, mock_ruff_checker_class: Mock) -> None:
        """Test file fixing in dry run mode."""
        # Setup mock
        mock_ruff = Mock()
        mock_ruff.fix_format.return_value = True
        mock_ruff_checker_class.return_value = mock_ruff

        config = PyQCConfig()
        runner = PyQCRunner(config)
        result = runner.fix_file(Path("test.py"), dry_run=True)

        assert result.success is True
        mock_ruff.fix_format.assert_called_once_with(Path("test.py"), dry_run=True)


class TestReportGenerator:
    """Test ReportGenerator class."""

    def test_generate_text_report_empty(self) -> None:
        """Test text report generation with no results."""
        report = ReportGenerator.generate_text_report([])
        assert "No files checked" in report

    def test_generate_text_report_with_issues(self) -> None:
        """Test text report generation with issues."""
        config = PyQCConfig()
        result = CheckResult(Path("test.py"), config)

        issues_data = [
            {
                "line": 10,
                "severity": "error",
                "message": "Error message",
                "code": "E001",
            },
            {"line": 20, "severity": "warning", "message": "Warning message"},
        ]
        result.add_issues(issues_data, "test-checker")

        report = ReportGenerator.generate_text_report([result])

        assert "PyQC Report" in report
        assert "Files checked: 1" in report
        assert "Total issues: 2" in report
        assert "error: 1" in report
        assert "warning: 1" in report
        assert "test.py:10: error: Error message [test-checker:E001]" in report

    def test_generate_json_report(self) -> None:
        """Test JSON report generation."""
        config = PyQCConfig()
        result = CheckResult(Path("test.py"), config)

        issues_data = [
            {"line": 10, "severity": "error", "message": "Error message"},
            {"line": 20, "severity": "warning", "message": "Warning message"},
        ]
        result.add_issues(issues_data, "test-checker")

        report = ReportGenerator.generate_json_report([result])

        assert "summary" in report
        assert "results" in report
        assert report["summary"]["files_checked"] == 1
        assert report["summary"]["total_issues"] == 2
        assert report["summary"]["severity_counts"]["error"] == 1
        assert report["summary"]["severity_counts"]["warning"] == 1

    def test_generate_github_actions_report(self) -> None:
        """Test GitHub Actions report generation."""
        config = PyQCConfig()
        result = CheckResult(Path("test.py"), config)

        issues_data = [
            {
                "line": 10,
                "column": 5,
                "severity": "error",
                "message": "Error message",
                "code": "E001",
            },
            {"line": 20, "severity": "warning", "message": "Warning message"},
        ]
        result.add_issues(issues_data, "test-checker")

        report = ReportGenerator.generate_github_actions_report([result])

        lines = report.split("\n")
        assert len(lines) == 2
        assert (
            "::error file=test.py,line=10,col=5::Error message [test-checker:E001]"
            in lines[0]
        )
        assert (
            "::warning file=test.py,line=20::Warning message [test-checker]" in lines[1]
        )

    def test_generate_github_actions_report_empty(self) -> None:
        """Test GitHub Actions report with no issues."""
        report = ReportGenerator.generate_github_actions_report([])
        assert report == ""
