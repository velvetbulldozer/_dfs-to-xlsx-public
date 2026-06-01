"""Tests for the FilenameBuilder class.

This suite verifies that:
- Timestamps follow the expected YYYYMMDD_HHMMSS format
- Filenames are constructed correctly for the first file and split files
- Base filenames are sanitized by stripping directory paths
"""

import os
from unittest.mock import patch

from src.dfs_to_xlsx.modules.filename_builder import FilenameBuilder


def test_timestamp_format():
    """Test that timestamp() returns a valid YYYYMMDD_HHMMSS string."""
    fb = FilenameBuilder("export", "/tmp")

    ts = fb.timestamp()

    # Format: YYYYMMDD_HHMMSS → length 15
    assert len(ts) == 15
    assert ts[8] == "_"
    assert ts[:8].isdigit()
    assert ts[9:].isdigit()


def test_build_first_file(tmp_path):
    """Test that build(1) produces the correct filename for the first file."""
    fb = FilenameBuilder("export", str(tmp_path))

    # Freeze timestamp for deterministic test
    with patch.object(fb, "timestamp", return_value="20260101_120000"):
        filename = fb.build(1)

    expected = os.path.join(str(tmp_path), "20260101_120000_export.xlsx")
    assert filename == expected


def test_build_split_file(tmp_path):
    """Test that build(n) appends the split index for n > 1."""
    fb = FilenameBuilder("export", str(tmp_path))

    # Freeze timestamp
    with patch.object(fb, "timestamp", return_value="20260101_120000"):
        filename = fb.build(3)

    expected = os.path.join(str(tmp_path), "20260101_120000_export_3.xlsx")
    assert filename == expected


def test_base_filename_strips_path(tmp_path):
    """Test that only the final component of the base filename is used."""
    fb = FilenameBuilder("/some/path/myfile", str(tmp_path))

    with patch.object(fb, "timestamp", return_value="20260101_120000"):
        filename = fb.build(1)

    expected = os.path.join(str(tmp_path), "20260101_120000_myfile.xlsx")
    assert filename == expected
