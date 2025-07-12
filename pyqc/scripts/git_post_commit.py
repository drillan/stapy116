#!/usr/bin/env python3
"""Git post-commit hook script for PyQC.

This script runs after Git commits to record statistics,
log commit information, and provide feedback.
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
    from pyqc.utils.logger import setup_logger

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


def get_latest_commit_info() -> dict[str, str]:
    """Get information about the latest commit.

    Returns:
        Dictionary with commit information
    """
    try:
        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        commit_hash = (
            hash_result.stdout.strip() if hash_result.returncode == 0 else "unknown"
        )

        # Get commit message
        message_result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        commit_message = (
            message_result.stdout.strip()
            if message_result.returncode == 0
            else "unknown"
        )

        # Get author
        author_result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%an"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        author = (
            author_result.stdout.strip() if author_result.returncode == 0 else "unknown"
        )

        # Get changed files count
        files_result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        changed_files = (
            len(files_result.stdout.strip().split("\n"))
            if files_result.returncode == 0 and files_result.stdout.strip()
            else 0
        )

        return {
            "hash": commit_hash[:8],  # Short hash
            "message": commit_message,
            "author": author,
            "changed_files": str(changed_files),
        }

    except Exception as e:
        return {
            "hash": "unknown",
            "message": "unknown",
            "author": "unknown",
            "changed_files": "0",
            "error": str(e),
        }


def run_quick_quality_check() -> tuple[bool, str]:
    """Run a quick quality check on changed files only.

    Returns:
        Tuple of (success, summary)
    """
    project_dir = Path(__file__).parent.parent
    original_cwd = os.getcwd()

    try:
        os.chdir(project_dir)

        # Get list of changed files in the last commit
        files_result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if files_result.returncode != 0 or not files_result.stdout.strip():
            return True, "No files changed"

        changed_files = [
            f for f in files_result.stdout.strip().split("\n") if f.endswith(".py")
        ]

        if not changed_files:
            return True, "No Python files changed"

        # Run PyQC on changed files only
        command = ["uv", "run", "pyqc", "check"] + changed_files + ["--output", "text"]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=15,  # 15 second timeout
        )

        success = result.returncode == 0

        if success:
            return (
                True,
                f"✅ Quality check passed for {len(changed_files)} Python files",
            )
        else:
            # Count issues from output
            issues_count = result.stdout.count("issues found:") if result.stdout else 0
            return (
                False,
                f"⚠️ {issues_count} quality issues found in {len(changed_files)} files",
            )

    except subprocess.TimeoutExpired:
        return False, "Quality check timed out"
    except Exception as e:
        return False, f"Quality check error: {str(e)}"
    finally:
        os.chdir(original_cwd)


def log_commit_statistics(
    commit_info: dict[str, str], quality_result: tuple[bool, str]
) -> None:
    """Log commit statistics for tracking.

    Args:
        commit_info: Commit information dictionary
        quality_result: Quality check result tuple
    """
    logger = get_git_hooks_logger()

    quality_success, quality_summary = quality_result

    # Log commit information
    logger.info("📊 POST-COMMIT STATISTICS")
    logger.info(f"🔹 Commit Hash: {commit_info['hash']}")
    logger.info(f"🔹 Message: {commit_info['message']}")
    logger.info(f"🔹 Author: {commit_info['author']}")
    logger.info(f"🔹 Changed Files: {commit_info['changed_files']}")
    logger.info(f"🔹 Quality Check: {quality_summary}")

    # Log in structured format for potential analysis
    logger.info(
        f"COMMIT_STATS | {commit_info['hash']} | "
        f"{commit_info['changed_files']} files | "
        f"Quality: {'PASS' if quality_success else 'ISSUES'}"
    )


def main() -> int:
    """Main function for Git post-commit hook.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger = get_git_hooks_logger()

    # Log startup information
    project_dir = Path(__file__).parent.parent
    logger.info("🔧 Git post-commit hook starting...")
    logger.info(f"📁 Project directory: {project_dir}")

    start_time = time.time()

    try:
        # Get commit information
        logger.info("📝 Gathering commit information...")
        commit_info = get_latest_commit_info()

        # Run quick quality check
        logger.info("🔍 Running post-commit quality check...")
        quality_result = run_quick_quality_check()

        # Log statistics
        log_commit_statistics(commit_info, quality_result)

        # Calculate execution time
        execution_time = time.time() - start_time

        # Display summary
        quality_success, quality_summary = quality_result
        logger.info(f"🎯 Post-commit processing completed ({execution_time:.2f}s)")
        logger.info(f"📋 Commit {commit_info['hash']}: {commit_info['message']}")
        logger.info(quality_summary)

        if not quality_success:
            logger.warning(
                "⚠️ Quality issues detected - consider running 'uv run pyqc fix .' to auto-fix"
            )

        return 0

    except Exception as e:
        logger.error(f"💥 Unexpected error in post-commit hook: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
