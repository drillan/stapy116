"""Tests for configuration management."""

from __future__ import annotations

from pathlib import Path

import pytest

from pyqc.config import PyQCConfig, RuffConfig, TypeCheckerConfig


class TestPyQCConfig:
    """Test PyQC configuration."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = PyQCConfig()

        assert config.line_length == 88
        assert config.type_checker == "mypy"
        assert config.parallel is True
        assert config.exclude == []

        # Test nested configs
        assert isinstance(config.ruff, RuffConfig)
        assert isinstance(config.mypy, TypeCheckerConfig)

    def test_ruff_config_defaults(self) -> None:
        """Test Ruff configuration defaults."""
        config = RuffConfig()

        assert config.extend_select == ["I", "N", "UP"]
        assert config.ignore == ["E501"]
        assert config.line_length == 88

    def test_type_checker_config_defaults(self) -> None:
        """Test type checker configuration defaults."""
        config = TypeCheckerConfig()

        assert config.strict is True
        assert config.ignore_missing_imports is True

    def test_config_validation_line_length(self) -> None:
        """Test line length validation."""
        # Valid values
        config = PyQCConfig(line_length=80)
        assert config.line_length == 80

        config = PyQCConfig(line_length=120)
        assert config.line_length == 120

        # Invalid values should be rejected
        with pytest.raises(ValueError):
            PyQCConfig(line_length=0)

        with pytest.raises(ValueError):
            PyQCConfig(line_length=-1)

    def test_config_validation_type_checker(self) -> None:
        """Test type checker validation."""
        # Valid values
        config = PyQCConfig(type_checker="mypy")
        assert config.type_checker == "mypy"

        # Invalid values should be rejected
        with pytest.raises(ValueError):
            PyQCConfig(type_checker="invalid")

    def test_exclude_configuration(self) -> None:
        """Test exclude patterns configuration."""
        # Test default (empty list)
        config = PyQCConfig()
        assert config.exclude == []

        # Test with exclude patterns
        config = PyQCConfig(exclude=["sample_project", "test_data"])
        assert config.exclude == ["sample_project", "test_data"]

        # Test empty exclude list
        config = PyQCConfig(exclude=[])
        assert config.exclude == []


class TestConfigFileLoading:
    """Test configuration file loading."""

    def test_load_from_pyproject_toml(self, tmp_path: Path) -> None:
        """Test loading from pyproject.toml."""
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text("""
[tool.pyqc]
line-length = 100
type-checker = "mypy"
parallel = false
exclude = ["sample_project", "test_data"]

[tool.pyqc.ruff]
extend-select = ["E", "F"]
ignore = ["E203"]
line-length = 100

[tool.pyqc.mypy]
strict = false
ignore_missing_imports = false
""")

        config = PyQCConfig.load_from_file(config_file)

        assert config.line_length == 100
        assert config.type_checker == "mypy"
        assert config.parallel is False
        assert config.exclude == ["sample_project", "test_data"]

        assert config.ruff.extend_select == ["E", "F"]
        assert config.ruff.ignore == ["E203"]
        assert config.ruff.line_length == 100

        assert config.mypy.strict is False
        assert config.mypy.ignore_missing_imports is False

    def test_load_from_yaml(self, tmp_path: Path) -> None:
        """Test loading from YAML file."""
        config_file = tmp_path / ".pyqc.yaml"
        config_file.write_text("""
pyqc:
  line-length: 120
  type-checker: mypy
  parallel: true
  
  ruff:
    extend-select: [W, E, F]
    ignore: [W503]
    line-length: 120
    
  mypy:
    strict: true
    ignore_missing_imports: true
""")

        config = PyQCConfig.load_from_file(config_file)

        assert config.line_length == 120
        assert config.type_checker == "mypy"
        assert config.parallel is True

        assert config.ruff.extend_select == ["W", "E", "F"]
        assert config.ruff.ignore == ["W503"]
        assert config.ruff.line_length == 120

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        """Test loading from nonexistent file."""
        config_file = tmp_path / "nonexistent.toml"

        with pytest.raises(FileNotFoundError):
            PyQCConfig.load_from_file(config_file)

    def test_load_invalid_toml(self, tmp_path: Path) -> None:
        """Test loading invalid TOML."""
        config_file = tmp_path / "invalid.toml"
        config_file.write_text("invalid toml content [")

        with pytest.raises(ValueError, match="Invalid TOML"):
            PyQCConfig.load_from_file(config_file)

    def test_load_invalid_yaml(self, tmp_path: Path) -> None:
        """Test loading invalid YAML."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [")

        with pytest.raises(ValueError, match="Invalid YAML"):
            PyQCConfig.load_from_file(config_file)

    def test_save_to_toml(self, tmp_path: Path) -> None:
        """Test saving config to TOML file."""
        config = PyQCConfig(line_length=100, type_checker="mypy", parallel=False)
        config_file = tmp_path / "saved.toml"

        config.save(config_file)

        # Verify file was created and has correct content
        assert config_file.exists()
        loaded_config = PyQCConfig.load_from_file(config_file)
        assert loaded_config.line_length == 100
        assert loaded_config.type_checker == "mypy"
        assert loaded_config.parallel is False

    def test_save_to_yaml(self, tmp_path: Path) -> None:
        """Test saving config to YAML file."""
        config = PyQCConfig(line_length=120, type_checker="mypy", parallel=True)
        config_file = tmp_path / "saved.yaml"

        config.save(config_file)

        # Verify file was created and has correct content
        assert config_file.exists()
        loaded_config = PyQCConfig.load_from_file(config_file)
        assert loaded_config.line_length == 120
        assert loaded_config.type_checker == "mypy"
        assert loaded_config.parallel is True

    def test_save_unsupported_format(self, tmp_path: Path) -> None:
        """Test saving to unsupported file format."""
        config = PyQCConfig()
        config_file = tmp_path / "config.json"

        with pytest.raises(ValueError, match="Unsupported config file format"):
            config.save(config_file)


class TestConfigDiscovery:
    """Test configuration file discovery."""

    def test_find_config_in_current_dir(self, tmp_path: Path) -> None:
        """Test finding config in current directory."""
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text("[tool.pyqc]\nline-length = 88")

        found_config = PyQCConfig.find_config_file(tmp_path)
        assert found_config == config_file

    def test_find_config_in_parent_dir(self, tmp_path: Path) -> None:
        """Test finding config in parent directory."""
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text("[tool.pyqc]\nline-length = 88")

        subdir = tmp_path / "subdir"
        subdir.mkdir()

        found_config = PyQCConfig.find_config_file(subdir)
        assert found_config == config_file

    def test_find_yaml_config_priority(self, tmp_path: Path) -> None:
        """Test YAML config has priority over TOML."""
        toml_config = tmp_path / "pyproject.toml"
        toml_config.write_text("[tool.pyqc]\nline-length = 88")

        yaml_config = tmp_path / ".pyqc.yaml"
        yaml_config.write_text("pyqc:\n  line-length: 100")

        found_config = PyQCConfig.find_config_file(tmp_path)
        assert found_config == yaml_config

    def test_no_config_found(self, tmp_path: Path) -> None:
        """Test when no config file is found."""
        found_config = PyQCConfig.find_config_file(tmp_path)
        assert found_config is None

    def test_load_with_discovery(self, tmp_path: Path) -> None:
        """Test loading config with automatic discovery."""
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text("""
[tool.pyqc]
line-length = 95
type-checker = "mypy"
""")

        config = PyQCConfig.load(tmp_path)
        assert config.line_length == 95
        assert config.type_checker == "mypy"

    def test_load_with_no_config_found(self, tmp_path: Path) -> None:
        """Test loading with no config file found returns defaults."""
        config = PyQCConfig.load(tmp_path)

        # Should return default config
        assert config.line_length == 88
        assert config.type_checker == "mypy"
        assert config.parallel is True
