"""Tests for the ProgressReporter class.

This suite verifies that:
- First‑sheet logging includes hit‑list info, word‑wrap status, and total DF count
- Disabled hit‑list logs the correct messages
- Sheet‑level messages are formatted correctly for:
  - single row
  - multiple rows, single batch
  - multiple rows, multiple batches
"""

import locale
import logging

import pandas as pd

from src.dfs_to_xlsx.modules.progress_reporter import ProgressReporter


def test_progress_reporter_first_sheet_logs_hitlist_wordwrap_total(caplog):
    """Test that first‑sheet logging includes hit‑list, word‑wrap, and DF count."""
    caplog.set_level(logging.INFO)

    dfs = {
        "A": pd.DataFrame({"x": [1, 2]}),
        "B": pd.DataFrame({"x": [3, 4]}),
    }

    pr = ProgressReporter(
        enable_hit_list=True,
        hit_list=["error", "warning"],
        check_cols=["status", "comments"],
        enable_word_wrap=True,
        dataframes_ref=dfs,
    )

    df = dfs["A"]
    pr.report(df, "SheetA", count=1, batches=[1, 2])

    logs = " ".join(record.message for record in caplog.records)

    assert (
        "Vocabulary contains two words applied to two columns: status, comments."
        in logs
    )
    assert "Word wrap enabled" in logs
    assert "Two dataframes will be exported." in logs


def test_progress_reporter_first_sheet_logs_disabled_hitlist(caplog):
    """Test that disabled hit‑list logs the correct messages."""
    caplog.set_level(logging.INFO)

    dfs = {"A": pd.DataFrame({"x": [1]})}

    pr = ProgressReporter(
        enable_hit_list=False,
        hit_list=["error"],
        check_cols=["status"],
        enable_word_wrap=False,
        dataframes_ref=dfs,
    )

    df = dfs["A"]
    pr.report(df, "SheetA", count=1, batches=[1])

    logs = " ".join(record.message for record in caplog.records)

    assert "Hit list disabled" in logs
    assert "Word wrap disabled" in logs
    assert "One dataframe will be exported." in logs


def test_progress_reporter_sheet_message_single_row():
    """Test sheet‑level message for a single row and one batch."""
    dfs = {"A": pd.DataFrame({"x": [1]})}

    pr = ProgressReporter(
        enable_hit_list=False,
        hit_list=None,
        check_cols=None,
        enable_word_wrap=False,
        dataframes_ref=dfs,
    )

    df = dfs["A"]
    pr.report(df, "SheetA", count=1, batches=[1])

    assert pr.last_sheet_message == "- 1 | Writes 1 row to 'SheetA' in one batch."


def test_progress_reporter_sheet_message_multiple_rows_single_batch():
    """Test sheet‑level message for multiple rows in a single batch."""
    dfs = {"A": pd.DataFrame({"x": list(range(10))})}

    pr = ProgressReporter(
        enable_hit_list=False,
        hit_list=None,
        check_cols=None,
        enable_word_wrap=False,
        dataframes_ref=dfs,
    )

    df = dfs["A"]
    pr.report(df, "SheetA", count=1, batches=[1])

    # Locale‑formatted row count
    row_count = locale.format_string("%d", df.shape[0], grouping=True)

    assert pr.last_sheet_message == (
        f"- 1 | Writes {row_count} rows to 'SheetA' in one batch."
    )


def test_progress_reporter_sheet_message_multiple_batches():
    """Test sheet‑level message for multiple rows across multiple batches."""
    dfs = {"A": pd.DataFrame({"x": list(range(100))})}

    pr = ProgressReporter(
        enable_hit_list=False,
        hit_list=None,
        check_cols=None,
        enable_word_wrap=False,
        dataframes_ref=dfs,
    )

    df = dfs["A"]
    pr.report(df, "SheetA", count=1, batches=[1, 2, 3])

    row_count = locale.format_string("%d", df.shape[0], grouping=True)

    assert pr.last_sheet_message == (
        f"- 1 | Writes {row_count} rows to 'SheetA' in three batches."
    )
