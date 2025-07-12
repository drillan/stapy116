#!/usr/bin/env python3
"""Git hooks detector for Claude Code Bash tool integration.

This script detects Git commit commands executed via Bash tool
and runs appropriate pre/post commit quality checks.
Integrates with Claude Code PostToolUse hooks for Bash commands.
Testing with .claude/settings.json configuration.
"""

import json
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
    from pyqc.utils.logger import setup_logger, log_git_hooks_execution

    # Set up git hooks logger
    project_dir = Path(__file__).parent.parent
    log_dir = project_dir / ".pyqc"
    log_file = log_dir / "git_hooks.log"

    def get_git_hooks_logger() -> logging.Logger:
        logger: logging.Logger = setup_logger(
            name="pyqc.git_hooks", level="INFO", log_file=log_file, use_rich=True
        )
        return logger

except ImportError:
    # Fallback if logger is not available
    import logging

    # Set up fallback logger with file output
    project_dir = Path(__file__).parent.parent
    log_dir = project_dir / ".pyqc"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "git_hooks.log"

    # Configure fallback logger
    logger = logging.getLogger("pyqc.git_hooks.fallback")
    logger.setLevel(logging.INFO)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_format = "%(levelname)s:%(name)s:%(message)s"
    console_handler.setFormatter(logging.Formatter(console_format))
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_format = (
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s | %(pathname)s:%(lineno)d"
    )
    file_handler.setFormatter(logging.Formatter(file_format))
    logger.addHandler(file_handler)

    def get_git_hooks_logger() -> "logging.Logger":
        return logger

    def log_git_hooks_execution(
        hook_type: str,
        command: str,
        success: bool,
        execution_time: float,
        output: str = "",
        error: str = "",
        commit_hash: str = "",
    ) -> None:
        """Fallback logging function for Git hooks execution."""
        status = "SUCCESS" if success else "FAILED"
        logger.info(
            f"GIT_HOOKS | {hook_type.upper()} | {status} | "
            f"Time: {execution_time:.2f}s | Command: {command}"
        )
        if output:
            logger.debug(f"Output: {output}")
        if error:
            logger.error(f"Error: {error}")


def is_git_commit_command(command: str) -> bool:
    """Check if the command is a Git commit.

    Args:
        command: The bash command that was executed

    Returns:
        True if it's a git commit command
    """
    # Normalize command by removing extra spaces and quotes
    normalized = command.strip().replace('"', "").replace("'", "")

    # Check for git commit patterns
    git_commit_patterns = [
        "git commit",
        "git commit -m",
        "git commit --message",
        "git commit -a",
        "git commit --all",
        "git commit --amend",
    ]

    return any(normalized.startswith(pattern) for pattern in git_commit_patterns)


def run_pyqc_check() -> tuple[bool, str, str]:
    """Run PyQC check on all files.

    Returns:
        Tuple of (success, stdout, stderr)
    """
    project_dir = Path(__file__).parent.parent
    original_cwd = os.getcwd()

    try:
        os.chdir(project_dir)

        # Build the PyQC command for all files
        command = ["uv", "run", "pyqc", "check", ".", "--output", "github"]

        # Run the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=20,  # 20 second timeout for PyQC
        )

        return result.returncode == 0, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        return False, "", "PyQC check timed out after 20 seconds"
    except Exception as e:
        return False, "", f"Unexpected error in PyQC check: {str(e)}"
    finally:
        os.chdir(original_cwd)


def run_pytest_check() -> tuple[bool, str, str]:
    """Run pytest with optimized settings for pre-commit.

    Returns:
        Tuple of (success, stdout, stderr)
    """
    project_dir = Path(__file__).parent.parent
    original_cwd = os.getcwd()

    try:
        os.chdir(project_dir)

        # Build optimized pytest command for pre-commit speed
        command = [
            "uv",
            "run",
            "pytest",
            "--no-cov",  # Disable coverage for speed
            "--tb=short",  # Short traceback format
            "--maxfail=5",  # Stop after 5 failures
            "-q",  # Quiet mode
            "--disable-warnings",  # Disable warnings for speed
            "-x",  # Stop on first failure
            "-m",
            "not e2e",  # Exclude E2E tests for speed
        ]

        # Run the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=40,  # 40 second timeout for pytest
        )

        return result.returncode == 0, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        return False, "", "pytest timed out after 40 seconds"
    except Exception as e:
        return False, "", f"Unexpected error in pytest: {str(e)}"
    finally:
        os.chdir(original_cwd)


def run_pre_commit_checks() -> bool:
    """Run comprehensive pre-commit quality checks.

    Returns:
        True if all checks passed
    """
    logger = get_git_hooks_logger()

    logger.info("🛡️ Running pre-commit quality checks...")

    start_time = time.time()

    try:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = {}

        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both tasks
            future_pyqc = executor.submit(run_pyqc_check)
            future_pytest = executor.submit(run_pytest_check)

            # Map futures to check names
            future_to_check = {future_pyqc: "pyqc", future_pytest: "pytest"}

            # Process completed tasks
            for future in as_completed(future_to_check):
                check_name = future_to_check[future]
                try:
                    result = future.result()
                    results[check_name] = result

                    success, stdout, stderr = result
                    status = "✅" if success else "❌"
                    logger.info(f"{status} {check_name} check completed")

                except Exception as e:
                    logger.error(f"❌ {check_name} check failed with exception: {e}")
                    results[check_name] = (False, "", str(e))

        # Calculate execution time
        execution_time = time.time() - start_time

        # Check if all passed
        all_success = all(success for success, _, _ in results.values())

        # Display results
        for check_name, (success, stdout, stderr) in results.items():
            # Log execution
            log_git_hooks_execution(
                hook_type="pre-commit",
                command=f"pre_commit_{check_name}",
                success=success,
                execution_time=execution_time,
                output=stdout,
                error=stderr,
            )

            # Display GitHub Actions format output if any
            if stdout.strip():
                for line in stdout.strip().split("\n"):
                    if line.strip():
                        print(line)

            # Display errors
            if stderr.strip():
                logger.error(f"{check_name} error: {stderr}")

        # Log overall result
        log_git_hooks_execution(
            hook_type="pre-commit",
            command="pre_commit_overall",
            success=all_success,
            execution_time=execution_time,
        )

        if all_success:
            logger.info(f"🎉 All pre-commit checks passed! ({execution_time:.2f}s)")
            logger.info("✅ Ready to commit")
        else:
            logger.error(f"❌ Pre-commit checks failed ({execution_time:.2f}s)")
            logger.error("🚫 Commit blocked - please fix issues before committing")

            # Display summary of failed checks
            failed_checks = [
                check_name
                for check_name, (success, _, _) in results.items()
                if not success
            ]
            logger.error(f"Failed checks: {', '.join(failed_checks)}")

        return all_success

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"💥 Unexpected error in pre-commit checks: {e}")

        log_git_hooks_execution(
            hook_type="pre-commit",
            command="pre_commit_overall",
            success=False,
            execution_time=execution_time,
            error=str(e),
        )

        return False


def run_post_commit_processing() -> bool:
    """Run post-commit processing.

    Returns:
        True if processing was successful
    """
    logger = get_git_hooks_logger()
    start_time = time.time()

    try:
        # Import and run the existing post-commit script
        import subprocess

        project_dir = Path(__file__).parent.parent
        original_cwd = os.getcwd()

        try:
            os.chdir(project_dir)

            # Run the post-commit script
            result = subprocess.run(
                ["uv", "run", "python", "scripts/git_post_commit.py"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            execution_time = time.time() - start_time
            success = result.returncode == 0

            # Log the execution
            log_git_hooks_execution(
                hook_type="post-commit",
                command="git_hooks_detector_post_commit",
                success=success,
                execution_time=execution_time,
                output=result.stdout,
                error=result.stderr,
            )

            if success:
                logger.info(
                    f"✅ Post-commit processing completed ({execution_time:.2f}s)"
                )
            else:
                logger.warning(
                    f"⚠️ Post-commit processing had issues ({execution_time:.2f}s)"
                )
                if result.stderr:
                    logger.error(f"Error: {result.stderr}")

            return success

        finally:
            os.chdir(original_cwd)

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"💥 Post-commit processing failed: {e}")

        log_git_hooks_execution(
            hook_type="post-commit",
            command="git_hooks_detector_post_commit",
            success=False,
            execution_time=execution_time,
            error=str(e),
        )

        return False


def main() -> int:
    """Main function for Git hooks detector.

    Reads JSON input from stdin containing Claude Code hook information.
    Expected format for PreToolUse:
    {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "git commit -m 'message'", ...}
    }

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger = get_git_hooks_logger()

    try:
        # Read JSON input from stdin
        hook_input = json.load(sys.stdin)

        # Verify this is a PreToolUse event for Bash
        event_name = hook_input.get("hook_event_name", "")
        tool_name = hook_input.get("tool_name", "")

        if event_name != "PreToolUse" or tool_name != "Bash":
            logger.debug(
                f"Skipping non-Bash PreToolUse event: {event_name}/{tool_name}"
            )
            return 0

        # Extract command from tool_input
        tool_input = hook_input.get("tool_input", {})
        command = tool_input.get("command", "")

        if not command:
            logger.debug("No command found in hook input")
            return 0

        logger.debug(f"Git hooks detector checking command: {command}")

        # Check if this is a git commit command
        if not is_git_commit_command(command):
            logger.debug("Not a git commit command, skipping")
            return 0

        logger.info(f"🔍 Git commit detected: {command}")

        # Run pre-commit checks first
        pre_commit_success = run_pre_commit_checks()

        if not pre_commit_success:
            logger.error("🚫 Pre-commit checks failed - blocking commit")
            return 1  # Block the commit

        # Pre-commit checks passed, allow commit to proceed
        # Note: Post-commit processing will run after the actual commit
        logger.info("✅ Pre-commit checks passed - allowing commit")

        # Run post-commit processing for immediate feedback
        run_post_commit_processing()

        return 0  # Always allow commit if pre-commit passed

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON input: {e}")
        return 0  # Don't fail the hook
    except Exception as e:
        logger.error(f"Unexpected error in Git hooks detector: {e}")
        return 0  # Don't fail the hook


if __name__ == "__main__":
    sys.exit(main())
