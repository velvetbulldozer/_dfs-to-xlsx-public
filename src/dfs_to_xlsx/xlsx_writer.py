# SPDX-License-Identifier: MIT

# Standard library imports
import logging  # Logging to console and file
import math  # Math utilities (ceil for batching)
import os  # File and path operations
from typing import Any  # Generic typing support

# Third-party imports
import pandas as pd  # DataFrame handling
import yaml  # YAML configuration loader
from tqdm import tqdm  # Optional progress bars for long operations

# Local imports
from .modules.conditional_formatter import (
    ConditionalFormatter,  # Utility for applying conditional formatting rules
)
from .modules.config_loader import (
    ConfigLoader,  # Configuration management for the exporter
)
from .modules.data_cleaner import (
    DataCleaner,  # Data cleaning utilities for normalizing DataFrame values
)
from .modules.dataframe_registry import (
    DataFrameRegistry,  # Registry for storing DataFrames
)
from .modules.filename_builder import (
    FilenameBuilder,  # Utility for constructing timestamped output filenames
)
from .modules.logger_manager import (
    LoggerManager,  # Logger manager for handling logging to file and console
)
from .modules.post_processor import (
    PostProcessor,  # Utility for post-processing exported Excel files, ZIP compression
)
from .modules.progress_reporter import (
    ProgressReporter,  # User-facing progress reporting during export
)
from .modules.sheet_formatter import (
    SheetFormatter,  # Utility for applying formatting to spreadsheets (column sizing, word wrapping, conditional formatting, etc.)
)
from .modules.sheet_name_sanitizer import (
    SheetNameSanitizer,  # Utility for sanitizing spreadsheets names
)
from .modules.sheet_writer import (
    SheetWriter,  # Utility for writing DataFrames to spreadsheets, including batching
)


class XlsxDataFrameWriter:
    """Excel export engine with formatting, batching, splitting, and zipping.

    This class manages the full workflow for exporting pandas DataFrames to
    Excel, including sheet sanitization, conditional formatting, batching for
    large datasets, file splitting, ZIP compression, and optional progress
    reporting. Configuration can be supplied via constructor arguments or a
    YAML file, with constructor values taking precedence.

    Args:
        config_path (str | None):
            Optional path to a YAML configuration file.
        output_folder (str | None):
            Directory where Excel and ZIP files are written.
        base_filename (str | None):
            Base name for generated Excel files (without extension).
        log_folder (str | None):
            Directory where log files are written.
        max_size_mb (int | None):
            Maximum file size (MB) before ZIP compression.
        max_sheets_per_file (int | None):
            Maximum number of sheets per Excel file before splitting.
        max_line_length (int | None):
            Maximum character length before applying word wrap.
        header_color (str | None):
            Hex color for header background. Overrides YAML if provided.
        header_font_color (str | None):
            Hex color for header text. Overrides YAML if provided.
        freeze_panes (int | None):
            Number of columns to freeze (Excel freeze panes).
        freeze_rows (int | None):
            Number of rows to freeze.
        enable_progress (bool | None):
            Whether to display tqdm progress bars.
        enable_word_wrap (bool | None):
            Whether to apply word wrapping to cells.
        enable_hit_list (bool | None):
            Whether to apply hit-list conditional formatting.
        hit_list (list[str] | None):
            Keywords to highlight using conditional formatting.
        check_cols (list[str] | None):
            Columns where hit-list highlighting is applied.
        batch_threshold (int | None):
            Row threshold for enabling batched writing.
        batch_size (int | None):
            Number of rows per batch when batching is active.
        disable_logging (bool | None):
            Whether to print logging information to the console. If `true`, logging will be disabled. If `false`, logging will be enabled and printed to the console. Defaults to `true` when left empty.

    Notes:
        - Output and log folders are created automatically.
        - Files are split when sheet or size limits are exceeded.
        - ZIP compression occurs when file size exceeds ``max_size_mb``.
        - Constructor arguments always override YAML configuration values.

    """

    def __init__(
        self,
        config_path: str | None = None,
        output_folder: str | None = None,
        base_filename: str | None = None,
        log_folder: str | None = None,
        max_size_mb: int | None = None,
        max_sheets_per_file: int | None = None,
        max_line_length: int | None = None,
        header_color: str | None = None,
        header_font_color: str | None = None,
        freeze_panes: int | None = None,
        freeze_rows: int | None = None,
        enable_progress: bool | None = None,
        enable_word_wrap: bool | None = None,
        enable_hit_list: bool | None = None,
        hit_list: list[str] | None = None,
        check_cols: list[str] | None = None,
        batch_threshold: int | None = None,
        batch_size: int | None = None,
        enable_logging: bool | None = None,
    ) -> None:

        # 1. Load YAML config if provided
        cfg = ConfigLoader(config_path)

        # 2. Define all fields in one place
        fields = [
            ("output_folder", output_folder, "output"),
            ("base_filename", base_filename, "export"),
            ("log_folder", log_folder, "logs"),
            ("max_size_mb", max_size_mb, 25),
            ("max_sheets_per_file", max_sheets_per_file, 20),
            ("enable_progress", enable_progress, False),
            ("enable_word_wrap", enable_word_wrap, True),
            ("max_line_length", max_line_length, 50),
            ("header_color", header_color, "#F2F2F2"),
            ("header_font_color", header_font_color, "#595959"),
            ("freeze_panes", freeze_panes, 1),
            ("freeze_rows", freeze_rows, 1),
            ("enable_hit_list", enable_hit_list, True),
            ("hit_list", hit_list, []),
            ("check_cols", check_cols, []),
            ("batch_threshold", batch_threshold, 50_000),
            ("batch_size", batch_size, 50_000),
            ("enable_logging", enable_logging, True),
        ]

        # 3. Initialize each field using the explicit value if provided; otherwise use cfg[name] or the default
        for name, value, default in fields:
            setattr(self, name, value if value is not None else cfg.get(name, default))

        # Disable logging if explicitly set to False (default is True)
        if not self.enable_logging:
            logging.disable(logging.CRITICAL)

        # 4. Log YAML config (safe)
        logging.debug("Loaded YAML configuration:\n" + yaml.dump(cfg, sort_keys=False))

        # 5. Ensure folders exist BEFORE initializing logger
        self.output_folder = self.check_create_output_folder()

        # 6. Initialize logger (now folder exists)
        self.logger = LoggerManager(self.output_folder)

        # 7. Initialize sheet name sanitizer (if extracted)
        self.sanitizer = SheetNameSanitizer()

        # 8. Initialize DataFrame registry
        self.registry = DataFrameRegistry(self.sanitizer.sanitize)

        # 9. Internal state
        self.dataframes = self.registry.dataframes

        # 10. Initialize cleaner
        self.cleaner = DataCleaner()

        # 11. Initialize conditional formatter
        self.formatter = ConditionalFormatter(self.header_color, self.header_font_color)

        # 12. Initialize progress reporter
        self.progress = ProgressReporter(
            enable_hit_list=self.enable_hit_list,
            hit_list=self.hit_list,
            check_cols=self.check_cols,
            enable_word_wrap=self.enable_word_wrap,
            dataframes_ref=self.registry.dataframes,
        )

        # 13. Initialize post-processor
        self.post_processor = PostProcessor(self.max_size_mb)

        # 14. Initialize filename builder
        self.filename_builder = FilenameBuilder(
            base_filename=self.base_filename,
            output_folder=self.output_folder,
        )

        # 15. Initialize sheet formatter
        self.sheet_formatter = SheetFormatter(
            enable_hit_list=self.enable_hit_list,
            freeze_panes=self.freeze_panes,
            freeze_rows=self.freeze_rows,
            max_line_length=self.max_line_length,
            enable_word_wrap=self.enable_word_wrap,
            conditional_formatter=self.formatter,
            hit_list=self.hit_list,
            check_cols=self.check_cols,
        )

        # 16. Initialize sheet writer
        self.sheet_writer = SheetWriter(
            batch_threshold=self.batch_threshold,
            batch_size=self.batch_size,
            progress=self.progress,
        )

    # -------------------------------------------------------------------------
    # Alternative constructor from YAML config
    # -------------------------------------------------------------------------
    @classmethod
    def from_yaml(cls, config_path: str) -> "XlsxDataFrameWriter":
        """Create an exporter from a YAML configuration file.

        Args:
            config_path (str): Path to the YAML config file.

        Returns:
            XlsxDataFrameWriter: A configured exporter instance.

        """
        return cls(config_path=config_path)

    # -------------------------------------------------------------------------
    # Output folder creation
    # -------------------------------------------------------------------------
    def check_create_output_folder(self) -> str:
        """Validate, create, and prepare the output directory.

        Resolves the configured output folder to an absolute path, ensures the
        directory exists, verifies that it is writable, and initializes the log
        folder inside it. If the path exists but is a file, or if the directory
        is not writable, an exception is raised.

        Returns (str):
                The absolute path to the validated output directory.

        Raises:
            NotADirectoryError:
                If the resolved output path exists but is a file instead of a
                directory.
            PermissionError:
                If the output directory exists but is not writable by the current
                process.

        """
        folder = os.path.abspath(self.output_folder)

        # Path exists but is a file → invalid
        if os.path.isfile(folder):
            raise NotADirectoryError(
                f"Output path '{folder}' exists but is a file, not a directory."
            )

        # Create directory if missing
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        # Check write permissions
        if not os.access(folder, os.W_OK):
            raise PermissionError(
                f"Output folder '{folder}' is not writable. "
                "Check permissions or choose another directory."
            )

        # Create log folder inside output folder
        self.log_folder = os.path.join(folder, "log")
        os.makedirs(self.log_folder, exist_ok=True)

        return folder

    # -------------------------------------------------------------------------
    # Add DataFrame(s) to the exporter (delegates to registry)
    # -------------------------------------------------------------------------
    def add_df(self, df: pd.DataFrame, sheet_name: str) -> None:
        """Register a single DataFrame for export.

        Args:
            df (pd.DataFrame): The DataFrame to add.
            sheet_name (str): Name of the sheet to associate with the DataFrame.

        """
        self.registry.add_df(df, sheet_name)

    def add_dfs(self, data: Any) -> None:
        """Register multiple DataFrames for export.

        Args:
            data (Any): A mapping or iterable of DataFrames to add.

        """
        self.registry.add_dfs(data)

    # -------------------------------------------------------------------------
    # Public method to show sheet names (delegates to registry)
    # -------------------------------------------------------------------------
    def list_sheet_names(self, verbose: bool = False):
        """Return registered sheet names.

        Args:
            verbose (bool): Whether to include detailed output.

        Returns:
            list[str]: The list of registered sheet names.

        """
        return self.registry.list_sheet_names(verbose)

    # -------------------------------------------------------------------------
    # Sync writing
    # -------------------------------------------------------------------------
    def _write_sync(self) -> dict[str, Any]:
        """Write Excel files synchronously and return the final result.

        This method processes all registered DataFrames, splits them into
        groups based on ``max_sheets_per_file``, writes each group to an
        Excel file, performs post-processing (such as ZIP compression),
        and returns the status dictionary for the last generated file.

        Returns:
            dict[str, Any]: A status dictionary describing the last written
            file, including fields such as file path, ZIP path (if compressed),
            and file size.

        """
        file_index = 1
        sheet_items = list(self.dataframes.items())
        result = {}

        for i in range(0, len(sheet_items), self.max_sheets_per_file):
            chunk = sheet_items[i : i + self.max_sheets_per_file]
            filename = self.filename_builder.build(file_index)
            file_index += 1

            logging.info(f"Writing {len(chunk)} sheets to {filename}")

            self._write_single_file(filename, chunk)
            result = self.post_processor.process(filename)
        return result

    # -------------------------------------------------------------------------
    # Write a single Excel file
    # -------------------------------------------------------------------------
    def _write_single_file(
        self, filename: str, sheets: list[tuple[str, pd.DataFrame]]
    ) -> None:
        """Write a single Excel file, using batching for large DataFrames.

        This method preserves the fast path (df.to_excel) for normal-sized
        DataFrames, but automatically switches to batched row writing when a
        sheet exceeds ``batch_threshold``. This prevents memory spikes and
        improves performance for very large exports.

        Args:
            filename (str): Full path of the Excel file to create.
            sheets (list[tuple[str, pd.DataFrame]]): List of (sheet_name, df) pairs.

        Returns:
            None.

        """
        with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
            workbook = writer.book

            # Create shared formats once per file
            (
                header_format,
                wrap_left_format,
                left_format,
                url_format,
                highlight_format,
            ) = self.formatter.create_formats(workbook)

            iterator = (
                tqdm(sheets, desc="Writing sheets") if self.enable_progress else sheets
            )

            for count, (sheet_name, df) in enumerate(iterator, start=1):
                df = self.cleaner.clean_dataframe(df)

                # Determine batch count BEFORE calling inform_user
                batch_count = (
                    1
                    if len(df) <= self.batch_threshold
                    else math.ceil(len(df) / self.batch_size)
                )

                # Inform user once per sheet
                self.progress.report(
                    df=df,
                    sheetname=sheet_name,
                    count=count,
                    batches=[None] * batch_count,
                )

                # Do not log here; instead, store the message in the progress reporter
                logging.info(self.progress.last_sheet_message)

                # ---------------------------------------------------------
                # WRITE DATA (fast path or batched)
                # ---------------------------------------------------------
                ws = self.sheet_writer.write(
                    workbook=workbook,
                    sheet_name=sheet_name,
                    df=df,
                    wrap_left_format=wrap_left_format,
                    header_format=header_format,
                    count=count,
                )

                self.sheet_formatter.apply_shared_formatting(
                    worksheet=ws,
                    df=df,
                    wrap_left_format=wrap_left_format,
                    left_format=left_format,
                    highlight_format=highlight_format,
                )
