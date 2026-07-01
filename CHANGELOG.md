# Changelog
All notable changes to **dfs-to-xlsx** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.7.18] - 2026-07-01
### Added
- Updated function naming and readme correspondingly.

## [0.7.14-0.7.17] - 2026-06-27
### Added
- Updated readme.

## [0.7.1-0.7.13] - 2026-06-24
### Added
- Various minor bugfixes.

## [0.6.4] - 2026-05-22
### Added
- Initial public release of `dfs-to-xlsx`.
- `XlsxDataFrameWriter` class with full Excel export pipeline.
- Support for adding DataFrames via:
  - `add_df(df, sheet_name)`
  - `add_dfs([(sheet_name, df), ...])`
- Automatic sheet‑name sanitization.
- Automatic cleaning of nested structures (lists, dicts, tuples).
- Automatic batching for large DataFrames (`batch_threshold`, `batch_size`).
- Automatic ZIP compression for oversized files (`max_size_mb`).
- Conditional formatting via hit list (`enable_hit_list`, `hit_list`, `check_cols`).
- Progress bar support (`enable_progress`).
- Logging support (`enable_logging`, `log_folder`, `log_file`).
- Sync and async export methods:
  - `write()`
  - `write_async()`
- Comprehensive test suite:
  - ZIP compression tests
  - Full pipeline tests
  - Sanitization tests
  - Cleaning tests
- Benchmark suite using `pytest-benchmark`.

