# SPDX-License-Identifier: MIT

from __future__ import annotations  # Future-proof type annotations

# Third-party imports
import pandas as pd  # For type annotations
from xlsxwriter.worksheet import Worksheet  # For type annotations


class SheetFormatter:
    """Applies formatting to Excel worksheets.

    This class encapsulates all formatting operations applied to each
    worksheet during export, including column sizing, word wrapping,
    header freezing, autofilters, and conditional formatting.

    Attributes:
        enable_word_wrap (bool): Whether word wrapping is enabled.
        conditional_formatter: Instance responsible for applying
            conditional formatting rules.
        hit_list (list[str]): Keywords to highlight.
        check_cols (list[str]): Columns where hit-list highlighting applies.

    """

    def __init__(
        self,
        enable_hit_list: bool,
        freeze_panes: int,
        freeze_rows: int,
        max_line_length: int,
        enable_word_wrap: bool,
        conditional_formatter,
        hit_list: list[str],
        check_cols: list[str],
    ) -> None:
        """Initialize the sheet formatter.

        Args:
            enable_hit_list (bool): Whether hit-list conditional formatting is enabled.
            freeze_panes (int): Number of columns to freeze (header).
            freeze_rows (int): Number of rows to freeze.
            max_line_length (int): Maximum line length.
            enable_word_wrap (bool): Whether to enable word wrapping.
            conditional_formatter: ConditionalFormatter instance.
            hit_list (list[str]): Words to highlight.
            check_cols (list[str]): Columns to check for hit-list matches.

        """
        self.enable_hit_list = enable_hit_list
        self.freeze_panes = freeze_panes
        self.freeze_rows = freeze_rows
        self.max_line_length = int(max_line_length)
        self.enable_word_wrap = enable_word_wrap
        self.conditional_formatter = conditional_formatter
        self.hit_list = hit_list
        self.check_cols = check_cols

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def apply_shared_formatting(
        self,
        worksheet: Worksheet,
        df: pd.DataFrame,
        wrap_left_format,
        left_format,
        highlight_format,
    ) -> None:
        """Apply all shared formatting to a worksheet.

        This includes:
        - Column width auto-sizing
        - Word wrapping (if enabled)
        - Freezing the header row
        - Adding an autofilter
        - Applying conditional formatting

        Args:
            worksheet (Worksheet): The worksheet to format.
            df (pd.DataFrame): DataFrame written to the worksheet.
            wrap_left_format: XlsxWriter format for wrapped text.
            left_format: XlsxWriter format for normal left-aligned text.
            highlight_format: XlsxWriter format for hit-list highlighting.

        """
        self._set_column_widths(worksheet, df, wrap_left_format, left_format)
        self._freeze_header(worksheet)
        self._apply_autofilter(worksheet, df)

        # Only apply hit-list formatting if enabled and there are keywords to check
        if self.enable_hit_list and self.hit_list:
            self._apply_conditional_formatting(worksheet, df, highlight_format)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _set_column_widths(
        self,
        worksheet: Worksheet,
        df: pd.DataFrame,
        wrap_left_format,
        left_format,
    ) -> None:
        """Auto-size worksheet columns with optional wrapping and maximum width.

        This method computes the optimal width for each column based on the
        longest value in the column and the column header. If ``self.max_line_length``
        is set, the computed width is capped at that value. Word wrapping is
        applied when enabled and the DataFrame size is below the configured
        threshold.

        Args:
            worksheet (Worksheet):
                The XlsxWriter worksheet where column widths will be applied.
            df (pd.DataFrame):
                The DataFrame whose columns determine the width calculations.
            wrap_left_format:
                XlsxWriter cell format used when word wrapping is enabled.
            left_format:
                XlsxWriter cell format used when word wrapping is disabled.

        Returns:
            None

        """
        for col_num, col in enumerate(df.columns):
            # Compute natural width
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2

            # Apply user-defined maximum width if set
            if self.max_line_length is not None:
                max_len = min(max_len, self.max_line_length)

            # Choose format
            fmt = wrap_left_format if self.enable_word_wrap else left_format

            worksheet.set_column(col_num, col_num, max_len, fmt)

    def _freeze_header(self, worksheet: Worksheet) -> None:
        """Freeze the first row of the worksheet.

        Args:
            worksheet (Worksheet): Target worksheet to modify.

        """
        worksheet.freeze_panes(self.freeze_rows, self.freeze_panes)

    def _apply_autofilter(self, worksheet: Worksheet, df: pd.DataFrame) -> None:
        """Apply an autofilter to the full DataFrame range.

        Args:
            worksheet (Worksheet): Worksheet where the filter is applied.
            df (pd.DataFrame): DataFrame defining the filter range.

        """
        last_row = len(df)
        last_col = len(df.columns) - 1
        worksheet.autofilter(0, 0, last_row, last_col)

    def _apply_conditional_formatting(
        self,
        worksheet: Worksheet,
        df: pd.DataFrame,
        highlight_format,
    ) -> None:
        """Apply hit-list conditional formatting to the worksheet.

        Args:
            worksheet (Worksheet): Worksheet to format.
            df (pd.DataFrame): DataFrame used to determine formatting range.
            highlight_format (Any): XlsxWriter format object for highlighting.

        """
        self.conditional_formatter.apply(
            worksheet=worksheet,
            df=df,
            hit_list=self.hit_list,
            check_cols=self.check_cols,
            highlight_format=highlight_format,
            enable_hit_list=bool(self.hit_list),
        )
