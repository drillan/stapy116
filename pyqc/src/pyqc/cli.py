"""CLI interface for PyQC."""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(
    name="pyqc",
    help="Python Quality Checker - Integrated code quality tools",
    no_args_is_help=True,
)
console = Console()


@app.command()
def check(
    path: str = typer.Argument(".", help="Path to check"),
    all_checks: bool = typer.Option(True, "--all", help="Run all checks"),
    lint: bool = typer.Option(False, "--lint", help="Run lint checks only"),
    types: bool = typer.Option(False, "--types", help="Run type checks only"),
    format_check: bool = typer.Option(False, "--format", help="Run format checks only"),
    output: str = typer.Option("text", "--output", help="Output format: text, json, github"),
) -> None:
    """Run quality checks on Python code."""
    console.print(f"🔍 Checking {path}...")
    console.print("✅ PyQC check completed (placeholder)")


@app.command()
def fix(
    path: str = typer.Argument(".", help="Path to fix"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be fixed"),
    backup: bool = typer.Option(False, "--backup", help="Create backup before fixing"),
    format_only: bool = typer.Option(False, "--format-only", help="Fix format issues only"),
) -> None:
    """Automatically fix code quality issues."""
    console.print(f"🔧 Fixing {path}...")
    console.print("✅ PyQC fix completed (placeholder)")


@app.command()
def config(
    action: str = typer.Argument("show", help="Action: show, set, init"),
) -> None:
    """Manage PyQC configuration."""
    console.print(f"⚙️ Config {action}...")
    console.print("✅ PyQC config completed (placeholder)")


@app.command()
def init(
    with_pre_commit: bool = typer.Option(False, "--with-pre-commit", help="Generate pre-commit config"),
    with_hooks: bool = typer.Option(False, "--with-hooks", help="Generate Claude Code hooks config"),
    type_checker: str = typer.Option("mypy", "--type-checker", help="Type checker: mypy, ty"),
) -> None:
    """Initialize PyQC in a project."""
    console.print("🚀 Initializing PyQC...")
    console.print("✅ PyQC init completed (placeholder)")


if __name__ == "__main__":
    app()