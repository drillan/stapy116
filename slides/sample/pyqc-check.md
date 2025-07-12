$ uv run pyqc check
🔍 Checking 22 Python file(s)...
  ✅ sample_project/example.py: 0 issues
  ✅ scripts/pyqc_hooks.py: 0 issues
  ✅ src/pyqc/__init__.py: 0 issues
  ✅ src/pyqc/__main__.py: 0 issues
  ✅ src/pyqc/checkers/__init__.py: 0 issues
  ✅ src/pyqc/checkers/ruff_checker.py: 0 issues
  ✅ src/pyqc/checkers/type_checker.py: 0 issues
  ✅ src/pyqc/cli.py: 0 issues
  ✅ src/pyqc/config.py: 0 issues
  ✅ src/pyqc/core.py: 0 issues
  ✅ src/pyqc/utils/__init__.py: 0 issues
  ✅ src/pyqc/utils/logger.py: 0 issues
  ⚠️ tests/e2e/test_e2e.py: 1 issues
  ⚠️ tests/integration/test_cli.py: 3 issues
  ⚠️ tests/integration/test_parallel_execution.py: 3 issues
  ✅ tests/unit/test_cli_utils.py: 0 issues
  ✅ tests/unit/test_config.py: 0 issues
  ✅ tests/unit/test_core.py: 0 issues
  ✅ tests/unit/test_main.py: 0 issues
  ⚠️ tests/unit/test_ruff_checker.py: 1 issues
  ⚠️ tests/unit/test_type_checker.py: 2 issues
  ✅ tests/unit/test_utils.py: 0 issues
PyQC Report
==================================================
Files checked: 22
Successful: 22
Total issues: 10

Issues by severity:
  error: 10

Issues found:
------------------------------
tests/e2e/test_e2e.py:13: error: Untyped decorator makes function "sample_project" untyped
tests/integration/test_cli.py:16: error: Untyped decorator makes function "runner" untyped
tests/integration/test_cli.py:22: error: Untyped decorator makes function "sample_python_file"
untyped
tests/integration/test_cli.py:36: error: Untyped decorator makes function "sample_project" untyped
tests/integration/test_parallel_execution.py:18: error: Untyped decorator makes function
"temp_project" untyped
tests/integration/test_parallel_execution.py:40: error: Untyped decorator makes function
"config_parallel" untyped
tests/integration/test_parallel_execution.py:48: error: Untyped decorator makes function
"config_sequential" untyped
tests/unit/test_ruff_checker.py:274: error: Untyped decorator makes function
"test_real_ruff_execution" untyped
tests/unit/test_type_checker.py:325: error: Untyped decorator makes function
"test_real_mypy_execution" untyped
tests/unit/test_type_checker.py:349: error: Untyped decorator makes function
"test_real_ty_execution" untyped