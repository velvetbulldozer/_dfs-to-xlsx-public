# SPDX-License-Identifier: MIT

from __future__ import annotations  # Future-proof type annotations

# Standard library imports
import logging  # For logging exceptions during cleaning operations
from typing import Any  # For type hints in cleaning methods

# Third-party imports
import pandas as pd  # For DataFrame manipulation in the cleaning process


class DataCleaner:
    """Utility class for normalizing and cleaning DataFrame values.

    This class provides safe, reusable helpers for cleaning Python collections,
    stringified collections, and general string normalization. It is designed
    to be used by the Excel export pipeline but can be reused independently.

    Methods:
        safe_str_strip: Safely strip whitespace from strings.
        clean_collections: Normalize Python collections and stringified collections.
        clean_dataframe: Apply cleaning to all values in a DataFrame.

    """

    # ------------------------------------------------------------------
    # Basic string cleaning
    # ------------------------------------------------------------------
    def safe_str_strip(self, value: Any) -> Any:
        """Safely strip whitespace from strings.

        Args:
            value (Any): Input value.

        Returns:
            Any: Stripped string or original value if not a string.

        """
        try:
            if isinstance(value, str):
                return value.strip()

            return value

        except Exception:
            return value

    # ------------------------------------------------------------------
    # Collection normalization
    # ------------------------------------------------------------------
    def clean_collections(self, value: Any) -> Any:
        """Normalize Python collections and stringified collections.

        Converts sets, lists, tuples, and dicts into comma-separated strings.
        Also handles stringified versions of these collections.

        Args:
            value (Any): Input value.

        Returns:
            Any: Cleaned and normalized value.

        """
        try:
            # Native Python collections
            if isinstance(value, (set, tuple, list)):
                return ", ".join(map(str, value))

            if isinstance(value, dict):
                return ", ".join(f"{k}: {v}" for k, v in value.items())

            # Stringified collections
            if isinstance(value, str):
                stripped = value.strip()

                if stripped.startswith("[") and stripped.endswith("]"):
                    return stripped[1:-1].replace("'", "").replace('"', "").strip()

                if stripped.startswith("{") and stripped.endswith("}"):
                    return stripped[1:-1].replace("'", "").replace('"', "").strip()

                if stripped.startswith("(") and stripped.endswith(")"):
                    return stripped[1:-1].replace("'", "").replace('"', "").strip()

            # Fallback: safe strip
            return self.safe_str_strip(value)

        except Exception as e:
            logging.exception(f"Error cleaning value: {value} — {e}")
            return value

    # ------------------------------------------------------------------
    # DataFrame cleaning
    # ------------------------------------------------------------------
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean all values in a DataFrame.

        Applies ``clean_collections`` to every cell in the DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame.

        Returns:
            pd.DataFrame: Cleaned DataFrame.

        """
        return df.apply(lambda col: col.map(self.clean_collections))
