# SPDX-License-Identifier: MIT

from __future__ import annotations  # Future-proof type annotations

# Standard library imports
import logging  # For logging post-processing actions and results
import os  # For file handling and path operations
import zipfile  # For compressing large Excel files into ZIP archives


class PostProcessor:
    """Handles post-processing of generated Excel files.

    This class performs size checks, ZIP compression, and cleanup of
    exported Excel files. It is designed to be used by the
    XlsxDataFrameWriter after each file is written.

    Attributes:
        max_size_mb (int): Maximum allowed file size in megabytes before
            compression is triggered.

    """

    GREEN = "\033[32m"
    RED = "\033[31m"
    RESET = "\033[0m"

    def __init__(self, max_size_mb: int) -> None:
        """Initialize the PostProcessor.

        Args:
            max_size_mb (int): Maximum allowed file size in megabytes.

        """
        self.max_size_mb = max_size_mb

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def process(self, filename: str) -> dict:
        """Perform post-processing on an exported Excel file.

        This method checks the file size and, if it exceeds the configured
        limit, compresses it into a ZIP archive and deletes the original
        file. If the file is within limits, it is left untouched.

        Args:
            filename (str): Absolute path to the Excel file to process.

        Returns:
            dict: A status dictionary describing the result. Keys include:
                - "status": Either "ok" or "zipped".
                - "file_path": Path to the saved file (if not zipped).
                - "zip_path": Path to the ZIP archive (if zipped).
                - "size_mb": File size in megabytes (if not zipped).
                - "original_size_mb": Original size before zipping.

        """
        size_mb = os.path.getsize(filename) / (1024 * 1024)

        if size_mb > self.max_size_mb:
            zip_path = self._zip_file(filename)

            print(f"{self.GREEN}Zipped: {zip_path}{self.RESET}")
            logging.warning(f"{filename} exceeded {self.max_size_mb} MB → zipped")

            # Delete original file
            try:
                os.remove(filename)
                print(f"{self.RED}Deleted original: {filename}{self.RESET}")
                logging.info(f"Deleted original file after zipping: {filename}")
            except Exception as e:
                print(
                    f"{self.RED}Failed to delete original: {filename} ({e}){self.RESET}"
                )
                logging.exception(f"Failed to delete original file: {filename} — {e}")

            return {
                "status": "zipped",
                "zip_path": zip_path,
                "original_size_mb": size_mb,
            }

        # File is within size limits
        print(f"{self.GREEN}Saved: {filename} ({size_mb:.2f} MB){self.RESET}")
        logging.info(f"{filename} OK ({size_mb:.2f} MB)")

        return {"status": "ok", "file_path": filename, "size_mb": size_mb}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _zip_file(self, file_path: str) -> str:
        """Compress a file into a ZIP archive.

        Args:
            file_path (str): Path to the file to compress.

        Returns:
            str: Path to the created ZIP archive.

        """
        zip_path = file_path.replace(".xlsx", ".zip")

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(file_path, arcname=os.path.basename(file_path))

        return zip_path
