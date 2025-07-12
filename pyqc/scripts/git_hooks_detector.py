#!/usr/bin/env python3
"""Git hooks detector for Claude Code Bash tool integration.

This script detects Git commit commands executed via Bash tool
and runs appropriate pre/post commit quality checks.
Integrates with Claude Code PostToolUse hooks for Bash commands.
Testing after Claude Code session restart.
"""

import logging
import os
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


def is_git_commit_command(command: str) -> bool:
    """Check if the command is a Git commit.

    Args:
        command: The bash command that was executed

    Returns:
        True if it's a git commit command
    """
    # Normalize command by removing extra spaces and quotes
    normalized = command.strip().replace('"', '').replace("'", "")
    
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
                logger.info(f"✅ Post-commit processing completed ({execution_time:.2f}s)")
            else:
                logger.warning(f"⚠️ Post-commit processing had issues ({execution_time:.2f}s)")
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
    Expected format:
    {
        "tool_name": "Bash",
        "tool_input": {"command": "git commit -m 'message'", ...},
        "tool_response": {...}
    }

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    logger = get_git_hooks_logger()
    
    try:
        import json
        
        # Read JSON input from stdin
        hook_input = json.load(sys.stdin)
        
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
        
        # Run post-commit processing
        success = run_post_commit_processing()
        
        return 0 if success else 1
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON input: {e}")
        return 0  # Don't fail the hook
    except Exception as e:
        logger.error(f"Unexpected error in Git hooks detector: {e}")
        return 0  # Don't fail the hook


if __name__ == "__main__":
    sys.exit(main())