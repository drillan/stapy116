#!/usr/bin/env python3
"""PyQC hooks script for Claude Code integration.

This script runs PyQC quality checks with detailed logging for Claude Code hooks.
It wraps the PyQC CLI and provides comprehensive execution tracking.
"""

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from pyqc.utils.logger import log_hooks_execution, log_hooks_start, setup_logger

    # Set up hooks logger with explicit path to PyQC project directory
    project_dir = Path(__file__).parent.parent
    log_dir = project_dir / ".pyqc"
    log_file = log_dir / "hooks.log"

    def get_hooks_logger() -> logging.Logger:
        logger: logging.Logger = setup_logger(
            name="pyqc.hooks", level="INFO", log_file=log_file, use_rich=True
        )
        return logger

except ImportError:
    # Fallback if logger is not available
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("pyqc.hooks.fallback")

    def log_hooks_start(file_path: str, command: str) -> None:
        logger.info(f"HOOKS START | {file_path} | Command: {command}")

    def log_hooks_execution(
        file_path: str,
        command: str,
        success: bool,
        execution_time: float,
        output: str = "",
        error: str = "",
    ) -> None:
        status = "SUCCESS" if success else "FAILED"
        logger.info(
            f"HOOKS EXECUTION | {status} | {file_path} | Time: {execution_time:.2f}s"
        )
        if output:
            logger.debug(f"Output: {output}")
        if error:
            logger.error(f"Error: {error}")

    def get_hooks_logger() -> "logging.Logger":
        return logger


def run_pyqc_check(file_path: Path) -> tuple[bool, str, str]:
    """Run PyQC check on the specified file.

    Args:
        file_path: Path to the Python file to check

    Returns:
        Tuple of (success, stdout, stderr)
    """
    # Change to the PyQC project directory
    project_dir = Path(__file__).parent.parent
    original_cwd = os.getcwd()

    try:
        os.chdir(project_dir)

        # Build the PyQC command
        command = ["uv", "run", "pyqc", "check", str(file_path), "--output", "github"]

        # Run the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
        )

        return result.returncode == 0, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        return False, "", "Command timed out after 30 seconds"
    except Exception as e:
        return False, "", f"Unexpected error: {str(e)}"
    finally:
        os.chdir(original_cwd)


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


def main() -> int:
    """Main function for PyQC hooks script.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Initialize logger and log startup information
    logger = get_hooks_logger()

    # Debug information for troubleshooting
    project_dir = Path(__file__).parent.parent
    log_dir = project_dir / ".pyqc"
    log_file = log_dir / "hooks.log"

    logger.info("🔧 PyQC hooks script starting...")
    logger.info(f"📁 Project directory: {project_dir}")
    logger.info(f"📁 Log directory: {log_dir}")
    logger.info(f"📝 Log file: {log_file}")
    logger.info(f"💼 Current working directory: {os.getcwd()}")
    logger.info(f"🔧 Log directory exists: {log_dir.exists()}")
    logger.info(f"📝 Log file exists: {log_file.exists()}")

    if len(sys.argv) < 2:
        logger.error("Usage: pyqc_hooks.py <file_path> [file_path2 ...]")
        return 1

    # Process all provided files
    file_paths = [Path(arg) for arg in sys.argv[1:]]
    all_success = True

    logger.info(f"🚀 PyQC hooks starting - processing {len(file_paths)} file(s)")

    for file_path in file_paths:
        try:
            success = process_file(file_path)
            if not success:
                all_success = False
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {e}")
            all_success = False

    if all_success:
        logger.info("🎉 All PyQC hooks completed successfully")
    else:
        logger.warning("⚠️ Some PyQC hooks completed with issues")

    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
