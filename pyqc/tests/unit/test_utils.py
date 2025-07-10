"""Unit tests for utility modules."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from pyqc.utils.logger import setup_logger


class TestSetupLogger:
    """Test logger setup."""

    def test_setup_logger_default_level(self) -> None:
        """Test setting up logger with default level."""
        logger = setup_logger("test")
        assert logger.level == logging.INFO
        assert logger.name == "test"

    def test_setup_logger_custom_level(self) -> None:
        """Test setting up logger with custom level."""
        logger = setup_logger("test", level="DEBUG")
        assert logger.level == logging.DEBUG

    def test_setup_logger_with_file_handler(self, tmp_path: Path) -> None:
        """Test setting up logger with file handler."""
        log_file = tmp_path / "test.log"
        logger = setup_logger("test", log_file=log_file)

        # Check that file handler is added
        file_handlers = [
            h for h in logger.handlers if isinstance(h, logging.FileHandler)
        ]
        assert len(file_handlers) == 1
        assert file_handlers[0].baseFilename == str(log_file)

    def test_setup_logger_no_rich_handler(self) -> None:
        """Test setting up logger without rich handler."""
        logger = setup_logger("test", use_rich=False)

        # Check that no rich handler is added
        rich_handlers = [
            h for h in logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert len(rich_handlers) == 1

    def test_setup_logger_with_rich_handler(self) -> None:
        """Test setting up logger with rich handler."""
        logger = setup_logger("test", use_rich=True)

        # Check that rich handler is added
        rich_handlers = [h for h in logger.handlers if hasattr(h, "console")]
        assert len(rich_handlers) >= 1

    def test_setup_logger_warning_level(self) -> None:
        """Test setting up logger with warning level."""
        logger = setup_logger("test", level="WARNING")
        assert logger.level == logging.WARNING

    def test_setup_logger_error_level(self) -> None:
        """Test setting up logger with error level."""
        logger = setup_logger("test", level="ERROR")
        assert logger.level == logging.ERROR

    def test_setup_logger_invalid_level(self) -> None:
        """Test setting up logger with invalid level raises AttributeError."""
        with pytest.raises(AttributeError):
            setup_logger("test", level="INVALID")

    def test_setup_logger_multiple_calls_same_name(self) -> None:
        """Test that multiple calls with same name return same logger."""
        logger1 = setup_logger("test")
        logger2 = setup_logger("test")
        assert logger1 is logger2

    def test_setup_logger_different_names(self) -> None:
        """Test that different names return different loggers."""
        logger1 = setup_logger("test1")
        logger2 = setup_logger("test2")
        assert logger1 is not logger2
        assert logger1.name != logger2.name
