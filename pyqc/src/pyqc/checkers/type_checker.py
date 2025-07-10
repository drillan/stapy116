"""Type checking wrapper for mypy/ty."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from pyqc.config import TypeCheckerConfig


class TypeChecker:
    """Type checker wrapper for mypy/ty."""

    def __init__(
        self, checker_type: str = "mypy", config: TypeCheckerConfig | None = None
    ) -> None:
        """Initialize type checker with configuration."""
        if checker_type not in ("mypy", "ty"):
            raise ValueError(f"Unsupported type checker: {checker_type}")

        self.checker_type = checker_type
        self.config = config or TypeCheckerConfig()

    def _build_command(self, path: Path) -> list[str]:
        """Build type checker command with configuration options."""
        if self.checker_type == "mypy":
            command = ["mypy"]

            # Add standard mypy options for consistent output
            command.extend(["--show-error-codes", "--no-error-summary"])

            # Add configuration options
            if self.config.strict:
                command.append("--strict")

            if self.config.ignore_missing_imports:
                command.append("--ignore-missing-imports")

            command.append(str(path))

        elif self.checker_type == "ty":
            command = ["ty", "check"]

            # ty specific options would go here
            # Note: ty is less common, so options may vary

            command.append(str(path))

        return command

    def check_types(self, path: Path) -> list[dict[str, Any]]:
        """Run type checks on the given path."""
        command = self._build_command(path)

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,  # Don't raise exception on non-zero exit
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(f"{self.checker_type}: command not found") from e

        # Type checkers typically return:
        # 0: No issues found
        # 1: Type issues found
        # 2+: Execution error
        if result.returncode >= 2:
            raise RuntimeError(f"{self.checker_type} execution failed: {result.stderr}")

        if self.checker_type == "mypy":
            return self._parse_mypy_output(result.stdout)
        elif self.checker_type == "ty":
            return self._parse_ty_output(result.stdout)

        return []

    def _parse_mypy_output(self, output: str) -> list[dict[str, Any]]:
        """Parse mypy output format."""
        if not output.strip():
            return []

        # Skip success messages
        if "Success:" in output and "no issues found" in output:
            return []

        issues = []
        lines = output.strip().split("\n")

        for line in lines:
            if not line.strip():
                continue

            # Parse mypy format: filename:line: severity: message [error-code]
            # Example: test.py:10: error: Incompatible types [assignment]
            match = re.match(
                r"^(.+):(\d+):\s*(error|warning|note):\s*(.+?)(?:\s*\[([^\]]+)\])?$",
                line,
            )

            if match:
                filename, line_num, severity, message, error_code = match.groups()
                issues.append(
                    {
                        "filename": filename,
                        "line": int(line_num),
                        "column": None,  # mypy doesn't always provide column info
                        "severity": severity,
                        "message": message.strip(),
                        "code": error_code,
                        "checker": "mypy",
                    }
                )

        return issues

    def _parse_ty_output(self, output: str) -> list[dict[str, Any]]:
        """Parse ty output format."""
        if not output.strip():
            return []

        try:
            # Assume ty outputs JSON format (this is hypothetical)
            data = json.loads(output)
            if isinstance(data, list):
                # Add checker field to each issue
                for issue in data:
                    issue["checker"] = "ty"
                return data
            return []
        except json.JSONDecodeError as e:
            # If not JSON, try to parse as text format
            raise json.JSONDecodeError(f"Invalid JSON from ty: {output}", "", 0) from e
