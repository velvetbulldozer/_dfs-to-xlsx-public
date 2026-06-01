# SPDX-License-Identifier: MIT

from __future__ import annotations  # Future-proof type annotations

# Standard library imports
from typing import Any  # Generic typing support

# Third-party imports
import pandas as pd  # DataFrame handling


class ConditionalFormatter:
    """Create workbook formats and apply conditional formatting rules.

    This class encapsulates all formatting logic used during Excel export,
    including creation of reusable XlsxWriter format objects and applying
    hit-list based conditional formatting to worksheets.

    Args:
        header_color (str, optional):
            Hex color for the header background. Defaults to "#F2F2F2".
            This value is typically overridden by YAML configuration.
        header_font_color (str, optional):
            Hex color for the header text. Defaults to "#595959".
            This value is typically overridden by YAML configuration.

    """

    def __init__(self, header_color: str, header_font_color: str) -> None:
        self.header_color = header_color
        self.header_font_color = header_font_color

    # ------------------------------------------------------------------
    # Create formatting presets
    # ------------------------------------------------------------------
    def create_formats(self, workbook) -> tuple[Any, Any, Any, Any, Any]:
        """Create formatting profiles for the workbook.

        Args:
            workbook (xlsxwriter.Workbook): Workbook object.

        Returns:
            tuple: Header, wrap-left, left, URL, and highlight formats.

        """
        header_format = workbook.add_format(
            {
                "font_name": "Calibri",
                "font_size": 11,
                "bold": True,
                "bottom": 1,
                "bg_color": self.header_color,
                "font_color": self.header_font_color,
            }
        )

        wrap_left_format = workbook.add_format(
            {
                "font_name": "Calibri",
                "font_size": 11,
                "text_wrap": True,
                "align": "left",
                "valign": "top",
            }
        )

        left_format = workbook.add_format(
            {
                "font_name": "Calibri",
                "font_size": 11,
                "text_wrap": False,
                "align": "left",
                "valign": "top",
            }
        )

        url_format = workbook.add_format(
            {
                "font_color": "blue",
                "underline": 1,
                "align": "left",
                "valign": "top",
            }
        )

        highlight_format = workbook.add_format(
            {"bg_color": "#FFF2CC", "font_color": "#9C6500"}
        )

        return (
            header_format,
            wrap_left_format,
            left_format,
            url_format,
            highlight_format,
        )

    # ------------------------------------------------------------------
    # Apply conditional formatting
    # ------------------------------------------------------------------
    def apply(
        self,
        worksheet,
        df: pd.DataFrame,
        hit_list: list[str] | None,
        check_cols: list[str] | None,
        highlight_format: Any,
        enable_hit_list: bool,
    ) -> None:
        """Apply conditional formatting based on hit list.

        Args:
            worksheet: XlsxWriter worksheet.
            df (pd.DataFrame): DataFrame for the sheet.
            hit_list (list[str] | None): Words to highlight.
            check_cols (list[str] | None): Columns to apply formatting.
            highlight_format: XlsxWriter format object.
            enable_hit_list (bool): Whether conditional formatting is enabled.

        Returns:
            None.

        """
        if not enable_hit_list:
            return

        if not hit_list or not check_cols:
            return

        for col_name in check_cols:
            if col_name not in df.columns:
                continue

            col_idx = df.columns.get_loc(col_name)
            last_row = len(df)

            for word in hit_list:
                worksheet.conditional_format(
                    1,
                    col_idx,
                    last_row,
                    col_idx,
                    {
                        "type": "text",
                        "criteria": "containing",
                        "value": word,
                        "format": highlight_format,
                    },
                )
