# SPDX-License-Identifier: MIT
from importlib.metadata import PackageNotFoundError, version

# Main module for dfs_to_xlsx package
from dfs_to_xlsx.xlsx_writer import XlsxDataFrameWriter

try:
    __version__ = version("dfs-to-xlsx")
except PackageNotFoundError:
    __version__ = "0.0.0"
