"""Tests for the ConditionalFormatter class.

This suite verifies that conditional formatting is applied correctly
based on hit-list settings. It covers:

- Disabled hit-list → no formatting applied
- Empty hit-list → no formatting applied
- Empty check-cols → no formatting applied
- Missing columns → no formatting applied
- Valid hit-list + valid columns → correct conditional formatting calls
"""

from unittest.mock import MagicMock, call

import pandas as pd

from src.dfs_to_xlsx.modules.conditional_formatter import ConditionalFormatter


def test_no_formatting_when_disabled():
    """Test that no conditional formatting is applied when enable_hit_list=False."""
    worksheet = MagicMock()
    df = pd.DataFrame({"A": ["ok", "error"]})

    cf = ConditionalFormatter()

    cf.apply(
        worksheet=worksheet,
        df=df,
        hit_list=["error"],
        check_cols=["A"],
        highlight_format=MagicMock(),
        enable_hit_list=False,
    )

    # Hit-list disabled → no formatting should be applied
    worksheet.conditional_format.assert_not_called()


def test_no_formatting_when_hit_list_empty():
    """Test that no formatting is applied when hit_list is empty."""
    worksheet = MagicMock()
    df = pd.DataFrame({"A": ["ok", "error"]})

    cf = ConditionalFormatter()

    cf.apply(
        worksheet=worksheet,
        df=df,
        hit_list=[],
        check_cols=["A"],
        highlight_format=MagicMock(),
        enable_hit_list=True,
    )

    # No hit-list words → no formatting
    worksheet.conditional_format.assert_not_called()


def test_no_formatting_when_check_cols_empty():
    """Test that no formatting is applied when check_cols is empty."""
    worksheet = MagicMock()
    df = pd.DataFrame({"A": ["ok", "error"]})

    cf = ConditionalFormatter()

    cf.apply(
        worksheet=worksheet,
        df=df,
        hit_list=["error"],
        check_cols=[],
        highlight_format=MagicMock(),
        enable_hit_list=True,
    )

    # No columns to check → no formatting
    worksheet.conditional_format.assert_not_called()


def test_no_formatting_when_column_missing():
    """Test that no formatting is applied when check_cols refer to missing columns."""
    worksheet = MagicMock()
    df = pd.DataFrame({"A": ["ok", "error"]})

    cf = ConditionalFormatter()

    cf.apply(
        worksheet=worksheet,
        df=df,
        hit_list=["error"],
        check_cols=["missing_col"],
        highlight_format=MagicMock(),
        enable_hit_list=True,
    )

    # Column does not exist → no formatting
    worksheet.conditional_format.assert_not_called()


def test_hit_list_formatting_applied_correctly():
    """Test that conditional formatting is applied correctly for valid hit-list and columns."""
    worksheet = MagicMock()
    highlight = MagicMock()

    df = pd.DataFrame(
        {
            "status": ["ok", "error", "warning"],
            "notes": ["fine", "check", "warning here"],
        }
    )

    cf = ConditionalFormatter()

    cf.apply(
        worksheet=worksheet,
        df=df,
        hit_list=["error", "warning"],
        check_cols=["status", "notes"],
        highlight_format=highlight,
        enable_hit_list=True,
    )

    # Expected calls:
    # df has 3 rows → Excel rows 1..3 (0 is header)
    expected_calls = [
        # status column (index 0)
        call(
            1,
            0,
            3,
            0,
            {
                "type": "text",
                "criteria": "containing",
                "value": "error",
                "format": highlight,
            },
        ),
        call(
            1,
            0,
            3,
            0,
            {
                "type": "text",
                "criteria": "containing",
                "value": "warning",
                "format": highlight,
            },
        ),
        # notes column (index 1)
        call(
            1,
            1,
            3,
            1,
            {
                "type": "text",
                "criteria": "containing",
                "value": "error",
                "format": highlight,
            },
        ),
        call(
            1,
            1,
            3,
            1,
            {
                "type": "text",
                "criteria": "containing",
                "value": "warning",
                "format": highlight,
            },
        ),
    ]

    # Validate that all expected formatting calls were made
    worksheet.conditional_format.assert_has_calls(expected_calls, any_order=True)

    # Ensure exactly 4 calls were made (2 columns × 2 hit-list words)
    assert worksheet.conditional_format.call_count == 4
