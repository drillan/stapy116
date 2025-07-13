#!/usr/bin/env python3
"""
Claude Code Hooks Integration for PyQC

統合されたClaude Code hooksハンドラー。JSON入力を処理し、PyQC品質チェックを実行します。
git_hooks_detector.pyと同様の設計パターンを採用し、シンプルで保守性の高い実装を提供します。
"""

import json
import subprocess
import sys
import time
from pathlib import Path

from pyqc.utils.logger import get_hooks_logger, log_hooks_execution, log_hooks_start


def run_pyqc_check(file_path: Path) -> tuple[bool, str, str]:
    """Run PyQC check on a single file.

    Args:
        file_path: Path to the file to check

    Returns:
        Tuple of (success, stdout, stderr)
    """
    logger = get_hooks_logger()

    try:
        # Get project root (two levels up from scripts/)
        project_dir = Path(__file__).parent.parent

        # Run PyQC check command
        cmd = ["uv", "run", "pyqc", "check", str(file_path), "--output", "github"]

        result = subprocess.run(
            cmd, cwd=project_dir, capture_output=True, text=True, timeout=30
        )

        # PyQC returns 0 for success, 1 for issues found
        success = result.returncode == 0
        return success, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        logger.error(f"PyQC check timed out for {file_path}")
        return False, "", "Command timed out after 30 seconds"
    except Exception as e:
        logger.error(f"Error running PyQC check: {e}")
        return False, "", str(e)


def check_file_accessibility(file_path: Path) -> bool:
    """Check if file exists and is a Python file.

    Args:
        file_path: Path to check

    Returns:
        True if file is accessible and is a Python file
    """
    logger = get_hooks_logger()

    if not file_path.exists():
        logger.error(f"File does not exist: {file_path}")
        return False

    if not file_path.is_file():
        logger.error(f"Path is not a file: {file_path}")
        return False

    if file_path.suffix != ".py":
        logger.info(f"Skipping non-Python file: {file_path}")
        return False

    return True


def process_file(file_path: Path) -> bool:
    """Process a single file with PyQC hooks.

    Args:
        file_path: Path to the file to process

    Returns:
        True if processing was successful
    """
    logger = get_hooks_logger()

    # Check file accessibility
    if not check_file_accessibility(file_path):
        return True  # Skip non-Python files without error

    # Prepare command for logging
    command_str = f"uv run pyqc check {file_path} --output github"

    # Log start of execution
    log_hooks_start(str(file_path), command_str)
    logger.info(f"🔍 Starting PyQC quality check for {file_path}")

    # Record start time
    start_time = time.time()

    # Run PyQC check
    success, stdout, stderr = run_pyqc_check(file_path)

    # Calculate execution time
    execution_time = time.time() - start_time

    # Combine output and error for logging
    output = stdout + stderr if stderr else stdout
    error_msg = stderr if not success else ""

    # Log execution result
    log_hooks_execution(
        file_path=str(file_path),
        command=command_str,
        success=success,
        execution_time=execution_time,
        output=output,
        error=error_msg,
    )

    # Display results
    if success:
        logger.info(
            f"✅ PyQC check completed successfully for {file_path} ({execution_time:.2f}s)"
        )
        if output.strip():
            # Show GitHub Actions format output if any
            for line in output.strip().split("\n"):
                if line.strip():
                    print(line)
    else:
        logger.warning(
            f"⚠️ PyQC check had issues for {file_path} ({execution_time:.2f}s)"
        )
        if output.strip():
            # Show GitHub Actions format output
            for line in output.strip().split("\n"):
                if line.strip():
                    print(line)
        if error_msg.strip():
            logger.error(f"Error details: {error_msg}")

    return success


def process_json_input() -> str | None:
    """Read and parse JSON input from stdin.

    Returns:
        File path if found in JSON input, None otherwise
    """
    logger = get_hooks_logger()

    try:
        # Read JSON from stdin
        hook_input = json.load(sys.stdin)

        # Extract file path from tool_input
        tool_input = hook_input.get("tool_input", {})
        file_path = tool_input.get("file_path", "")

        if not file_path:
            logger.warning("No file_path found in hook input")
            return None

        logger.info(f"📄 Extracted file path from JSON: {file_path}")
        return str(file_path)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON input: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error reading JSON input: {e}")
        return None


def main() -> int:
    """Main function for Claude Code hooks integration.

    This script reads JSON input from stdin (provided by Claude Code hooks),
    extracts the file path, and runs PyQC quality checks on the file.
    """
    logger = get_hooks_logger()

    logger.info("🚀 Claude Code hooks integration starting...")

    # Process JSON input from stdin
    file_path_str = process_json_input()

    if not file_path_str:
        logger.error("Failed to extract file path from JSON input")
        return 1

    # Convert to Path object
    file_path = Path(file_path_str)

    # Process the file
    logger.info(f"📝 Processing file: {file_path}")
    success = process_file(file_path)

    if success:
        logger.info("✅ Claude Code hooks completed successfully")
        return 0
    else:
        logger.warning("⚠️ Claude Code hooks completed with issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
