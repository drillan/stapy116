"""CLI interface for PyQC.

This module provides the main CLI interface for the Python Quality Checker tool.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from pyqc.config import PyQCConfig
from pyqc.core import PyQCRunner, ReportGenerator

app = typer.Typer(
    name="pyqc",
    help="Python Quality Checker - Integrated code quality tools",
    no_args_is_help=True,
)
console = Console()


def find_python_files(path: Path) -> list[Path]:
    """Find Python files in the given path."""
    if path.is_file() and path.suffix == ".py":
        return [path]
    elif path.is_dir():
        # Find all .py files, excluding common directories
        exclude_patterns = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            ".venv",
            "venv",
            "node_modules",
        }
        python_files = []
        for py_file in path.rglob("*.py"):
            if not any(exclude in str(py_file) for exclude in exclude_patterns):
                python_files.append(py_file)
        return sorted(python_files)
    else:
        return []


def load_config(start_dir: Path) -> PyQCConfig:
    """Load PyQC configuration."""
    try:
        return PyQCConfig.load(start_dir)
    except Exception as e:
        console.print(f"⚠️ Warning: Could not load config: {e}", style="yellow")
        console.print("Using default configuration", style="yellow")
        return PyQCConfig()


@app.command()
def check(
    path: str = typer.Argument(".", help="Path to check"),
    all_checks: bool = typer.Option(True, "--all", help="Run all checks"),
    lint: bool = typer.Option(False, "--lint", help="Run lint checks only"),
    types: bool = typer.Option(False, "--types", help="Run type checks only"),
    format_check: bool = typer.Option(False, "--format", help="Run format checks only"),
    output: str = typer.Option(
        "text", "--output", help="Output format: text, json, github"
    ),
    show_performance: bool = typer.Option(
        False, "--show-performance", help="Show performance metrics"
    ),
) -> None:
    """Run quality checks on Python code."""
    target_path = Path(path).resolve()

    if not target_path.exists():
        console.print(f"❌ Error: Path '{path}' does not exist", style="red")
        raise typer.Exit(1)

    # Find Python files to check
    python_files = find_python_files(target_path)
    if not python_files:
        console.print(f"⚠️ No Python files found in '{path}'", style="yellow")
        raise typer.Exit(0)

    # Load configuration
    config = load_config(target_path)

    # Show progress
    if output == "text":
        console.print(f"🔍 Checking {len(python_files)} Python file(s)...")

    # Initialize runner
    runner = PyQCRunner(config)

    # Process files using parallel execution
    try:
        results = runner.check_files_parallel(python_files)

        # Show per-file progress for multiple files in text mode
        if output == "text" and len(python_files) > 1:
            for result in results:
                status = "✅" if result.success and not result.issues else "⚠️"
                issue_count = len(result.issues)
                console.print(
                    f"  {status} {result.path.relative_to(target_path)}: {issue_count} issues"
                )

    except Exception as e:
        console.print(f"❌ Error during parallel execution: {e}", style="red")
        sys.exit(1)

    # Generate and display report
    try:
        if output == "json":
            json_report = ReportGenerator.generate_json_report(
                results, include_performance=show_performance
            )
            console.print(json.dumps(json_report, indent=2))
        elif output == "github":
            github_report = ReportGenerator.generate_github_actions_report(results)
            if github_report:
                console.print(github_report)
        else:  # text format
            text_report = ReportGenerator.generate_text_report(
                results, show_performance=show_performance
            )
            console.print(text_report)

    except Exception as e:
        console.print(f"❌ Error generating report: {e}", style="red")
        sys.exit(1)

    # Exit with appropriate code
    total_issues = sum(len(result.issues) for result in results)
    failed_files = sum(1 for result in results if not result.success)

    if failed_files > 0:
        sys.exit(2)  # Execution errors
    elif total_issues > 0:
        sys.exit(1)  # Issues found
    else:
        sys.exit(0)  # No issues


@app.command()
def fix(
    path: str = typer.Argument(".", help="Path to fix"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be fixed"),
    backup: bool = typer.Option(False, "--backup", help="Create backup before fixing"),
    format_only: bool = typer.Option(
        False, "--format-only", help="Fix format issues only"
    ),
) -> None:
    """Automatically fix code quality issues."""
    target_path = Path(path).resolve()

    if not target_path.exists():
        console.print(f"❌ Error: Path '{path}' does not exist", style="red")
        raise typer.Exit(1)

    # Find Python files to fix
    python_files = find_python_files(target_path)
    if not python_files:
        console.print(f"⚠️ No Python files found in '{path}'", style="yellow")
        raise typer.Exit(0)

    # Load configuration
    config = load_config(target_path)

    # Show what we're going to do
    action = "would fix" if dry_run else "fixing"
    console.print(f"🔧 {action.capitalize()} {len(python_files)} Python file(s)...")

    if backup and not dry_run:
        console.print("⚠️ Backup option not yet implemented", style="yellow")

    # Initialize runner
    runner = PyQCRunner(config)

    # Process files using parallel execution
    try:
        results = runner.fix_files_parallel(python_files, dry_run=dry_run)

        # Process results
        fixed_files = 0
        failed_files = 0

        for result in results:
            if result.success and "ruff-format-fix" in result.checks_run:
                fixed_files += 1
                status = "Would fix" if dry_run else "Fixed"
                console.print(f"  ✅ {status}: {result.path.relative_to(target_path)}")
            elif result.success:
                console.print(
                    f"  ➖ No fixes needed: {result.path.relative_to(target_path)}"
                )
            else:
                failed_files += 1
                console.print(
                    f"  ❌ Error fixing {result.path.relative_to(target_path)}: {result.error_message}",
                    style="red",
                )

    except Exception as e:
        console.print(f"❌ Error during parallel execution: {e}", style="red")
        failed_files = len(python_files)
        fixed_files = 0

    # Summary
    if dry_run:
        console.print(
            f"\n📊 Summary: {fixed_files} file(s) would be fixed, {failed_files} errors"
        )
    else:
        console.print(
            f"\n📊 Summary: {fixed_files} file(s) fixed, {failed_files} errors"
        )

    # Exit with appropriate code
    if failed_files > 0:
        sys.exit(1)
    else:
        sys.exit(0)


@app.command()
def config(
    action: str = typer.Argument("show", help="Action: show, set, init"),
    key: str = typer.Option("", "--key", help="Configuration key (for set action)"),
    value: str = typer.Option(
        "", "--value", help="Configuration value (for set action)"
    ),
    global_config: bool = typer.Option(
        False, "--global", help="Use global configuration"
    ),
    local_config: bool = typer.Option(False, "--local", help="Use local configuration"),
) -> None:
    """Manage PyQC configuration."""
    target_path = Path.cwd()

    if action == "show":
        _show_config(target_path, global_config, local_config)
    elif action == "set":
        _set_config(target_path, key, value, global_config, local_config)
    elif action == "init":
        _init_config(target_path, global_config, local_config)
    else:
        console.print(f"❌ Unknown action: {action}", style="red")
        console.print("Available actions: show, set, init")
        raise typer.Exit(1)


def _show_config(target_path: Path, global_config: bool, local_config: bool) -> None:
    """Show current configuration."""
    console.print("⚙️ PyQC Configuration", style="bold blue")

    try:
        config = load_config(target_path)

        # Show configuration in a nice table
        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        # Core settings
        table.add_row("Line Length", str(config.line_length))
        table.add_row("Type Checker", config.type_checker)
        table.add_row("Parallel Execution", str(config.parallel))

        # Ruff settings
        table.add_row("Ruff Extend Select", ", ".join(config.ruff.extend_select))
        table.add_row("Ruff Ignore", ", ".join(config.ruff.ignore))

        # MyPy settings
        table.add_row("MyPy Strict", str(config.mypy.strict))
        table.add_row(
            "MyPy Ignore Missing Imports", str(config.mypy.ignore_missing_imports)
        )

        console.print(table)

        # Show configuration file locations
        console.print("\n📄 Configuration Files:")
        config_files = [
            target_path / "pyproject.toml",
            target_path / ".pyqc.yaml",
            target_path / ".pyqc.yml",
        ]

        for config_file in config_files:
            if config_file.exists():
                console.print(f"  ✅ {config_file}")
            else:
                console.print(f"  ➖ {config_file} (not found)")

    except Exception as e:
        console.print(f"❌ Error loading configuration: {e}", style="red")
        raise typer.Exit(1)


def _set_config(
    target_path: Path, key: str, value: str, global_config: bool, local_config: bool
) -> None:
    """Set configuration value."""
    if not key or not value:
        console.print(
            "❌ Both --key and --value are required for set action", style="red"
        )
        raise typer.Exit(1)

    console.print(f"🔧 Setting {key} = {value}")

    # For now, just show what would be done
    console.print("⚠️ Configuration modification not yet implemented", style="yellow")
    console.print("💡 Use 'pyqc config init' to create a configuration file,")
    console.print("   then edit it manually with your preferred settings.")

    # TODO: Implement actual configuration modification
    # This would involve:
    # 1. Loading existing config
    # 2. Modifying the specified key
    # 3. Writing back to the appropriate file


def _init_config(target_path: Path, global_config: bool, local_config: bool) -> None:
    """Initialize configuration file."""
    config_path = target_path / "pyproject.toml"

    if config_path.exists():
        console.print(
            f"⚠️ Configuration file already exists: {config_path}", style="yellow"
        )
        if not typer.confirm("Do you want to overwrite it?"):
            console.print("❌ Configuration initialization cancelled")
            raise typer.Exit(0)

    console.print(f"🚀 Creating configuration file: {config_path}")

    # Create default configuration
    default_config = """
# PyQC Configuration
[tool.pyqc]
line-length = 88
type-checker = "mypy"
parallel = true

[tool.pyqc.ruff]
extend-select = ["I", "N", "UP"]
ignore = []

[tool.pyqc.mypy]
strict = true
ignore_missing_imports = true
"""

    try:
        if config_path.exists():
            # Read existing pyproject.toml and add PyQC section
            with open(config_path) as f:
                existing_content = f.read()

            if "[tool.pyqc]" not in existing_content:
                with open(config_path, "a") as f:
                    f.write(default_config)
                console.print(f"✅ Added PyQC configuration to existing {config_path}")
            else:
                console.print(f"⚠️ PyQC configuration already exists in {config_path}")
        else:
            # Create new pyproject.toml
            with open(config_path, "w") as f:
                f.write(default_config.strip())
            console.print(f"✅ Created new configuration file: {config_path}")

        # Verify configuration
        console.print("\n🔍 Verifying configuration...")
        config = load_config(target_path)
        console.print("✅ Configuration loaded successfully")
        console.print(f"   Line length: {config.line_length}")
        console.print(f"   Type checker: {config.type_checker}")

    except Exception as e:
        console.print(f"❌ Error creating configuration: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def hooks(
    action: str = typer.Argument(
        "stats", help="Action: stats, log, clear, setup, validate, migrate"
    ),
    lines: int = typer.Option(20, "--lines", "-n", help="Number of log lines to show"),
) -> None:
    """Manage and monitor Claude Code hooks."""
    if action == "stats":
        _show_hooks_stats()
    elif action == "log":
        _show_hooks_log(lines)
    elif action == "clear":
        _clear_hooks_log()
    elif action == "setup":
        _setup_hooks_config()
    elif action == "validate":
        _validate_hooks_config()
    elif action == "migrate":
        _migrate_hooks_config()
    else:
        console.print(f"❌ Unknown action: {action}", style="red")
        console.print("Available actions: stats, log, clear, setup, validate, migrate")
        sys.exit(1)


def _show_hooks_stats() -> None:
    """Show Claude Code hooks execution statistics."""
    from pyqc.utils.logger import get_hooks_stats

    console.print("📊 Claude Code Hooks Statistics", style="bold blue")

    stats = get_hooks_stats()

    if stats["total_executions"] == 0:
        console.print(
            "No hooks executions found. Try editing a Python file to trigger hooks."
        )
        return

    table = Table(title="Hooks Execution Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Executions", str(stats["total_executions"]))
    table.add_row("Successful", str(stats["successful_executions"]))
    table.add_row("Failed", str(stats["failed_executions"]))
    table.add_row("Success Rate", f"{stats['success_rate']:.1f}%")
    table.add_row("Average Time", f"{stats['average_execution_time']:.2f}s")
    table.add_row("Last Execution", stats["last_execution"] or "Never")

    console.print(table)


def _show_hooks_log(lines: int) -> None:
    """Show recent hooks log entries."""
    log_file = Path.cwd() / ".pyqc" / "hooks.log"

    if not log_file.exists():
        console.print("No hooks log file found. Hooks haven't been executed yet.")
        return

    console.print(f"📋 Last {lines} hooks log entries:", style="bold blue")

    try:
        with open(log_file, encoding="utf-8") as f:
            log_lines = f.readlines()

        # Show last N lines
        recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines

        for line in recent_lines:
            line = line.strip()
            if line:
                # Color-code based on log level
                if "ERROR" in line:
                    console.print(line, style="red")
                elif "WARNING" in line:
                    console.print(line, style="yellow")
                elif "SUCCESS" in line:
                    console.print(line, style="green")
                else:
                    console.print(line)

    except Exception as e:
        console.print(f"❌ Error reading log file: {e}", style="red")


def _clear_hooks_log() -> None:
    """Clear the hooks log file."""
    log_file = Path.cwd() / ".pyqc" / "hooks.log"

    if not log_file.exists():
        console.print("No hooks log file to clear.")
        return

    if typer.confirm("Are you sure you want to clear the hooks log?"):
        try:
            log_file.unlink()
            console.print("✅ Hooks log cleared successfully.")
        except Exception as e:
            console.print(f"❌ Error clearing log file: {e}", style="red")
    else:
        console.print("❌ Operation cancelled.")


def _detect_project_structure() -> tuple[Path, Path]:
    """Detect PyQC project structure and return project root and pyqc directory.

    Returns:
        Tuple of (project_root, pyqc_directory)
    """
    current_dir = Path.cwd()

    # Look for pyqc directory in current and parent directories
    for dir_path in [current_dir] + list(current_dir.parents):
        pyqc_dir = dir_path / "pyqc"
        if pyqc_dir.exists() and (pyqc_dir / "src" / "pyqc").exists():
            return dir_path, pyqc_dir

    # If not found, assume we're in the pyqc directory itself
    if (current_dir / "src" / "pyqc").exists():
        return current_dir.parent, current_dir

    # Last resort: assume current directory is project root
    pyqc_dir = current_dir / "pyqc"
    return current_dir, pyqc_dir


def _setup_hooks_config() -> None:
    """Set up environment-independent Claude Code hooks configuration."""
    console.print("🚀 Setting up Claude Code hooks configuration...", style="bold blue")

    try:
        # Detect project structure
        project_root, pyqc_dir = _detect_project_structure()

        console.print(f"📁 Detected project root: {project_root}")
        console.print(f"📁 Detected PyQC directory: {pyqc_dir}")

        # Create .claude directory if it doesn't exist
        claude_dir = project_root / ".claude"
        claude_dir.mkdir(exist_ok=True)

        settings_file = claude_dir / "settings.json"

        # Check if settings.json already exists
        if settings_file.exists():
            console.print(
                f"⚠️ Settings file already exists: {settings_file}", style="yellow"
            )
            if not typer.confirm(
                "Do you want to overwrite it? (Backup will be created)"
            ):
                console.print("❌ Setup cancelled.")
                return

            # Create backup
            backup_file = settings_file.with_suffix(".json.backup")
            settings_file.rename(backup_file)
            console.print(f"📄 Backup created: {backup_file}")

        # Generate environment-specific configuration using absolute paths (required by uv --directory)
        hooks_config = {
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": "Bash",
                        "hooks": [
                            {
                                "type": "command",
                                "command": f"uv --directory {pyqc_dir} run scripts/git_hooks_detector.py",
                                "onFailure": "block",
                                "timeout": 60000,
                            }
                        ],
                    }
                ],
                "PostToolUse": [
                    {
                        "matcher": "Write|Edit|MultiEdit",
                        "hooks": [
                            {
                                "type": "command",
                                "command": f"uv --directory {pyqc_dir} run scripts/claude_hooks.py",
                                "onFailure": "warn",
                                "timeout": 15000,
                            }
                        ],
                    }
                ],
            }
        }

        # Write new configuration
        with open(settings_file, "w") as f:
            json.dump(hooks_config, f, indent=2)

        console.print(f"✅ Created new hooks configuration: {settings_file}")
        console.print("\n📋 Configuration details:")
        console.print(f"   Project root: {project_root}")
        console.print(f"   PyQC directory: {pyqc_dir}")
        console.print(
            f"   Commands use 'uv --directory {pyqc_dir}' (absolute path required)"
        )
        console.print(
            "\n⚠️ Note: This configuration contains environment-specific absolute paths"
        )
        console.print("   Add .claude/settings.json to .gitignore for team development")

        console.print(
            "\n🔄 Please restart Claude Code to activate the new hooks configuration."
        )

    except Exception as e:
        console.print(f"❌ Error setting up hooks configuration: {e}", style="red")
        sys.exit(1)


def _validate_hooks_config() -> None:
    """Validate the current Claude Code hooks configuration."""
    console.print("🔍 Validating Claude Code hooks configuration...", style="bold blue")

    try:
        # Detect project structure
        project_root, pyqc_dir = _detect_project_structure()

        claude_dir = project_root / ".claude"
        settings_file = claude_dir / "settings.json"

        if not settings_file.exists():
            console.print(f"❌ No settings file found: {settings_file}", style="red")
            console.print("💡 Run 'uv run pyqc hooks setup' to create configuration.")
            return

        # Load and validate configuration
        with open(settings_file) as f:
            config = json.load(f)

        # Check basic structure
        if "hooks" not in config:
            console.print("❌ No 'hooks' section found in configuration", style="red")
            return

        # Validate hook scripts exist
        required_scripts = [
            pyqc_dir / "scripts" / "git_hooks_detector.py",
            pyqc_dir / "scripts" / "claude_hooks.py",
        ]

        all_valid = True
        for script in required_scripts:
            if script.exists():
                console.print(f"✅ Script found: {script}")
            else:
                console.print(f"❌ Script missing: {script}", style="red")
                all_valid = False

        # Check for invalid relative paths in uv --directory commands
        config_str = json.dumps(config, indent=2)
        has_invalid_paths = False

        # Look for relative paths in --directory (which don't work)
        for line in config_str.split("\n"):
            if "--directory" in line:
                # Extract the path after --directory
                parts = line.split("--directory")
                if len(parts) > 1:
                    path_part = parts[1].strip().split()[0].strip('"')
                    # Check if path is relative (doesn't start with / or contain :)
                    if not (path_part.startswith("/") or ":" in path_part):
                        console.print(
                            "❌ Found relative path in uv --directory command",
                            style="red",
                        )
                        console.print(f"   Problem line: {line.strip()}")
                        console.print(f"   Relative path: {path_part}")
                        console.print("   uv --directory requires absolute paths")
                        has_invalid_paths = True
                        all_valid = False

        if has_invalid_paths:
            console.print(
                "💡 Run 'uv run pyqc hooks migrate' to fix relative path issues"
            )
        else:
            # Check if we have proper absolute paths in --directory commands
            has_directory_commands = "--directory" in config_str
            if has_directory_commands:
                console.print("✅ uv --directory commands use absolute paths (correct)")
            else:
                console.print("⚠️ No uv --directory commands found", style="yellow")

        if all_valid:
            console.print("✅ Configuration validation passed!", style="green")
            console.print("📋 Summary:")
            console.print(f"   Settings file: {settings_file}")
            console.print(f"   Project root: {project_root}")
            console.print(f"   PyQC directory: {pyqc_dir}")
        else:
            console.print("❌ Configuration validation failed", style="red")

    except json.JSONDecodeError as e:
        console.print(f"❌ Invalid JSON in settings file: {e}", style="red")
    except Exception as e:
        console.print(f"❌ Error validating configuration: {e}", style="red")


def _migrate_hooks_config() -> None:
    """Migrate existing hooks configuration to environment-independent format."""
    console.print("🔄 Migrating hooks configuration...", style="bold blue")

    try:
        # Detect project structure
        project_root, pyqc_dir = _detect_project_structure()

        claude_dir = project_root / ".claude"
        settings_file = claude_dir / "settings.json"

        if not settings_file.exists():
            console.print(f"❌ No settings file found: {settings_file}", style="red")
            console.print("💡 Run 'uv run pyqc hooks setup' to create configuration.")
            return

        # Load existing configuration
        with open(settings_file) as f:
            config = json.load(f)

        # Check if migration is needed (look for old cd format or relative --directory paths)
        config_str = json.dumps(config, indent=2)
        needs_migration = False

        # Check for old cd format
        if "cd " in config_str:
            console.print("🔍 Found old 'cd' format commands")
            needs_migration = True

        # Check for relative paths in --directory (which don't work)
        for line in config_str.split("\n"):
            if "--directory" in line:
                # Extract the path after --directory
                parts = line.split("--directory")
                if len(parts) > 1:
                    path_part = parts[1].strip().split()[0].strip('"')
                    # Check if path is relative (doesn't start with / or contain :)
                    if not (path_part.startswith("/") or ":" in path_part):
                        console.print(
                            f"🔍 Found relative path in uv --directory: {path_part}"
                        )
                        needs_migration = True
                        break

        if not needs_migration:
            console.print(
                "✅ Configuration is already using correct absolute paths!",
                style="green",
            )
            return

        console.print(
            "🔍 Found environment-dependent configuration, proceeding with migration..."
        )

        # Create backup
        backup_file = settings_file.with_suffix(".json.migrate_backup")
        settings_file.rename(backup_file)
        console.print(f"📄 Backup created: {backup_file}")

        # Create new environment-specific configuration using absolute paths (required by uv --directory)
        new_config = {
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": "Bash",
                        "hooks": [
                            {
                                "type": "command",
                                "command": f"uv --directory {pyqc_dir} run scripts/git_hooks_detector.py",
                                "onFailure": "block",
                                "timeout": 60000,
                            }
                        ],
                    }
                ],
                "PostToolUse": [
                    {
                        "matcher": "Write|Edit|MultiEdit",
                        "hooks": [
                            {
                                "type": "command",
                                "command": f"uv --directory {pyqc_dir} run scripts/claude_hooks.py",
                                "onFailure": "warn",
                                "timeout": 15000,
                            }
                        ],
                    }
                ],
            }
        }

        # Write migrated configuration
        with open(settings_file, "w") as f:
            json.dump(new_config, f, indent=2)

        console.print(f"✅ Migration completed: {settings_file}")
        console.print("\n📋 Migration summary:")
        console.print(f"   Backup: {backup_file}")
        console.print(f"   New config: {settings_file}")
        console.print("   Updated to use absolute paths (required by uv --directory)")
        console.print(f"   Commands use 'uv --directory {pyqc_dir}'")
        console.print(
            "\n⚠️ Note: Configuration now contains environment-specific absolute paths"
        )
        console.print("   Recommend adding .claude/settings.json to .gitignore")

        console.print(
            "\n🔄 Please restart Claude Code to activate the migrated configuration."
        )

    except json.JSONDecodeError as e:
        console.print(f"❌ Invalid JSON in settings file: {e}", style="red")
    except Exception as e:
        console.print(f"❌ Error migrating configuration: {e}", style="red")


if __name__ == "__main__":
    app()
