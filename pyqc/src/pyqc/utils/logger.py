"""Logging system for PyQC.

Provides structured logging for PyQC operations, especially for Claude Code hooks.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.logging import RichHandler


def setup_logger(
    name: str = "pyqc",
    level: str = "INFO",
    log_file: Path | None = None,
    use_rich: bool = True,
) -> logging.Logger:
    """Set up a logger with console and file output.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        use_rich: Whether to use rich formatting for console output

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logger.setLevel(getattr(logging, level.upper()))

    # Console handler
    if use_rich:
        rich_handler = RichHandler(
            console=Console(stderr=True), show_path=False, show_time=True, markup=True
        )
        console_format = "[bold blue]%(name)s[/bold blue] | %(message)s"
        rich_handler.setFormatter(logging.Formatter(console_format))
        logger.addHandler(rich_handler)
    else:
        stream_handler = logging.StreamHandler(sys.stderr)
        console_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        stream_handler.setFormatter(logging.Formatter(console_format))
        logger.addHandler(stream_handler)

    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s | %(pathname)s:%(lineno)d"
        file_handler.setFormatter(logging.Formatter(file_format))
        logger.addHandler(file_handler)

    return logger


def get_hooks_logger() -> logging.Logger:
    """Get a logger specifically configured for Claude Code hooks.

    Returns:
        Logger instance configured for hooks with file logging
    """
    log_dir = Path.cwd() / ".pyqc"
    log_file = log_dir / "hooks.log"

    return setup_logger(
        name="pyqc.hooks", level="INFO", log_file=log_file, use_rich=True
    )


def get_logger(name: str = "pyqc") -> logging.Logger:
    """Get a standard PyQC logger.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return setup_logger(name=name, use_rich=True)


def log_hooks_execution(
    file_path: str,
    command: str,
    success: bool,
    execution_time: float,
    output: str = "",
    error: str = "",
) -> None:
    """Log Claude Code hooks execution details.

    Args:
        file_path: Path to the file being checked
        command: Command that was executed
        success: Whether the execution was successful
        execution_time: Execution time in seconds
        output: Command output
        error: Error message if any
    """
    logger = get_hooks_logger()

    status = "SUCCESS" if success else "FAILED"

    logger.info(
        f"HOOKS EXECUTION | {status} | {file_path} | "
        f"Time: {execution_time:.2f}s | Command: {command}"
    )

    if output:
        logger.debug(f"Command output: {output}")

    if error:
        logger.error(f"Command error: {error}")


def log_hooks_start(file_path: str, command: str) -> None:
    """Log the start of a hooks execution.

    Args:
        file_path: Path to the file being checked
        command: Command being executed
    """
    logger = get_hooks_logger()
    logger.info(f"HOOKS START | {file_path} | Command: {command}")


def get_hooks_stats() -> dict[str, Any]:
    """Get statistics from hooks log file.

    Returns:
        Dictionary with hooks execution statistics
    """
    log_file = Path.cwd() / ".pyqc" / "hooks.log"

    if not log_file.exists():
        return {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "success_rate": 0.0,
            "average_execution_time": 0.0,
            "last_execution": None,
        }

    total = 0
    successful = 0
    failed = 0
    execution_times = []
    last_execution = None

    try:
        with open(log_file, encoding="utf-8") as f:
            for line in f:
                if "HOOKS EXECUTION" in line:
                    total += 1
                    if "SUCCESS" in line:
                        successful += 1
                    elif "FAILED" in line:
                        failed += 1

                    # Extract execution time
                    try:
                        time_part = line.split("Time: ")[1].split("s")[0]
                        execution_times.append(float(time_part))
                    except (IndexError, ValueError):
                        pass

                    # Extract timestamp for last execution
                    try:
                        timestamp = line.split(" | ")[0]
                        last_execution = timestamp
                    except IndexError:
                        pass
    except Exception:
        pass

    return {
        "total_executions": total,
        "successful_executions": successful,
        "failed_executions": failed,
        "success_rate": (successful / total * 100) if total > 0 else 0.0,
        "average_execution_time": sum(execution_times) / len(execution_times)
        if execution_times
        else 0.0,
        "last_execution": last_execution,
    }
