# SPDX-License-Identifier: MIT

from __future__ import annotations  # Future-proof type annotations

# Standard library imports
import logging  # For logging events during DataFrame registration
from typing import Any  # For type hints in add_dfs method

# Third-party imports
import pandas as pd  # For DataFrame type hints and manipulation


class DataFrameRegistry:
    """Registry for storing DataFrames with sanitized, unique sheet names.

    This class encapsulates the logic for adding single or multiple DataFrames
    to an export queue. It ensures that sheet names comply with Excel's naming
    rules, resolves duplicates, and logs all relevant events.

    The registry does not perform any cleaning or writing; it only manages
    DataFrame storage and sheet name validation.
    """

    def __init__(
        self,
        sanitizer: str,
        enable_logging: bool = True,
    ) -> None:
        """Initialize the registry.

        Args:
            sanitizer (callable): Function that sanitizes sheet names.
            enable_logging (bool): Whether to log registry operations.

        """
        self._sanitize_sheet_name = sanitizer
        self.dataframes = {}
        self.enable_logging = enable_logging

    # ------------------------------------------------------------------
    # Add a single DataFrame
    # ------------------------------------------------------------------
    def add_df(self, df: pd.DataFrame, sheet_name: str) -> None:
        """Register a DataFrame under a sanitized sheet name.

        Args:
            df (pd.DataFrame): DataFrame to register.
            sheet_name (str): Desired sheet name before sanitization.

        """
        existing = set(self.dataframes.keys())
        sanitized = self._sanitize_sheet_name(sheet_name, existing)

        if sanitized != sheet_name and self.enable_logging:
            logging.warning(
                f"Sheet name '{sheet_name}' sanitized to '{sanitized}' "
                "to comply with Excel naming rules."
            )

        if sanitized in self.dataframes:
            if self.enable_logging:
                logging.error(f"Sheet '{sanitized}' already exists — skipping.")
            return  # Prevent overwrite

        if self.enable_logging:
            logging.info(
                f"Adding DataFrame to sheet '{sanitized}' ({df.shape[0]} rows)"
            )

        self.dataframes[sanitized] = df

    # ------------------------------------------------------------------
    # Add multiple DataFrames
    # ------------------------------------------------------------------
    def add_dfs(self, data: Any) -> None:
        """Add multiple DataFrames at once.

        Supports:
            - dict[str, pd.DataFrame]
            - list[tuple[str, pd.DataFrame]]
            - list[pd.DataFrame] (auto-named)

        Args:
            data: Collection of DataFrames to add.

        Returns:
            None.

        Raises:
            TypeError: If the input format is not supported.

        """
        # Case 1: dict of {sheet_name: df}
        if isinstance(data, dict):
            if self.enable_logging and self.enable_logging:
                logging.info(f"Adding {len(data)} DataFrames from dict")
            for sheet_name, df in data.items():
                self.add_df(df, sheet_name)
            return

        # Case 2: list of (sheet_name, df)
        if isinstance(data, list) and all(
            isinstance(item, tuple) and len(item) == 2 for item in data
        ):
            if self.enable_logging:
                logging.info(f"Adding {len(data)} DataFrames from list of tuples")
            for sheet_name, df in data:
                self.add_df(df, sheet_name)
            return

        # Case 3: list of DataFrames → auto-named
        if isinstance(data, list) and all(isinstance(df, pd.DataFrame) for df in data):
            if self.enable_logging:
                logging.info(f"Adding {len(data)} DataFrames with auto-named sheets")
            for idx, df in enumerate(data, start=1):
                sheet_name = f"Sheet_{idx}"
                self.add_df(df, sheet_name)
            return

        raise TypeError(
            "add_dfs() expects dict, list of (name, df) tuples, or list of dfs."
        )

    # ------------------------------------------------------------------
    # Utility: List registered sheet names
    # ------------------------------------------------------------------
    def list_sheet_names(self, verbose: bool = False) -> list[str] | None:
        """Return or print the registered sheet names.

        Args:
            verbose (bool):
                If True, prints the sheet names with numbering and returns None.
                If False, returns the list of sheet names.

        Returns:
            list[str] | None: List of sheet names if verbose=False, otherwise None.

        """
        names = list(self.dataframes.keys())

        if verbose:
            logging.info("Registered sheet names:")
            for idx, name in enumerate(names, start=1):
                print(f"{idx}. {name}")
            return None

        return names
