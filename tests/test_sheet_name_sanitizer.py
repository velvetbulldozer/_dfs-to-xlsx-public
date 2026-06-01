"""Tests for the SheetNameSanitizer class.

This suite verifies that:
- Invalid Excel sheet name characters are removed
- Leading/trailing whitespace and apostrophes are stripped
- Maximum sheet name length is enforced
- Empty names fall back to a default ("Sheet")
- Name collisions are resolved by suffixing (_1, _2, _3, ...)
- Truncation + uniqueness logic works together correctly
"""

from src.dfs_to_xlsx.modules.sheet_name_sanitizer import SheetNameSanitizer


def test_removes_invalid_characters():
    """Test that invalid Excel characters are removed from sheet names."""
    s = SheetNameSanitizer()
    result = s.sanitize("Bad:Name/With*Chars?", existing=set())
    assert result == "BadNameWithChars"


def test_trims_and_strips_apostrophes():
    """Test that whitespace and surrounding apostrophes are stripped."""
    s = SheetNameSanitizer()
    result = s.sanitize("  'Hello World'  ", existing=set())
    assert result == "Hello World"


def test_max_length_enforced():
    """Test that sheet names are truncated to the maximum allowed length."""
    s = SheetNameSanitizer()
    long_name = "A" * 50  # exceeds Excel's 31‑character limit
    result = s.sanitize(long_name, existing=set())
    assert len(result) == s.MAX_LEN


def test_empty_name_fallback():
    """Test that an empty sanitized name falls back to 'Sheet'."""
    s = SheetNameSanitizer()
    result = s.sanitize(":/[]", existing=set())  # becomes empty after cleaning
    assert result == "Sheet"


def test_uniqueness_suffixing():
    """Test that name collisions are resolved by appending a numeric suffix."""
    s = SheetNameSanitizer()
    existing = {"Sheet", "Sheet_1", "Sheet_2"}

    result = s.sanitize("Sheet", existing)
    assert result == "Sheet_3"


def test_uniqueness_with_truncation():
    """Test that truncation and uniqueness suffixing work together correctly."""
    s = SheetNameSanitizer()

    base = "A" * 31  # exactly at max length
    existing = {base, base[:-2] + "_1"}  # simulate collision after truncation

    result = s.sanitize(base, existing)

    # Should append _2 but still respect max length
    assert result.endswith("_2")
    assert len(result) <= s.MAX_LEN
