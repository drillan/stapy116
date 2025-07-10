"""Unit tests for CLI interface."""

from __future__ import annotations

from pathlib import Path

from pyqc.cli import find_python_files, load_config


class TestFindPythonFiles:
    """Test finding Python files."""

    def test_find_single_file(self, tmp_path: Path) -> None:
        """Test finding a single Python file."""
        py_file = tmp_path / "test.py"
        py_file.write_text("print('hello')")

        result = find_python_files(py_file)
        assert result == [py_file]

    def test_find_non_python_file(self, tmp_path: Path) -> None:
        """Test handling non-Python files."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("hello")

        result = find_python_files(txt_file)
        assert result == []

    def test_find_directory_with_python_files(self, tmp_path: Path) -> None:
        """Test finding Python files in a directory."""
        (tmp_path / "file1.py").write_text("print('file1')")
        (tmp_path / "file2.py").write_text("print('file2')")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file3.py").write_text("print('file3')")

        result = find_python_files(tmp_path)
        assert len(result) == 3
        assert all(f.suffix == ".py" for f in result)

    def test_find_directory_excludes_common_dirs(self, tmp_path: Path) -> None:
        """Test that common directories are excluded."""
        (tmp_path / "good.py").write_text("print('good')")

        # Create files in excluded directories
        for exclude_dir in [
            ".git",
            "__pycache__",
            ".pytest_cache",
            ".venv",
            "venv",
            "node_modules",
        ]:
            (tmp_path / exclude_dir).mkdir()
            (tmp_path / exclude_dir / "bad.py").write_text("print('bad')")

        result = find_python_files(tmp_path)
        assert len(result) == 1
        assert result[0].name == "good.py"

    def test_find_nonexistent_path(self, tmp_path: Path) -> None:
        """Test handling non-existent paths."""
        nonexistent = tmp_path / "nonexistent"
        result = find_python_files(nonexistent)
        assert result == []


class TestLoadConfig:
    """Test configuration loading."""

    def test_load_config_with_pyproject_toml(self, tmp_path: Path) -> None:
        """Test loading config from pyproject.toml."""
        pyproject_toml = tmp_path / "pyproject.toml"
        pyproject_toml.write_text("""
[tool.pyqc]
line_length = 120
type_checker = "ty"

[tool.pyqc.ruff]
extend_select = ["I"]
        """)

        config = load_config(tmp_path)
        assert config.line_length == 120
        assert config.type_checker == "ty"
        assert config.ruff.extend_select == ["I"]

    def test_load_config_with_pyqc_yaml(self, tmp_path: Path) -> None:
        """Test loading config from .pyqc.yaml."""
        pyqc_yaml = tmp_path / ".pyqc.yaml"
        pyqc_yaml.write_text("""
pyqc:
  line_length: 100
  type_checker: "mypy"
  ruff:
    extend_select: ["N", "UP"]
        """)

        config = load_config(tmp_path)
        assert config.line_length == 100
        assert config.type_checker == "mypy"
        assert config.ruff.extend_select == ["N", "UP"]

    def test_load_config_defaults(self, tmp_path: Path) -> None:
        """Test loading default config when no config file exists."""
        config = load_config(tmp_path)
        assert config.line_length == 88
        assert config.type_checker == "mypy"
        # Default config includes some extend_select rules
        assert isinstance(config.ruff.extend_select, list)

    def test_load_config_searches_parent_dirs(self, tmp_path: Path) -> None:
        """Test that config loading searches parent directories."""
        pyproject_toml = tmp_path / "pyproject.toml"
        pyproject_toml.write_text("""
[tool.pyqc]
line_length = 90
        """)

        # Create a subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        config = load_config(subdir)
        assert config.line_length == 90

    def test_load_config_pyproject_toml_takes_precedence(self, tmp_path: Path) -> None:
        """Test that .pyqc.yaml takes precedence over pyproject.toml."""
        pyproject_toml = tmp_path / "pyproject.toml"
        pyproject_toml.write_text("""
[tool.pyqc]
line_length = 100
        """)

        pyqc_yaml = tmp_path / ".pyqc.yaml"
        pyqc_yaml.write_text("""
pyqc:
  line_length: 120
        """)

        config = load_config(tmp_path)
        assert config.line_length == 120
