"""CLI interface for PyQC."""

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
def init(
    with_pre_commit: bool = typer.Option(
        False, "--with-pre-commit", help="Generate pre-commit config"
    ),
    with_hooks: bool = typer.Option(
        False, "--with-hooks", help="Generate Claude Code hooks config"
    ),
    type_checker: str = typer.Option(
        "mypy", "--type-checker", help="Type checker: mypy, ty"
    ),
) -> None:
    """Initialize PyQC in a project."""
    target_path = Path.cwd()

    console.print("🚀 Initializing PyQC in project...", style="bold blue")

    try:
        # 1. Create PyQC configuration
        console.print("\n1️⃣ Creating PyQC configuration...")
        _init_config(target_path, False, False)

        # 2. Generate pre-commit config if requested
        if with_pre_commit:
            console.print("\n2️⃣ Generating pre-commit configuration...")
            _create_pre_commit_config(target_path)

        # 3. Generate Claude Code hooks if requested
        if with_hooks:
            console.print("\n3️⃣ Generating Claude Code hooks configuration...")
            _create_hooks_config(target_path)

        # 4. Show next steps
        console.print("\n✅ PyQC initialization completed!", style="bold green")
        console.print("\n📋 Next steps:")
        console.print("  • Run 'uv run pyqc check' to check your code")
        console.print("  • Run 'uv run pyqc fix' to auto-fix issues")
        console.print("  • Run 'uv run pyqc config show' to view configuration")

        if with_pre_commit:
            console.print("  • Run 'pre-commit install' to install pre-commit hooks")

        if with_hooks:
            console.print("  • Restart Claude Code to activate hooks")

    except Exception as e:
        console.print(f"❌ Error initializing PyQC: {e}", style="red")
        raise typer.Exit(1)


def _create_pre_commit_config(target_path: Path) -> None:
    """Create pre-commit configuration."""
    config_path = target_path / ".pre-commit-config.yaml"

    if config_path.exists():
        console.print(
            f"⚠️ Pre-commit config already exists: {config_path}", style="yellow"
        )
        if not typer.confirm("Do you want to overwrite it?"):
            console.print("❌ Pre-commit config creation cancelled")
            return

    pre_commit_config = """repos:
  - repo: local
    hooks:
      - id: pyqc-check
        name: PyQC Check
        entry: uv run pyqc check
        language: system
        types: [python]
        pass_filenames: false
        
      - id: pyqc-fix
        name: PyQC Fix
        entry: uv run pyqc fix
        language: system
        types: [python]
        pass_filenames: false
"""

    try:
        with open(config_path, "w") as f:
            f.write(pre_commit_config)
        console.print(f"✅ Created pre-commit config: {config_path}")
    except Exception as e:
        console.print(f"❌ Error creating pre-commit config: {e}", style="red")
        raise


def _create_hooks_config(target_path: Path) -> None:
    """Create Claude Code hooks configuration."""
    hooks_dir = target_path / ".claude"
    hooks_dir.mkdir(exist_ok=True)

    config_path = hooks_dir / "hooks.json"

    if config_path.exists():
        console.print(f"⚠️ Hooks config already exists: {config_path}", style="yellow")
        if not typer.confirm("Do you want to overwrite it?"):
            console.print("❌ Hooks config creation cancelled")
            return

    hooks_config = {
        "hooks": {
            "PostToolUse": {
                "Write,Edit,MultiEdit": {
                    "command": "uv run pyqc check ${file} --output github",
                    "onFailure": "warn",
                    "timeout": 10000,
                }
            }
        }
    }

    try:
        with open(config_path, "w") as f:
            json.dump(hooks_config, f, indent=2)
        console.print(f"✅ Created Claude Code hooks config: {config_path}")
    except Exception as e:
        console.print(f"❌ Error creating hooks config: {e}", style="red")
        raise


if __name__ == "__main__":
    app()
