"""
Tests for the DataCleaner class.

This suite verifies that:
- safe_str_strip() trims strings safely without altering non-strings
- clean_collections() normalizes lists, tuples, dicts, and stringified collections
- clean_dataframe() applies all cleaning rules across an entire DataFrame
"""

import pandas as pd

from src.dfs_to_xlsx.modules.data_cleaner import DataCleaner


def test_safe_str_strip():
    """Test that safe_str_strip() trims strings and leaves non-strings unchanged."""
    cleaner = DataCleaner()

    # Basic trimming
    assert cleaner.safe_str_strip("  hello  ") == "hello"
    assert cleaner.safe_str_strip("nochange") == "nochange"

    # Non-strings should be returned unchanged
    assert cleaner.safe_str_strip(123) == 123
    assert cleaner.safe_str_strip(None) is None


def test_clean_collections():
    """Test that clean_collections() normalizes Python and stringified collections."""
    cleaner = DataCleaner()

    # Native Python collections
    assert cleaner.clean_collections(["a", "b"]) == "a, b"
    assert cleaner.clean_collections(("x", "y")) == "x, y"

    # Dict order is not guaranteed, so allow either ordering
    assert cleaner.clean_collections({"k": 1, "m": 2}) in ["k: 1, m: 2", "m: 2, k: 1"]

    # Stringified collections
    assert cleaner.clean_collections("[1, 2, 3]") == "1, 2, 3"
    assert cleaner.clean_collections("{'a': 1}") == "a: 1"
    assert cleaner.clean_collections("(x, y)") == "x, y"

    # Fallback to trimming
    assert cleaner.clean_collections("  hello  ") == "hello"


def test_clean_dataframe_full():
    """Test that clean_dataframe() applies all cleaning rules across all columns."""
    cleaner = DataCleaner()

    df = pd.DataFrame(
        {
            "name": ["  Alice  ", "  Bob  ", "  Carl  "],
            "tags": [["gold", "vip"], ["standard"], ["risk"]],
            "meta": [{"age": 30}, {"age": 40}, {"age": 50}],
            "raw": ["[1, 2, 3]", "{'a': 1}", "(x, y)"],
            "number": [10, 20, 30],
            "none": [None, None, None],
        }
    )

    cleaned = cleaner.clean_dataframe(df)

    # String trimming
    assert cleaned["name"][0] == "Alice"
    assert cleaned["name"][1] == "Bob"
    assert cleaned["name"][2] == "Carl"

    # List/tuple normalization
    assert cleaned["tags"][0] == "gold, vip"
    assert cleaned["tags"][1] == "standard"
    assert cleaned["tags"][2] == "risk"

    # Dict normalization
    assert "age: 30" in cleaned["meta"][0]
    assert "age: 40" in cleaned["meta"][1]
    assert "age: 50" in cleaned["meta"][2]

    # Stringified collections
    assert cleaned["raw"][0] == "1, 2, 3"
    assert cleaned["raw"][1] == "a: 1"
    assert cleaned["raw"][2] == "x, y"

    # Numbers unchanged
    assert cleaned["number"][0] == 10
    assert cleaned["number"][2] == 30

    # None unchanged
    assert cleaned["none"][0] is None
    assert cleaned["none"][2] is None
