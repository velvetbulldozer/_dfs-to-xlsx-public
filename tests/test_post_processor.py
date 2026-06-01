"""Tests for the PostProcessor class.

This suite verifies that:
- Small files below the size threshold are left untouched
- Large files above the threshold are zipped, removed, and replaced with a .zip archive
- The returned metadata includes correct status, paths, and size information
"""

import os
import zipfile

from src.dfs_to_xlsx.modules.post_processor import PostProcessor


def test_process_small_file(tmp_path):
    """Test that small files remain unchanged and return status 'ok'."""
    # Create a small dummy file (< max_size_mb)
    file_path = tmp_path / "small.xlsx"
    file_path.write_bytes(b"12345")  # ~5 KB

    pp = PostProcessor(max_size_mb=1)  # 1 MB limit

    result = pp.process(str(file_path))

    # File should remain untouched
    assert result["status"] == "ok"
    assert result["file_path"] == str(file_path)
    assert os.path.isfile(file_path)
    assert result["size_mb"] < 1


def test_process_large_file(tmp_path):
    """Test that large files are zipped and the original file is removed."""
    # Create a large dummy file (> max_size_mb)
    file_path = tmp_path / "large.xlsx"
    file_path.write_bytes(b"0" * (2 * 1024 * 1024))  # 2 MB

    pp = PostProcessor(max_size_mb=1)  # 1 MB limit

    result = pp.process(str(file_path))

    zip_path = file_path.with_suffix(".zip")

    # Status and metadata
    assert result["status"] == "zipped"
    assert result["zip_path"] == str(zip_path)
    assert result["original_size_mb"] > 1

    # ZIP exists
    assert os.path.isfile(zip_path)

    # Original file removed
    assert not os.path.exists(file_path)

    # ZIP contains the original file
    with zipfile.ZipFile(zip_path, "r") as zf:
        assert "large.xlsx" in zf.namelist()
