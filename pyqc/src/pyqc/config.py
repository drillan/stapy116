"""Configuration management for PyQC."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator


class RuffConfig(BaseModel):
    """Ruff checker configuration."""
    
    extend_select: list[str] = Field(default=["I", "N", "UP"], alias="extend-select")
    ignore: list[str] = Field(default=["E501"])
    line_length: int = Field(default=88, ge=1, le=300, alias="line-length")
    
    model_config = {"populate_by_name": True}


class TypeCheckerConfig(BaseModel):
    """Type checker configuration."""
    
    strict: bool = Field(default=True)
    ignore_missing_imports: bool = Field(default=True)


class PyQCConfig(BaseModel):
    """Main PyQC configuration."""
    
    line_length: int = Field(default=88, ge=1, le=300, alias="line-length")
    type_checker: str = Field(default="mypy", alias="type-checker")
    parallel: bool = Field(default=True)
    ruff: RuffConfig = Field(default_factory=RuffConfig)
    mypy: TypeCheckerConfig = Field(default_factory=TypeCheckerConfig)
    
    model_config = {"populate_by_name": True}
    
    @field_validator("type_checker")
    @classmethod
    def validate_type_checker(cls, v: str) -> str:
        """Validate type checker choice."""
        allowed = {"mypy", "ty"}
        if v not in allowed:
            raise ValueError(f"type_checker must be one of {allowed}, got {v!r}")
        return v
    
    @classmethod
    def find_config_file(cls, start_dir: Path) -> Path | None:
        """Find configuration file in directory hierarchy."""
        current = start_dir.resolve()
        
        while current != current.parent:
            # Priority order: .pyqc.yaml > .pyqc.yml > pyproject.toml
            for config_name in [".pyqc.yaml", ".pyqc.yml", "pyproject.toml"]:
                config_path = current / config_name
                if config_path.exists():
                    return config_path
            current = current.parent
        
        return None
    
    @classmethod
    def load_from_file(cls, path: Path) -> PyQCConfig:
        """Load configuration from file."""
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        try:
            if path.suffix == ".toml":
                with open(path, "rb") as f:
                    data = tomllib.load(f)
                # Extract [tool.pyqc] section
                config_data = data.get("tool", {}).get("pyqc", {})
                
            elif path.suffix in {".yaml", ".yml"}:
                with open(path, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                # Extract pyqc section
                config_data = data.get("pyqc", {}) if data else {}
            else:
                raise ValueError(f"Unsupported config file format: {path.suffix}")
        
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML in {path}: {e}") from e
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {path}: {e}") from e
        
        return cls.model_validate(config_data, by_alias=True)
    
    @classmethod
    def load(cls, start_dir: Path | None = None) -> PyQCConfig:
        """Load configuration with automatic discovery."""
        if start_dir is None:
            start_dir = Path.cwd()
        
        config_path = cls.find_config_file(start_dir)
        if config_path is None:
            # Return default configuration
            return cls()
        
        return cls.load_from_file(config_path)
    
    def save(self, path: Path) -> None:
        """Save configuration to file."""
        if path.suffix == ".toml":
            import tomli_w
            config_dict = {"tool": {"pyqc": self.model_dump()}}
            with open(path, "wb") as f:
                tomli_w.dump(config_dict, f)
        elif path.suffix in {".yaml", ".yml"}:
            config_dict = {"pyqc": self.model_dump()}
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(config_dict, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")