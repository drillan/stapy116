"""Core PyQC functionality - result aggregation and reporting."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pyqc.checkers.ruff_checker import RuffChecker
from pyqc.checkers.type_checker import TypeChecker
from pyqc.config import PyQCConfig


class Issue:
    """Standardized issue representation."""
    
    def __init__(
        self,
        filename: str,
        line: int,
        column: int | None,
        severity: str,
        message: str,
        code: str | None,
        checker: str,
        fixable: bool = False
    ) -> None:
        """Initialize issue."""
        self.filename = filename
        self.line = line
        self.column = column
        self.severity = severity
        self.message = message
        self.code = code
        self.checker = checker
        self.fixable = fixable
    
    def to_dict(self) -> dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            "filename": self.filename,
            "line": self.line,
            "column": self.column,
            "severity": self.severity,
            "message": self.message,
            "code": self.code,
            "checker": self.checker,
            "fixable": self.fixable
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Issue:
        """Create issue from dictionary."""
        return cls(
            filename=data["filename"],
            line=data["line"],
            column=data.get("column"),
            severity=data["severity"],
            message=data["message"],
            code=data.get("code"),
            checker=data["checker"],
            fixable=data.get("fixable", False)
        )


class CheckResult:
    """Result from running quality checks."""
    
    def __init__(self, path: Path, config: PyQCConfig) -> None:
        """Initialize check result."""
        self.path = path
        self.config = config
        self.issues: list[Issue] = []
        self.checks_run: list[str] = []
        self.execution_time: float = 0.0
        self.success = True
        self.error_message: str | None = None
    
    def add_issues(self, issues: list[dict[str, Any]], checker: str) -> None:
        """Add issues from a checker."""
        for issue_data in issues:
            # Standardize issue format
            issue = Issue(
                filename=issue_data.get("filename", str(self.path)),
                line=issue_data.get("line", 0),
                column=issue_data.get("column"),
                severity=issue_data.get("severity", "error"),
                message=issue_data.get("message", "Unknown issue"),
                code=issue_data.get("code"),
                checker=checker,
                fixable=issue_data.get("fixable", False)
            )
            self.issues.append(issue)
    
    def get_issue_count_by_severity(self) -> dict[str, int]:
        """Get count of issues by severity."""
        counts = {"error": 0, "warning": 0, "info": 0, "note": 0}
        for issue in self.issues:
            if issue.severity in counts:
                counts[issue.severity] += 1
            else:
                counts["error"] += 1  # Unknown severity treated as error
        return counts
    
    def get_fixable_issues(self) -> list[Issue]:
        """Get list of fixable issues."""
        return [issue for issue in self.issues if issue.fixable]
    
    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "path": str(self.path),
            "issues": [issue.to_dict() for issue in self.issues],
            "checks_run": self.checks_run,
            "execution_time": self.execution_time,
            "success": self.success,
            "error_message": self.error_message,
            "summary": self.get_issue_count_by_severity()
        }


class PyQCRunner:
    """Main PyQC runner that coordinates all checkers."""
    
    def __init__(self, config: PyQCConfig) -> None:
        """Initialize PyQC runner with configuration."""
        self.config = config
        self.ruff_checker = RuffChecker(config.ruff)
        self.type_checker = TypeChecker(config.type_checker, config.mypy)
    
    def check_file(self, path: Path) -> CheckResult:
        """Run all quality checks on a single file."""
        result = CheckResult(path, self.config)
        
        try:
            # Run ruff lint check
            try:
                lint_issues = self.ruff_checker.check_lint(path)
                # Mark ruff lint issues as potentially fixable
                for issue in lint_issues:
                    if issue.get("fix"):
                        issue["fixable"] = True
                result.add_issues(lint_issues, "ruff-lint")
                result.checks_run.append("ruff-lint")
            except Exception as e:
                result.success = False
                result.error_message = f"Ruff lint failed: {e}"
            
            # Run ruff format check
            try:
                format_issues = self.ruff_checker.check_format(path)
                # Mark format issues as fixable
                for issue in format_issues:
                    issue["fixable"] = True
                result.add_issues(format_issues, "ruff-format")
                result.checks_run.append("ruff-format")
            except Exception as e:
                result.success = False
                result.error_message = f"Ruff format failed: {e}"
            
            # Run type check
            try:
                type_issues = self.type_checker.check_types(path)
                result.add_issues(type_issues, "type-check")
                result.checks_run.append("type-check")
            except Exception as e:
                result.success = False
                result.error_message = f"Type check failed: {e}"
        
        except Exception as e:
            result.success = False
            result.error_message = f"Unexpected error: {e}"
        
        return result
    
    def fix_file(self, path: Path, dry_run: bool = False) -> CheckResult:
        """Run automatic fixes on a single file."""
        result = CheckResult(path, self.config)
        
        try:
            # Run ruff format fix
            try:
                fix_success = self.ruff_checker.fix_format(path, dry_run=dry_run)
                if fix_success:
                    result.checks_run.append("ruff-format-fix")
                else:
                    result.success = False
                    result.error_message = "Ruff format fix failed"
            except Exception as e:
                result.success = False
                result.error_message = f"Ruff format fix failed: {e}"
        
        except Exception as e:
            result.success = False
            result.error_message = f"Unexpected error during fix: {e}"
        
        return result


class ReportGenerator:
    """Generate reports from check results."""
    
    @staticmethod
    def generate_text_report(results: list[CheckResult]) -> str:
        """Generate human-readable text report."""
        if not results:
            return "No files checked."
        
        lines = ["PyQC Report", "=" * 50]
        
        total_files = len(results)
        total_issues = sum(len(result.issues) for result in results)
        successful_files = sum(1 for result in results if result.success)
        
        lines.append(f"Files checked: {total_files}")
        lines.append(f"Successful: {successful_files}")
        lines.append(f"Total issues: {total_issues}")
        lines.append("")
        
        # Group issues by severity
        severity_counts = {"error": 0, "warning": 0, "info": 0, "note": 0}
        for result in results:
            counts = result.get_issue_count_by_severity()
            for severity, count in counts.items():
                severity_counts[severity] += count
        
        lines.append("Issues by severity:")
        for severity, count in severity_counts.items():
            if count > 0:
                lines.append(f"  {severity}: {count}")
        lines.append("")
        
        # List all issues
        if total_issues > 0:
            lines.append("Issues found:")
            lines.append("-" * 30)
            
            for result in results:
                if result.issues:
                    for issue in result.issues:
                        location = f"{issue.filename}:{issue.line}"
                        if issue.column:
                            location += f":{issue.column}"
                        
                        checker_info = f"[{issue.checker}]"
                        if issue.code:
                            checker_info = f"[{issue.checker}:{issue.code}]"
                        
                        lines.append(f"{location}: {issue.severity}: {issue.message} {checker_info}")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_json_report(results: list[CheckResult]) -> dict[str, Any]:
        """Generate JSON report."""
        total_files = len(results)
        total_issues = sum(len(result.issues) for result in results)
        successful_files = sum(1 for result in results if result.success)
        
        # Aggregate severity counts
        severity_counts = {"error": 0, "warning": 0, "info": 0, "note": 0}
        for result in results:
            counts = result.get_issue_count_by_severity()
            for severity, count in counts.items():
                severity_counts[severity] += count
        
        return {
            "summary": {
                "files_checked": total_files,
                "successful_files": successful_files,
                "total_issues": total_issues,
                "severity_counts": severity_counts
            },
            "results": [result.to_dict() for result in results]
        }
    
    @staticmethod
    def generate_github_actions_report(results: list[CheckResult]) -> str:
        """Generate GitHub Actions annotations format."""
        lines = []
        
        for result in results:
            for issue in result.issues:
                # GitHub Actions annotation format
                # ::warning file=path,line=line,col=col::message
                annotation_type = "error" if issue.severity == "error" else "warning"
                
                location_info = f"file={issue.filename},line={issue.line}"
                if issue.column:
                    location_info += f",col={issue.column}"
                
                checker_info = f"[{issue.checker}]"
                if issue.code:
                    checker_info = f"[{issue.checker}:{issue.code}]"
                
                message = f"{issue.message} {checker_info}"
                lines.append(f"::{annotation_type} {location_info}::{message}")
        
        return "\n".join(lines)