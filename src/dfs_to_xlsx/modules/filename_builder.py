# SPDX-License-Identifier: MIT

from __future__ import annotations  # Future-proof type annotations

# Standard library imports
import os  # File and path operations
from datetime import datetime  # Timestamp generation


class FilenameBuilder:
    """Generates timestamped filenames for Excel exports.

    This class encapsulates all logic related to constructing output
    filenames, including timestamp generation and index-based suffixes.

    Attributes:
        base_filename (str): Base name used for all generated files.
        output_folder (str): Absolute path to the output directory.

    """

    def __init__(self, base_filename: str, output_folder: str) -> None:
        """Initialize the filename builder.

        Args:
            base_filename (str): Base name for exported files.
            output_folder (str): Directory where files will be written.

        """
        self.base_filename = os.path.basename(base_filename)
        self.output_folder = output_folder

    def timestamp(self) -> str:
        """Return a timestamp in YYYYMMDD_HHMMSS format.

        Returns:
            str: Timestamp string.

        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def build(self, index: int) -> str:
        """Construct a full output filename.

        Args:
            index (int): File index (1 for first file, 2+ for split files).

        Returns:
            str: Absolute path to the generated filename.

        """
        ts = self.timestamp()

        if index == 1:
            name = f"{ts}_{self.base_filename}.xlsx"

        else:
            name = f"{ts}_{self.base_filename}_{index}.xlsx"

        return os.path.join(self.output_folder, name)
