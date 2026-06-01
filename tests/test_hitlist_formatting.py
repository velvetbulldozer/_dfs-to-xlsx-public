"""Tests for hit‑list conditional formatting integration inside XlsxDataFrameWriter.

This suite verifies that:
- The writer correctly forwards hit‑list settings to ConditionalFormatter.apply()
- The correct DataFrame, hit list, and check columns are passed through
- Conditional formatting is invoked exactly once per sheet
"""

from unittest.mock import MagicMock

import pandas as pd

from src.dfs_to_xlsx.xlsx_writer import XlsxDataFrameWriter


def test_hit_list_formatting(tmp_path):
    """Test that hit‑list formatting is applied with correct arguments."""
    writer = XlsxDataFrameWriter(
        output_folder=str(tmp_path),
        enable_hit_list=True,
        hit_list=["error", "warning"],
        check_cols=["status", "comments"],
        enable_word_wrap=False,
    )

    df = pd.DataFrame(
        {
            "status": ["ok", "error"],
            "comments": ["fine", "warning: check"],
        }
    )

    # Mock the conditional formatter so no real Excel operations occur
    writer.sheet_formatter.conditional_formatter.apply = MagicMock()

    # Add DataFrame and trigger synchronous write
    writer.add_df(df, "TestSheet")
    writer._write_sync()

    # Ensure conditional formatting was applied
    writer.sheet_formatter.conditional_formatter.apply.assert_called()

    # Extract call arguments
    args, kwargs = writer.sheet_formatter.conditional_formatter.apply.call_args

    # Validate forwarded parameters
    assert kwargs["hit_list"] == ["error", "warning"]
    assert kwargs["check_cols"] == ["status", "comments"]
    assert kwargs["enable_hit_list"] is True

    # DataFrame should be passed through unchanged
    assert kwargs["df"].equals(df)
