# SPDX-License-Identifier: MIT

from __future__ import annotations  # Future-proof type annotations

# Standard library imports
import logging  # For type hinting only; actual logging configuration is handled in LoggerManager
import os  # For directory and file path management
from datetime import datetime  # For timestamping log files


class LoggerManager:
    """Manage log folder creation and logging configuration.

    This class encapsulates all logic related to setting up logging for an
    application. It ensures a log directory exists, creates a timestamped
    log file, and configures both console and file logging handlers.

    Attributes:
        output_folder (str): Base folder where the log directory will be created.
        log_folder (str): Absolute path to the created log directory.
        log_file (str): Absolute path to the timestamped log file.

    """

    def __init__(self, output_folder: str, enable_logging: bool = True) -> None:
        """Initialize the LoggerManager.

        Args:
            output_folder (str): Path to the application's output directory.
            enable_logging (bool): Whether to enable logging.


        """
        self.output_folder = output_folder
        self.log_folder = self._ensure_log_folder()
        self.log_file = self._create_log_file()
        self.enable_logging = enable_logging
        self.logging_message = self._configure_logging()

    # -------------------------------------------------------------------------
    # Folder creation
    # -------------------------------------------------------------------------
    def _ensure_log_folder(self) -> str:
        """Ensure that the log folder exists.

        Creates a ``log`` subdirectory inside ``output_folder`` if it does not
        already exist.

        Returns:
            str: Absolute path to the log folder.

        """
        log_folder = os.path.join(self.output_folder, "log")
        os.makedirs(log_folder, exist_ok=True)
        return log_folder

    # -------------------------------------------------------------------------
    # Log file creation
    # -------------------------------------------------------------------------
    def _create_log_file(self) -> str:
        """Create a timestamped log file path.

        Returns:
            str: Absolute path to the new log file.

        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.log_folder, f"{timestamp}_log.log")

    # -------------------------------------------------------------------------
    # Logging configuration
    # -------------------------------------------------------------------------
    def _configure_logging(self) -> None:
        """Configure logging for both console and file output.

        Sets up:
            - A file handler that logs all messages (DEBUG and above).
            - A console handler that logs INFO and above.

        Existing handlers are cleared to avoid duplicate logs.
        """
        logger = logging.getLogger()
        logger.handlers.clear()
        logger.setLevel(logging.DEBUG)

        # File handler — logs EVERYTHING
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )

        # Console handler — logs INFO and above
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        if self.enable_logging:
            logging.info(f"Logging to file: {self.log_file}")
