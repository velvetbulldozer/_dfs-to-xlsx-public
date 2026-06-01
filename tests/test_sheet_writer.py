"""Tests for the SheetWriter class.

This suite verifies that:
- The fast‑path write logic calls DataFrame.to_excel exactly once
- ProgressReporter receives the correct batch information
- The returned worksheet object is the one stored in writer.sheets
"""

from unittest.mock import MagicMock, patch

import pandas as pd

from src.dfs_to_xlsx.modules.sheet_writer import SheetWriter


def test_write_fast_path_calls_to_excel_and_reports_progress():
    """Test that fast‑path writing triggers to_excel once and reports progress."""
    df = pd.DataFrame({"A": [1, 2, 3]})

    progress = MagicMock()
    writer = MagicMock()
    writer.sheets = {"Sheet1": MagicMock()}

    sw = SheetWriter(batch_threshold=10, batch_size=5, progress=progress)

    # Patch DataFrame.to_excel so no real file I/O occurs
    with patch.object(pd.DataFrame, "to_excel", return_value=None) as mock_to_excel:
        result_ws = sw.write(
            workbook=MagicMock(),
            writer=writer,
            sheet_name="Sheet1",
            df=df,
            header_format=MagicMock(),
            count=1,
        )

    # Fast path → df.to_excel called once
    mock_to_excel.assert_called_once_with(writer, sheet_name="Sheet1", index=False)

    # Progress reporter called with exactly one batch
    progress.report.assert_called_once()
    args, kwargs = progress.report.call_args
    assert len(kwargs["batches"]) == 1

    # Returned worksheet should be writer.sheets["Sheet1"]
    assert result_ws == writer.sheets["Sheet1"]
