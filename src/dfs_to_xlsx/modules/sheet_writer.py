# SPDX-License-Identifier: MIT

from __future__ import annotations  # Future-proof type annotations

# Standard library imports
import math  # Math utilities (ceil for batching)
from turtle import pd
from typing import Any  # Generic typing support

import pandas as pd  # For type annotations


class SheetWriter:
    """Handles writing a single DataFrame to an Excel worksheet.

    This class encapsulates all logic related to writing a sheet, including
    batching for large DataFrames, header writing, and integration with the
    progress reporter. It does not apply formatting or perform data cleaning;
    those responsibilities belong to other components.

    Attributes:
        batch_threshold (int):
            Maximum number of rows allowed before batching is activated.
        batch_size (int):
            Number of rows per batch when batching is used.
        progress (ProgressReporter):
            Object responsible for reporting progress to the user.

    """

    def __init__(self, batch_threshold: int, batch_size: int, progress) -> None:
        """Initialize the SheetWriter.

        Args:
            batch_threshold (int):
                Row count threshold at which batching is enabled.
            batch_size (int):
                Number of rows to write per batch when batching is active.
            progress (ProgressReporter):
                Progress reporter used to inform the user about sheet writing
                status and batch counts.

        """
        self.batch_threshold = batch_threshold
        self.batch_size = batch_size
        self.progress = progress

    def write(
        self,
        workbook: Any,
        sheet_name: str,
        df: pd.DataFrame,
        wrap_left_format: Any,
        header_format: Any,
        count: int,
    ) -> Any:
        """Write a DataFrame to an Excel worksheet with optional batching.

        Batching is used when the DataFrame exceeds ``batch_threshold``. In
        batched mode, headers and rows are written manually in chunks of
        ``batch_size``. In non-batched mode, the DataFrame is written using
        ``DataFrame.to_excel`` for maximum performance.

        Args:
            workbook (xlsxwriter.Workbook):
                Workbook used to create worksheets and formats.
            sheet_name (str):
                Name of the worksheet to create.
            df (pd.DataFrame):
                DataFrame to write.
            header_format (xlsxwriter.Format):
                Format applied to header cells in batched mode.
            wrap_left_format: XlsxWriter format for wrapped text.
            count (int):
                Index of the sheet being written, used for progress reporting.

        Returns:
            xlsxwriter.Worksheet:
                The worksheet that was written to.

        Raises:
            ValueError:
                If the DataFrame has no columns.

        """
        # Validate that the DataFrame has columns to write
        if df.empty and len(df.columns) == 0:
            raise ValueError(
                f"Cannot write sheet '{sheet_name}': DataFrame has no columns."
            )

        # Get the number of rows in the DataFrame to determine if batching is needed
        row_count = len(df)

        # Decide whether to use batching at all
        use_batches = row_count > self.batch_threshold

        # Calculate the number of batches needed if batching is enabled
        if use_batches:
            batch_count = math.ceil(row_count / self.batch_size)
        else:
            batch_count = 1

        # Report progress with the actual number of batches we will use
        self.progress.report(
            df=df,
            sheetname=sheet_name,
            count=count,
            batches=[None] * batch_count,
        )

        # Fast path: no batching
        if not use_batches:
            ws = workbook.add_worksheet(sheet_name)

            # Write header with your custom format
            ws.write_row(0, 0, df.columns.tolist(), header_format)

            # Write data rows
            for row_idx, row in enumerate(df.to_numpy().tolist(), start=1):
                ws.write_row(row_idx, 0, row, wrap_left_format)

            return ws

        # Batched path
        ws = workbook.add_worksheet(sheet_name)

        # Write header
        ws.write_row(0, 0, df.columns.tolist(), header_format)

        # Convert DataFrame to list of lists for faster access during batching
        data = df.to_numpy().tolist()

        for start in range(0, row_count, self.batch_size):
            end = min(start + self.batch_size, row_count)
            batch = data[start:end]

            # Write rows in batches
            for row_offset, row in enumerate(batch, start=1 + start):
                ws.write_row(row_offset, 0, row, wrap_left_format)

        return ws
