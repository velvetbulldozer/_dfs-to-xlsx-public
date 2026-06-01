"""Tests for the SheetFormatter class.

This suite verifies that:
- Shared formatting applies column widths, freeze panes, autofilter,
  and delegates conditional formatting correctly.
- Column width logic switches between wrap format and left format
  depending on the word-wrap setting.
"""

from unittest.mock import MagicMock

import pandas as pd

from src.dfs_to_xlsx.modules.sheet_formatter import SheetFormatter


def test_apply_shared_formatting_calls_all_helpers():
    """Test that apply_shared_formatting() triggers all formatting helpers."""
    # Mock worksheet and formats
    worksheet = MagicMock()
    wrap_fmt = MagicMock()
    left_fmt = MagicMock()
    highlight_fmt = MagicMock()

    # Mock conditional formatter
    conditional_formatter = MagicMock()

    df = pd.DataFrame(
        {
            "A": ["hello", "world"],
            "B": ["x", "y"],
        }
    )

    sf = SheetFormatter(
        enable_word_wrap=True,
        conditional_formatter=conditional_formatter,
        hit_list=["error"],
        check_cols=["A"],
    )

    sf.apply_shared_formatting(
        worksheet=worksheet,
        df=df,
        wrap_left_format=wrap_fmt,
        left_format=left_fmt,
        highlight_format=highlight_fmt,
    )

    # Column widths applied once per column
    assert worksheet.set_column.call_count == len(df.columns)

    # Freeze header row
    worksheet.freeze_panes.assert_called_once_with(1, 0)

    # Autofilter applied across full DataFrame
    worksheet.autofilter.assert_called_once_with(0, 0, len(df), len(df.columns) - 1)

    # Conditional formatting delegated correctly
    conditional_formatter.apply.assert_called_once()
    args, kwargs = conditional_formatter.apply.call_args

    assert kwargs["worksheet"] == worksheet
    assert kwargs["df"].equals(df)
    assert kwargs["hit_list"] == ["error"]
    assert kwargs["check_cols"] == ["A"]
    assert kwargs["highlight_format"] == highlight_fmt
    assert kwargs["enable_hit_list"] is True


def test_set_column_widths_uses_wrap_format_when_enabled():
    """Test that wrap format is used when word‑wrap is enabled."""
    worksheet = MagicMock()
    wrap_fmt = MagicMock()
    left_fmt = MagicMock()

    df = pd.DataFrame({"A": ["longtext", "short"]})

    sf = SheetFormatter(
        enable_word_wrap=True,
        conditional_formatter=MagicMock(),
        hit_list=[],
        check_cols=[],
    )

    sf._set_column_widths(worksheet, df, wrap_fmt, left_fmt)

    # Should use wrap format
    worksheet.set_column.assert_called_with(
        0, 0, max(df["A"].astype(str).map(len).max(), len("A")) + 2, wrap_fmt
    )


def test_set_column_widths_uses_left_format_when_disabled():
    """Test that left‑aligned format is used when word‑wrap is disabled."""
    worksheet = MagicMock()
    wrap_fmt = MagicMock()
    left_fmt = MagicMock()

    df = pd.DataFrame({"A": ["longtext", "short"]})

    sf = SheetFormatter(
        enable_word_wrap=False,
        conditional_formatter=MagicMock(),
        hit_list=[],
        check_cols=[],
    )

    sf._set_column_widths(worksheet, df, wrap_fmt, left_fmt)

    worksheet.set_column.assert_called_with(
        0, 0, max(df["A"].astype(str).map(len).max(), len("A")) + 2, left_fmt
    )
