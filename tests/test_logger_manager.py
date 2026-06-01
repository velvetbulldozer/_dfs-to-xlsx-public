"""Tests for the LoggerManager class.

This suite verifies that:
- A log directory is created automatically inside the output folder
- Log files are named using a timestamp and created correctly
- Logger handlers (file + console) are configured with correct levels
- The file handler writes to the expected log file path
"""

import logging
import os
from datetime import datetime
from unittest.mock import patch

from src.dfs_to_xlsx.modules.logger_manager import LoggerManager


def test_logger_manager_creates_log_folder(tmp_path):
    """Test that LoggerManager creates the log folder and log file."""
    output_folder = tmp_path
    log_dir = os.path.join(output_folder, "log")

    # Patch datetime.datetime.now() safely
    with patch("src.dfs_to_xlsx.modules.logger_manager.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 1, 1, 12, 0, 0)
        mock_dt.strftime = datetime.strftime  # keep real strftime

        lm = LoggerManager(str(output_folder))

    # Folder should exist
    assert os.path.isdir(log_dir)

    # Log file should exist and match expected name
    expected_log_file = os.path.join(log_dir, "20260101_120000_log.log")
    assert lm.log_file == expected_log_file
    assert os.path.isfile(expected_log_file)


def test_logger_manager_configures_handlers(tmp_path):
    """Test that LoggerManager configures file and console handlers correctly."""
    output_folder = tmp_path

    # Freeze timestamp for deterministic file naming
    with patch("src.dfs_to_xlsx.modules.logger_manager.datetime") as mock_dt:
        mock_dt.now.return_value = datetime(2026, 1, 1, 12, 0, 0)
        mock_dt.strftime = datetime.strftime

        LoggerManager(str(output_folder))

    logger = logging.getLogger()

    # Should have exactly 2 handlers: file + console
    assert len(logger.handlers) == 2

    # Identify handlers
    file_handler = next(
        h for h in logger.handlers if isinstance(h, logging.FileHandler)
    )
    console_handler = next(
        h
        for h in logger.handlers
        if isinstance(h, logging.StreamHandler)
        and not isinstance(h, logging.FileHandler)
    )

    # Verify log levels
    assert file_handler.level == logging.DEBUG
    assert console_handler.level == logging.INFO

    # File handler should write to the expected file
    log_dir = os.path.join(output_folder, "log")
    expected_log_file = os.path.join(log_dir, "20260101_120000_log.log")
    assert file_handler.baseFilename == expected_log_file
