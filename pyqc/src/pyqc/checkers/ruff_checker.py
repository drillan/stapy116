"""Ruff-based code quality checker."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from pyqc.config import RuffConfig


class RuffChecker:
    """Ruff linter and formatter wrapper."""

    def __init__(self, config: RuffConfig | None = None) -> None:
        """Initialize Ruff checker with configuration."""
        self.config = config or RuffConfig()

    def _build_command(self, action: str, path: Path) -> list[str]:
        """Build ruff command with configuration options."""
        command = ["ruff", action]

        if action == "check":
            command.append("--output-format=json")

            # Add configuration options
            if self.config.line_length != 88:  # Only add if not default
                command.append(f"--line-length={self.config.line_length}")

            if self.config.extend_select:
                command.append(f"--extend-select={','.join(self.config.extend_select)}")

            if self.config.ignore:
                command.append(f"--ignore={','.join(self.config.ignore)}")

        elif action == "format":
            # Format command has different options
            if self.config.line_length != 88:
                command.append(f"--line-length={self.config.line_length}")

        command.append(str(path))
        return command

    def check_lint(self, path: Path) -> list[dict[str, Any]]:
        """Run lint checks on the given path."""
        command = self._build_command("check", path)

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,  # Don't raise exception on non-zero exit
            )
        except FileNotFoundError as e:
            raise FileNotFoundError("ruff: command not found") from e

        # ruff returns:
        # 0: No issues found
        # 1: Issues found
        # 2+: Execution error
        if result.returncode >= 2:
            raise RuntimeError(f"Ruff execution failed: {result.stderr}")

        if not result.stdout.strip():
            return []

        try:
            issues = json.loads(result.stdout)
            return issues if isinstance(issues, list) else []
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON from ruff: {result.stdout}", "", 0
            ) from e

    def check_format(self, path: Path) -> list[dict[str, Any]]:
        """Check code formatting on the given path."""
        command = self._build_command("format", path)
        command.append("--check")  # Check mode, don't modify files

        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=False
            )
        except FileNotFoundError as e:
            raise FileNotFoundError("ruff: command not found") from e

        # ruff format returns:
        # 0: No formatting needed
        # 1: Would reformat files
        # 2+: Execution error
        if result.returncode >= 2:
            raise RuntimeError(f"Ruff format execution failed: {result.stderr}")

        if result.returncode == 1:
            # Files would be reformatted
            return [
                {
                    "type": "format",
                    "message": "File would be reformatted",
                    "filename": str(path),
                    "severity": "info",
                }
            ]

        return []

    def fix_format(self, path: Path, dry_run: bool = False) -> bool:
        """Fix code formatting issues."""
        command = self._build_command("format", path)

        if dry_run:
            command.append("--check")

        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=False
            )
        except FileNotFoundError as e:
            raise FileNotFoundError("ruff: command not found") from e

        if result.returncode >= 2:
            raise RuntimeError(f"Ruff format execution failed: {result.stderr}")

        return result.returncode == 0 or (dry_run and result.returncode == 1)
