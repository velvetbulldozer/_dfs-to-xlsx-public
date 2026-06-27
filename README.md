<div align="center">
  <img src="https://github.com/velvetbulldozer/_dfs-to-xlsx-public/raw/f56e9284543d37add078637e666bfe3f497748c5/image.svg" alt="dfs-to-xlsx Logo">
</div>

---
# Table of contents | **dfs-to-xlsx**

- [Table of contents | **dfs-to-xlsx**](#table-of-contents--dfs-to-xlsx)
- [What does it do?](#what-does-it-do)
  - [🚀 Installation](#-installation)
  - [⚙️ Use **YAML-config file** or use parameters on instantiation](#️-use-yaml-config-file-or-use-parameters-on-instantiation)
  - [📦 Basic Usage  — All Parameters](#-basic-usage---all-parameters)
        - [✔ What the example does](#-what-the-example-does)
      - [📄 Single DataFrame](#-single-dataframe)
        - [✔ What the example does](#-what-the-example-does-1)
      - [📄 Multiple DataFrames](#-multiple-dataframes)
        - [✔ What the example does](#-what-the-example-does-2)
      - [📚 Multiple DataFrames — Input Styles](#-multiple-dataframes--input-styles)
      - [🧩 Batching Large DataFrames](#-batching-large-dataframes)
      - [🗜 Automatic ZIP Compression](#-automatic-zip-compression)
      - [🎨 Hit List Highlighting (Conditional Formatting)](#-hit-list-highlighting-conditional-formatting)
      - [📁 Logging](#-logging)
      - [•••·· Monitoring progress](#-monitoring-progress)
- [📝 Package Info and Quality](#-package-info-and-quality)

---

# What does it do?
`dfs-to-xlsx` provides a clean API for exporting one or many DataFrames to Excel. A fast, flexible, and feature-rich Excel exporter for **multiple pandas DataFrames** to an **Excel spreadsheet**. It lets you export one or many pandas DataFrames into a clean, well‑formatted Excel workbook — with zero boilerplate.

✨ Key Features:

- Export multiple DataFrames into a single Excel file with multiple tabs.
- Automatic sheet‑name sanitization
- Clean formatting:
  - Word wrapping
  - Maximum column width
  - Header styling
  - Frozen panes
- Conditional formatting via hit‑lists
- Batching for large DataFrames
- Automatic ZIP compression for oversized files
- Optional progress bar
- Optional logging
- YAML‑based configuration or full programmatic control

---
## 🚀 Installation
In your virtual env:
```bash
# Install with pip
pip install dfs-to-xlsx

# Or install with uv
uv add dfs-to-xlsx
```
You can verify which version of **dfs_to_xlsx** is installed:
```python
import dfs_to_xlsx
print(dfs_to_xlsx.__version__)
```
This is useful when debugging, reporting issues, or confirming that an upgrade succeeded.

---
## ⚙️ Use **YAML-config file** or use parameters on instantiation
Two approaches:
 1. Add YAML-config file to the root of your project in `config.yaml`
 2. Or use parameters in the class instantiation — see paragraph [📦 Basic Usage](#-basic-usage---all-parameters)

```yaml
# Parameters:

# output_folder: The directory where output files will be saved. Defaults to `output` when left empty.
output_folder: "output"

# base_filename: The base name for output files. Defaults to 'export' when left empty.
base_filename: "report"

# log_folder: The path to the log file where processing logs will be saved. If left empty, logging will be disabled.
log_folder: "output/log/"

# max_size_mb: The maximum file size in megabytes before splitting or compressing. Defaults to `25` mb when left empty.
max_size_mb: 25

# max_sheets_per_file: The maximum number of sheets allowed in a single Excel file before splitting. Defaults to `20` sheets when left empty.
max_sheets_per_file: 20

# enable_progress: Whether to display a progress bar during pipeline processing. Defaults to `true` when left empty.
enable_progress: false

# enable_word_wrap: Whether to enable word wrapping in Excel cells. Defaults to `true` when left empty.
enable_word_wrap: true

# max_line_length: The maximum line length for cell content before truncation or wrapping. Defaults to `50` characters when left empty. Setting this parameter helps prevent excessively wide columns in Excel, which can improve readability and performance when dealing with large datasets.
max_line_length: 50

# header_color: The background color for header rows in Excel sheets, specified in hexadecimal format. Defaults to `#D9D9D9` (a light grey) when left empty. This parameter allows you to customize the appearance of header rows for better visual distinction from data rows.
header_color: "#F2F2F2"

# header_font_color: The font color for header rows in Excel sheets, specified in hexadecimal format. Defaults to `#595959` (a dark grey) when left empty. This parameter ensures that the text in header rows is clearly visible against the specified `header_color`, enhancing readability.
header_font_color: "#595959"

# freeze_panes: The number of columns to freeze at the left of each sheet. Defaults to `1` when left empty. This means the first column will be frozen, allowing it to remain visible while scrolling horizontally through the data.
freeze_panes: 1

# freeze_rows: The number of rows to freeze at the top of each sheet. Defaults to `1` when left empty, which means the first row (usually the header) will be frozen for easy reference while scrolling through the data
freeze_rows: 1

# enable_hit_list: Whether to apply conditional formatting based on the `hit_list` keywords. Defaults to `true` when left empty. If enabled, cells in the specified `check_cols` that contain any of the keywords in `hit_list` will be highlighted for easy identification.
enable_hit_list: false

# batch_threshold: The number of rows at which to start batching. Defaults to `50000` rows when left empty.
batch_threshold: 50000

# batch_size: The number of rows to include in each batch when batching is enabled. Defaults to `5000` rows when left empty. If the total number of rows exceeds `batch_threshold`, the DataFrame will be split into batches of this size for processing, which can help manage memory usage and improve performance when dealing with large datasets.
batch_size: 5000

# hit_list: A list of keywords to check for in specified columns. If `enable_hit_list` is true, cells containing any of these keywords will be highlighted.
hit_list:
  - "error"
  - "warning"
  - "failed"

# check_cols: A list of column names to check for the presence of `hit_list` keywords when `enable_hit_list` is true.
check_cols:
  - "comments"
  - "status"

# enable_logging: Whether to write logs to a file and show as output. Defaults to `true` when left empty.
enable_logging: true
```

---
## 📦 Basic Usage  — All Parameters
In your script import the writer and config file:
```python
# import package
from dfs_to_xlsx import XlsxDataFrameWriter

# load exporter from YAML config and instantiate
writer = XlsxDataFrameWriter.from_yaml("../config.yaml")

# this works too
writer = XlsxDataFrameWriter("config.yaml")

# or... use parameters on instantiation
writer = XlsxDataFrameWriter(
    config_path=None,  # not used since we're passing config directly
    output_folder="output",
    base_filename="single_export",
    log_folder="output/log/",
    max_size_mb=5,
    max_sheets_per_file=20,
    enable_progress=False,
    enable_word_wrap=True,
    max_line_length= 50,
    header_color= "#F2F2F2", # if left empty this is the default header color
    header_font_color= "#595959", # if left empty this is the default header font color
    freeze_panes= 1,
    freeze_rows= 1, # freezes header
    enable_hit_list=False,
    batch_threshold=50000,
    batch_size=5000,
    hit_list=["error", "warning", "failed"],
    check_cols=["comments", "status"],
    enable_logging=True,
    )
```

##### ✔ What the example does
- Writes all DataFrames into one Excel file
- Automatically sanitizes sheet names
- Creates the output folder if missing
- Generates a clean filename automatically
- Supports maximum file size before auto‑zipping
- Supports maximum sheets per workbook
- Optional progress bar
- Adds each DataFrame to its own sheet
- Applies word‑wrap to keep columns readable
- Optional hit‑list conditional formatting (e.g., highlight “error”, “warning”, “failed”)
- Automatic batching for large DataFrames
- Configurable batch size
- Optional logging of all added DataFrames

---
#### 📄 Single DataFrame

Use ```add_df(df, sheet_name)``` to add one DataFrame to your export:

```python
# use the config file
writer = XlsxDataFrameWriter.from_yaml("config.yaml")

# add single df
writer.add_df(df, "Employees")

# export result
result = writer._write_sync()
```
##### ✔ What the example does
- Uses presets from config.yaml located in root folder
- Adds a single dataframe to spreadsheet
- Exports DataFrame
---
#### 📄 Multiple DataFrames

Use multiple ```add_dfs``` to export multiple DataFrames and use ```all parameters``` on instantiation of the XlsxDataFrameWriter:
```python
# add multiple dfs
writer.add_dfs(
    [
        ("Sales Overview", df_sales),
        ("Customer Status", df_customers),
        ("Large Dataset", df_large),
        ("Wide Dataset", df_wide),
        ("Huge Dataset", df_huge),
        ("Nested Dataset", df_nested),
    ]
)

# show all added dfs, false shows list, true prints names and index
writer.list_sheet_names(True)

# export result
result = writer._write_sync()
```

##### ✔ What the example does
- Adds multiple DataFrames at once, each with its own sheet name
- Shows all added sheets (either as a list or printed with index positions)
- Exports everything into a single Excel file with all configured features applied
---
#### 📚 Multiple DataFrames — Input Styles
You can pass multiple DataFrames to add_dfs in three different formats, depending on what fits your workflow best.

1. Use a dictionary where ```keys = sheet names and values = DataFrames```.
2. Use a list of ```(sheet_name, df)``` tuples.
3. List only style and sheet names will be auto-generated.

```python
# dict style
exporter.add_dfs(
    {
        "Sales Overview": df_sales,
        "Customer Status": df_customers,
        "Large Dataset": df_large,
        "Wide Dataset": df_wide,
        "Huge Dataset": df_huge,
        "Nested Dataset": df_nested,
    }
)

# tuple list style
exporter.add_dfs(
    [
        ("Sales Overview", df_sales),
        ("Customer Status", df_customers),
        ("Large Dataset", df_large),
        ("Wide Dataset", df_wide),
        ("Huge Dataset", df_huge),
        ("Nested Dataset", df_nested),
    ]
)

# list-only style (auto sheet names) are Sheet1, Sheet2, Sheet3, ...
exporter.add_dfs(
    [
        df_sales,
        df_customers,
        df_large,
        df_wide,
        df_huge,
        df_nested,
    ]
)
```
---
#### 🧩 Batching Large DataFrames

If a DataFrame exceeds batch_threshold, it is written in chunks:
```python
# or change values in the import yaml and import the yaml, see above.
writer = XlsxDataFrameWriter(
    output_folder="output",
    batch_threshold=50000,
    batch_size=5000,
)
```
This prevents memory issues and speeds up writing.

---
#### 🗜 Automatic ZIP Compression
If the final Excel file exceeds max_size_mb, it is automatically zipped:
```python
# or change values in the import yaml and import the yaml, see above.
writer = XlsxDataFrameWriter(
    output_folder="output",
    max_size_mb=5,  # MB
)
```
---
#### 🎨 Hit List Highlighting (Conditional Formatting)
Highlight rows containing specific keywords:
``` python
# or change values in the import yaml and import the yaml, see above.
writer = XlsxDataFrameWriter(
    output_folder="output",
    enable_hit_list=True,
    hit_list=["error", "failed", "risk"],
    check_cols=["status", "comments"],
)
```
---
#### 📁 Logging
Enable logging to a file:
```python
# or change values in the import yaml and import the yaml, see above.
writer = XlsxDataFrameWriter(
    output_folder="output",
    log_folder="output/log/",
    enable_logging=True,
)
```
---
#### •••·· Monitoring progress
You can enable or disable logging and the progress bar independently.
This allows you to show **only logging, only the progress bar, both,** or **neither**.
```python
# or change monitoring
writer = XlsxDataFrameWriter(
    enable_progress=False,  # Disable progress bar
    enable_logging=False,  # Disable logging
)
```
---
# 📝 Package Info and Quality
<p align="center">
  <!-- Identity -->
  <img src="https://img.shields.io/badge/License-MIT-green.svg" />
  <img src="https://img.shields.io/pypi/pyversions/dfs-to-xlsx.svg" />
  <img src="https://static.pepy.tech/badge/dfs-to-xlsx" />
</p>
<p align="center">
  <!-- Quality -->
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" />
  <img src="https://img.shields.io/badge/type%20checked-mypy-blue" />
  <img src="https://img.shields.io/pypi/wheel/dfs-to-xlsx" />
  <img src="https://img.shields.io/librariesio/release/pypi/dfs-to-xlsx" />
  <img src="https://img.shields.io/badge/tests-pytest-blue" />
  <img src="https://img.shields.io/badge/lint-ruff-red" />
</p>
<p align="center">
  <!-- Repo activity + Tech -->
  <img src="https://img.shields.io/github/last-commit/velvetbulldozer/_dfs-to-xlsx-public" />
  <img src="https://img.shields.io/github/stars/velvetbulldozer/_dfs-to-xlsx-public" />
  <img src="https://img.shields.io/github/forks/velvetbulldozer/_dfs-to-xlsx-public" />
  <img src="https://img.shields.io/github/issues/velvetbulldozer/_dfs-to-xlsx-public" />
  <img src="https://img.shields.io/badge/powered%20by-pandas-150458.svg" />
  <img src="https://img.shields.io/badge/Excel-217346?logo=microsoft-excel&logoColor=white" />
</p>
