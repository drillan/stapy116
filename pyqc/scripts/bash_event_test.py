#!/usr/bin/env python3
"""Simple test script to verify Claude Code Bash PostToolUse event handling.

This script logs Bash events to verify that Claude Code hooks are working.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def main() -> int:
    """Test Bash event handling and log results."""
    # Set up log file path
    project_dir = Path(__file__).parent.parent
    log_dir = project_dir / ".pyqc"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "bash_event_test.log"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - Bash event detected!\n")

            # Try to read JSON input from stdin
            try:
                hook_input = json.load(sys.stdin)
                f.write("Hook input received:\n")
                f.write(f"{json.dumps(hook_input, indent=2, ensure_ascii=False)}\n")

                # Extract command if available
                tool_input = hook_input.get("tool_input", {})
                command = tool_input.get("command", "")
                if command:
                    f.write(f"Command executed: {command}\n")

            except json.JSONDecodeError as e:
                f.write(f"Failed to parse JSON input: {e}\n")
            except Exception as e:
                f.write(f"Error reading stdin: {e}\n")

            f.write("=" * 50 + "\n")

    except Exception as e:
        # Fallback logging to ensure we know something happened
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()} - ERROR: {e}\n")
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
