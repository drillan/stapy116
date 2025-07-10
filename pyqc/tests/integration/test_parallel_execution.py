"""Integration tests for parallel execution functionality."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from pyqc.config import PyQCConfig
from pyqc.core import PyQCRunner


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create a temporary project with multiple Python files."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create multiple Python files
    files = []
    for i in range(5):
        file_path = project_dir / f"file_{i}.py"
        file_path.write_text(f"""
def function_{i}():
    return {i}

if __name__ == "__main__":
    print(function_{i}())
""")
        files.append(file_path)

    return project_dir


@pytest.fixture
def config_parallel() -> PyQCConfig:
    """Configuration with parallel execution enabled."""
    config = PyQCConfig()
    config.parallel = True
    return config


@pytest.fixture
def config_sequential() -> PyQCConfig:
    """Configuration with parallel execution disabled."""
    config = PyQCConfig()
    config.parallel = False
    return config


class TestParallelExecution:
    """Test parallel execution functionality."""

    @patch("subprocess.run")
    def test_parallel_check_multiple_files(
        self, mock_run: Mock, temp_project: Path, config_parallel: PyQCConfig
    ) -> None:
        """Test parallel checking of multiple files."""
        # Mock subprocess calls
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check"], returncode=0, stdout="", stderr=""
        )

        runner = PyQCRunner(config_parallel)
        files = list(temp_project.glob("*.py"))

        start_time = time.time()
        results = runner.check_files_parallel(files)
        execution_time = time.time() - start_time

        # Verify results
        assert len(results) == 5
        assert all(result.success for result in results)
        assert all(result.path in files for result in results)

        # Results should be sorted by path
        sorted_paths = sorted(files, key=str)
        assert [result.path for result in results] == sorted_paths

        # Should be reasonably fast (parallel execution)
        assert execution_time < 2.0  # Should complete in under 2 seconds

    @patch("subprocess.run")
    def test_sequential_vs_parallel_performance(
        self, mock_run: Mock, temp_project: Path
    ) -> None:
        """Test performance difference between sequential and parallel execution."""

        # Mock subprocess calls with slight delay
        def slow_subprocess(
            *args: Any, **kwargs: Any
        ) -> subprocess.CompletedProcess[str]:
            time.sleep(0.1)  # Simulate 100ms per file
            return subprocess.CompletedProcess(
                args=["ruff", "check"], returncode=0, stdout="", stderr=""
            )

        mock_run.side_effect = slow_subprocess

        files = list(temp_project.glob("*.py"))

        # Test sequential execution
        config_seq = PyQCConfig()
        config_seq.parallel = False
        runner_seq = PyQCRunner(config_seq)

        start_time = time.time()
        results_seq = runner_seq.check_files_parallel(files)
        seq_time = time.time() - start_time

        # Test parallel execution
        config_par = PyQCConfig()
        config_par.parallel = True
        runner_par = PyQCRunner(config_par)

        start_time = time.time()
        results_par = runner_par.check_files_parallel(files)
        par_time = time.time() - start_time

        # Verify same results
        assert len(results_seq) == len(results_par) == 5

        # Parallel should be faster (with some tolerance)
        assert par_time < seq_time * 0.8  # At least 20% faster

    @patch("subprocess.run")
    def test_parallel_execution_with_failures(
        self, mock_run: Mock, temp_project: Path, config_parallel: PyQCConfig
    ) -> None:
        """Test parallel execution handles failures gracefully."""

        # Mock some files to fail
        def mixed_subprocess(
            *args: Any, **kwargs: Any
        ) -> subprocess.CompletedProcess[str]:
            if "file_2.py" in str(args[0]):
                return subprocess.CompletedProcess(
                    args=["ruff", "check"],
                    returncode=1,
                    stdout=json.dumps(
                        [
                            {
                                "filename": str(args[0][-1]),
                                "line": 1,
                                "column": 1,
                                "message": "Test error",
                                "code": "E999",
                                "severity": "error",
                            }
                        ]
                    ),
                    stderr="",
                )
            else:
                return subprocess.CompletedProcess(
                    args=["ruff", "check"], returncode=0, stdout="", stderr=""
                )

        mock_run.side_effect = mixed_subprocess

        runner = PyQCRunner(config_parallel)
        files = list(temp_project.glob("*.py"))

        results = runner.check_files_parallel(files)

        # Verify all files processed
        assert len(results) == 5

        # Check that one file has issues
        files_with_issues = [r for r in results if r.issues]
        assert len(files_with_issues) == 1

        # Check the specific error file
        error_result = next(r for r in results if "file_2.py" in str(r.path))
        assert (
            len(error_result.issues) >= 1
        )  # May have multiple issues from different checkers

        # Check that our specific error is in there
        error_messages = [issue.message for issue in error_result.issues]
        assert "Test error" in error_messages

    @patch("subprocess.run")
    def test_parallel_fix_multiple_files(
        self, mock_run: Mock, temp_project: Path, config_parallel: PyQCConfig
    ) -> None:
        """Test parallel fixing of multiple files."""
        # Mock subprocess calls
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "format"], returncode=0, stdout="", stderr=""
        )

        runner = PyQCRunner(config_parallel)
        files = list(temp_project.glob("*.py"))

        results = runner.fix_files_parallel(files, dry_run=False)

        # Verify results
        assert len(results) == 5
        assert all(result.success for result in results)

        # Check that ruff format was called for each file
        assert mock_run.call_count == 5

    @patch("subprocess.run")
    def test_parallel_execution_exception_handling(
        self, mock_run: Mock, temp_project: Path, config_parallel: PyQCConfig
    ) -> None:
        """Test parallel execution handles exceptions properly."""

        # Mock subprocess to raise exception for one file
        def exception_subprocess(
            *args: Any, **kwargs: Any
        ) -> subprocess.CompletedProcess[str]:
            if "file_1.py" in str(args[0]):
                raise RuntimeError("Simulated error")
            else:
                return subprocess.CompletedProcess(
                    args=["ruff", "check"], returncode=0, stdout="", stderr=""
                )

        mock_run.side_effect = exception_subprocess

        runner = PyQCRunner(config_parallel)
        files = list(temp_project.glob("*.py"))

        results = runner.check_files_parallel(files)

        # Should still return results for all files
        assert len(results) == 5

        # One file should have failed
        failed_results = [r for r in results if not r.success]
        assert len(failed_results) == 1

        # Check the failed result
        failed_result = failed_results[0]
        assert "file_1.py" in str(failed_result.path)
        assert "Simulated error" in failed_result.error_message


class TestPerformanceMetrics:
    """Test performance metrics functionality."""

    @patch("subprocess.run")
    def test_performance_metrics_calculation(
        self, mock_run: Mock, temp_project: Path, config_parallel: PyQCConfig
    ) -> None:
        """Test performance metrics are calculated correctly."""
        # Mock subprocess calls
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check"], returncode=0, stdout="", stderr=""
        )

        runner = PyQCRunner(config_parallel)
        files = list(temp_project.glob("*.py"))

        results = runner.check_files_parallel(files)
        metrics = runner.get_performance_metrics(results)

        # Verify metrics structure
        assert "total_files" in metrics
        assert "successful_files" in metrics
        assert "failed_files" in metrics
        assert "total_execution_time" in metrics
        assert "average_time_per_file" in metrics
        assert "parallel_enabled" in metrics
        assert "files_per_second" in metrics

        # Verify values
        assert metrics["total_files"] == 5
        assert metrics["successful_files"] == 5
        assert metrics["failed_files"] == 0
        assert metrics["parallel_enabled"] is True
        assert metrics["total_execution_time"] > 0
        assert metrics["average_time_per_file"] > 0
        assert metrics["files_per_second"] > 0

    @patch("subprocess.run")
    def test_performance_metrics_with_failures(
        self, mock_run: Mock, temp_project: Path, config_parallel: PyQCConfig
    ) -> None:
        """Test performance metrics with some failures."""

        # Mock some files to fail
        def mixed_subprocess(
            *args: Any, **kwargs: Any
        ) -> subprocess.CompletedProcess[str]:
            if "file_2.py" in str(args[0]):
                raise RuntimeError("Simulated error")
            else:
                return subprocess.CompletedProcess(
                    args=["ruff", "check"], returncode=0, stdout="", stderr=""
                )

        mock_run.side_effect = mixed_subprocess

        runner = PyQCRunner(config_parallel)
        files = list(temp_project.glob("*.py"))

        results = runner.check_files_parallel(files)
        metrics = runner.get_performance_metrics(results)

        # Verify metrics with failures
        assert metrics["total_files"] == 5
        assert metrics["successful_files"] == 4
        assert metrics["failed_files"] == 1
        assert metrics["total_execution_time"] > 0


class TestWorkerConfiguration:
    """Test worker configuration for parallel execution."""

    @patch("subprocess.run")
    def test_custom_max_workers(
        self, mock_run: Mock, temp_project: Path, config_parallel: PyQCConfig
    ) -> None:
        """Test custom max_workers parameter."""
        # Mock subprocess calls
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check"], returncode=0, stdout="", stderr=""
        )

        runner = PyQCRunner(config_parallel)
        files = list(temp_project.glob("*.py"))

        # Test with custom max_workers
        results = runner.check_files_parallel(files, max_workers=2)

        # Should still process all files
        assert len(results) == 5
        assert all(result.success for result in results)

    @patch("subprocess.run")
    def test_auto_worker_scaling(
        self, mock_run: Mock, temp_project: Path, config_parallel: PyQCConfig
    ) -> None:
        """Test automatic worker scaling based on file count."""
        # Mock subprocess calls
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ruff", "check"], returncode=0, stdout="", stderr=""
        )

        runner = PyQCRunner(config_parallel)

        # Test with single file (should use 1 worker)
        single_file = [list(temp_project.glob("*.py"))[0]]
        results = runner.check_files_parallel(single_file)
        assert len(results) == 1

        # Test with multiple files (should use multiple workers)
        all_files = list(temp_project.glob("*.py"))
        results = runner.check_files_parallel(all_files)
        assert len(results) == 5
