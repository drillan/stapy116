"""Type checking wrapper for mypy/ty."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class TypeChecker:
    """Type checker wrapper for mypy/ty."""
    
    def __init__(self, checker_type: str = "mypy", config: dict[str, Any] | None = None) -> None:
        """Initialize type checker with configuration."""
        self.checker_type = checker_type
        self.config = config or {}
    
    def check_types(self, path: Path) -> list[dict[str, Any]]:
        """Run type checks on the given path."""
        # Placeholder implementation
        return []