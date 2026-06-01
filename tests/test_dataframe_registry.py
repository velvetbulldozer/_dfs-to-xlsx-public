"""Tests for the DataFrameRegistry class.

This suite verifies that:
- Sheet names are sanitized before being stored
- Duplicate sheet names (after sanitization) are rejected
- DataFrames can be added from dicts, lists of tuples, and auto‑named lists
- Invalid inputs raise TypeError
- Sheet name listing works as expected
"""

from unittest.mock import MagicMock

import pandas as pd

from src.dfs_to_xlsx.modules.dataframe_registry import DataFrameRegistry


def test_add_df_sanitizes_name():
    """Test that sheet names are sanitized before being stored."""
    sanitizer = MagicMock(return_value="CleanName")
    reg = DataFrameRegistry(sanitizer)

    df = pd.DataFrame({"a": [1]})
    reg.add_df(df, "Dirty/Name")

    # Sanitized name should be used as key
    assert "CleanName" in reg.dataframes

    # Sanitizer should be called exactly once
    sanitizer.assert_called_once()


def test_add_df_rejects_duplicate_after_sanitization():
    """Test that duplicate sheet names (after sanitization) are rejected."""
    sanitizer = MagicMock(side_effect=lambda name, existing: "Sheet1")
    reg = DataFrameRegistry(sanitizer)

    df = pd.DataFrame({"a": [1]})

    reg.add_df(df, "Original")
    reg.add_df(df, "AnotherName")  # Sanitizes to same name → skipped

    # Only one entry should exist
    assert len(reg.dataframes) == 1


def test_add_dfs_dict():
    """Test adding multiple DataFrames from a dict."""
    sanitizer = MagicMock(side_effect=lambda name, existing: name)
    reg = DataFrameRegistry(sanitizer)

    data = {
        "Sales": pd.DataFrame({"x": [1]}),
        "Customers": pd.DataFrame({"y": [2]}),
    }

    reg.add_dfs(data)

    assert "Sales" in reg.dataframes
    assert "Customers" in reg.dataframes
    assert len(reg.dataframes) == 2


def test_add_dfs_list_of_tuples():
    """Test adding DataFrames from a list of (name, df) tuples."""
    sanitizer = MagicMock(side_effect=lambda name, existing: name)
    reg = DataFrameRegistry(sanitizer)

    data = [
        ("SheetA", pd.DataFrame({"a": [1]})),
        ("SheetB", pd.DataFrame({"b": [2]})),
    ]

    reg.add_dfs(data)

    assert "SheetA" in reg.dataframes
    assert "SheetB" in reg.dataframes
    assert len(reg.dataframes) == 2


def test_add_dfs_auto_named_list():
    """Test adding DataFrames from a list without names (auto‑naming)."""
    sanitizer = MagicMock(side_effect=lambda name, existing: name)
    reg = DataFrameRegistry(sanitizer)

    data = [
        pd.DataFrame({"a": [1]}),
        pd.DataFrame({"b": [2]}),
    ]

    reg.add_dfs(data)

    # Auto‑generated names
    assert "Sheet_1" in reg.dataframes
    assert "Sheet_2" in reg.dataframes
    assert len(reg.dataframes) == 2


def test_add_dfs_invalid_input():
    """Test that invalid inputs raise TypeError."""
    sanitizer = MagicMock()
    reg = DataFrameRegistry(sanitizer)

    data = ["not a df", 123]

    try:
        reg.add_dfs(data)
        assert False, "Expected TypeError"
    except TypeError:
        assert True


def test_list_sheet_names_returns_list():
    """Test that list_sheet_names() returns sheet names in order."""
    sanitizer = MagicMock(side_effect=lambda name, existing: name)
    reg = DataFrameRegistry(sanitizer)

    reg.add_df(pd.DataFrame({"a": [1]}), "Sheet1")
    reg.add_df(pd.DataFrame({"b": [2]}), "Sheet2")

    names = reg.list_sheet_names(verbose=False)

    assert names == ["Sheet1", "Sheet2"]
