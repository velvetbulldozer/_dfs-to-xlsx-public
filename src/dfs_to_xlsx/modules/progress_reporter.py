# SPDX-License-Identifier: MIT

from __future__ import annotations  # Future-proof type annotations

# Standard library imports
# Third-party imports
import pandas as pd  # For type hinting DataFrames; actual DataFrame handling is done in the writer class
from num2words import (
    num2words,  # For converting batch counts and total DataFrame counts to human-readable words
)


class ProgressReporter:
    """Report progress to the user during Excel export.

    This class encapsulates all user-facing messaging related to the export
    process, including sheet-level progress, batch counts, hit-list status,
    word-wrap status, and total DataFrame count. It keeps the writer class
    focused solely on writing logic.
    """

    def __init__(
        self,
        enable_hit_list: bool,
        hit_list: list[str] | None,
        check_cols: list[str] | None,
        enable_word_wrap: bool,
        dataframes_ref: dict[str, pd.DataFrame],
    ) -> None:
        """Initialize the progress reporter.

        Args:
            enable_hit_list (bool):
                Whether hit-list conditional formatting is enabled.
            hit_list (list[str] | None):
                List of words to highlight. May be empty or None.
            check_cols (list[str] | None):
                Columns where hit-list matching should be applied.
            enable_word_wrap (bool):
                Whether word wrapping is enabled for eligible sheets.
            dataframes_ref (dict[str, pd.DataFrame]):
                Reference to the registry's DataFrame dictionary. Used to
                determine total sheet count for reporting.

        """
        self.enable_hit_list = enable_hit_list
        self.hit_list = hit_list or []
        self.check_cols = check_cols or []
        self.enable_word_wrap = enable_word_wrap
        self.dataframes_ref = dataframes_ref
        self.last_sheet_message = ""

    # ------------------------------------------------------------------
    # Main reporting method
    # ------------------------------------------------------------------
    def report(self, df, sheetname, count, batches):
        """Generate progress messages for the current sheet export.

        This method builds human-readable progress messages describing the
        export status of a single DataFrame sheet. It returns all messages
        relevant to the current step, including global export information
        on the first sheet and per sheet progress details.

        Args:
            df (pd.DataFrame):
                The DataFrame being exported.
            sheetname (str):
                The sanitized name of the sheet being written.
            count (int):
                The 1-based index of the sheet currently being processed.
            batches (list[Any]):
                A list representing the number of write batches. Only the
                length of this list is used.

        Returns:
            list[str]:
                A list of progress messages for this step. The list may
                include hit-list status, word-wrap status, total DataFrame
                count (only on the first sheet), and the per-sheet message.

        """
        df_size = f"{df.shape[0]:,}"
        total_dfs = len(self.dataframes_ref)
        batch_count = len(batches)

        messages = []

        if count == 1:
            messages.append(self._report_hit_list_status())
            messages.append(self._report_word_wrap_status())
            messages.append(self._report_total_dfs(total_dfs))

        if df.shape[0] == 1:
            msg = (
                f"- {count} | Writes {df_size} row to '{sheetname}' "
                f"in {num2words(batch_count)} batch."
            )
        elif batch_count == 1:
            msg = (
                f"- {count} | Writes {df_size} rows to '{sheetname}' "
                f"in {num2words(batch_count)} batch."
            )
        else:
            msg = (
                f"- {count} | Writes {df_size} rows to '{sheetname}' "
                f"in {num2words(batch_count)} batches."
            )

        self.last_sheet_message = msg
        messages.append(msg)

        return messages

    # ------------------------------------------------------------------
    # Helper reporting methods
    # ------------------------------------------------------------------

    def _report_hit_list_status(self) -> str:
        """Return a message describing hit-list conditional formatting status.

        Returns:
            str: Human-readable description of hit-list configuration.

        """
        if not self.enable_hit_list:
            return "Hit list disabled — no conditional formatting will be applied."
        elif self.hit_list and self.check_cols:
            return (
                f"Vocabulary contains {num2words(len(self.hit_list))} "
                f"{'word' if len(self.hit_list) == 1 else 'words'} "
                f"applied to {num2words(len(self.check_cols))} columns: "
                f"{', '.join(self.check_cols)}."
            )
        return "No vocabulary provided."

    def _report_word_wrap_status(self) -> str:
        """Return a message describing word-wrap configuration.

        Returns:
            str: Word-wrap status message.

        """
        return (
            "Word wrap enabled (applies under 20.000 rows)."
            if self.enable_word_wrap
            else "Word wrap disabled."
        )

    def _report_total_dfs(self, total_dfs: int) -> str:
        """Return a message describing the total number of DataFrames.

        Args:
            total_dfs (int): Number of DataFrames registered for export.

        Returns:
            str: Message describing the total DataFrame count.

        """
        return (
            f"{num2words(total_dfs).title()} dataframe will be exported."
            if total_dfs == 1
            else f"{num2words(total_dfs).title()} dataframes will be exported."
        )
