#!/usr/bin/env python3
"""Git pre-commit hook script for PyQC.

This script runs comprehensive quality checks before Git commits,
providing pre-commit functionality through Claude Code hooks.
Supports parallel execution for optimal performance.
"""

import logging
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("pyqc.git_hooks.fallback")

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


def run_checks_parallel() -> dict[str, tuple[bool, str, str]]:
    """Run PyQC and pytest checks in parallel.

    Returns:
        Dictionary with check results
    """
    logger = get_git_hooks_logger()

    logger.info("🚀 Starting parallel quality checks...")

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

    return results


def display_results(results: dict[str, tuple[bool, str, str]]) -> bool:
    """Display results and return overall success status.

    Args:
        results: Dictionary of check results

    Returns:
        True if all checks passed
    """
    logger = get_git_hooks_logger()

    all_success = True

    for check_name, (success, stdout, stderr) in results.items():
        if not success:
            all_success = False

        # Display GitHub Actions format output if any
        if stdout.strip():
            for line in stdout.strip().split("\n"):
                if line.strip():
                    print(line)

        # Display errors
        if stderr.strip():
            logger.error(f"{check_name} error: {stderr}")

    return all_success


def main() -> int:
    """Main function for Git pre-commit hook.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger = get_git_hooks_logger()

    # Log startup information
    project_dir = Path(__file__).parent.parent
    logger.info("🔧 Git pre-commit hook starting...")
    logger.info(f"📁 Project directory: {project_dir}")
    logger.info(f"💼 Current working directory: {os.getcwd()}")

    overall_start_time = time.time()

    logger.info("🛡️ Running comprehensive quality checks before commit...")

    try:
        # Run checks in parallel
        results = run_checks_parallel()

        # Calculate overall execution time
        overall_execution_time = time.time() - overall_start_time

        # Log individual results
        for check_name, (success, stdout, stderr) in results.items():
            log_git_hooks_execution(
                hook_type="pre-commit",
                command=f"git_pre_commit_{check_name}",
                success=success,
                execution_time=overall_execution_time,  # Approximation
                output=stdout,
                error=stderr,
            )

        # Display results
        all_success = display_results(results)

        # Log overall result
        log_git_hooks_execution(
            hook_type="pre-commit",
            command="git_pre_commit_overall",
            success=all_success,
            execution_time=overall_execution_time,
        )

        if all_success:
            logger.info(
                f"🎉 All pre-commit checks passed! ({overall_execution_time:.2f}s)"
            )
            logger.info("✅ Ready to commit")
        else:
            logger.error(f"❌ Pre-commit checks failed ({overall_execution_time:.2f}s)")
            logger.error("🚫 Commit blocked - please fix issues before committing")

            # Display summary of failed checks
            failed_checks = [
                check_name
                for check_name, (success, _, _) in results.items()
                if not success
            ]
            logger.error(f"Failed checks: {', '.join(failed_checks)}")

        return 0 if all_success else 1

    except Exception as e:
        logger.error(f"💥 Unexpected error in pre-commit hook: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
