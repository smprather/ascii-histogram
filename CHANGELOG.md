# Changelog

All notable changes to this project will be documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added

- `Histogram.auto_size(data, min_buckets, bucket_size, middle_value)` — derives
  bucket parameters from data using the 10th–90th percentile range; robust to
  outliers, which land in `±Inf` edge buckets without inflating the scale
- `_nice_ceil(x)` — rounds a value up to the nearest number in the
  {1, 2, 5} × 10ᵏ series, guaranteeing human-readable bucket widths
- Bucket edges now snap to exact multiples of `bucket_size` (previously they
  could land at half-steps like −77.5 instead of −75)
- Integer bucket edges displayed without a trailing `.0` (e.g. `−75` not
  `−75.0`); non-integer edges use the minimum decimal places implied by
  `bucket_size`

### Changed

- CLI: `--bucket-size` and `--middle-value` now default to `None` (auto-sized)
  instead of fixed values — fully automatic out of the box
- CLI: `--num-buckets` replaced by `--min-buckets / -n` (default 21); drives
  the auto-sizing target rather than setting an exact count
- CLI always prints auto-chosen parameters to **stderr** so they are visible
  but do not pollute piped output

---

## [0.1.0] — 2026-04-06

### Added

- `Histogram` class with middle-anchored, overflow-safe bucketing
- `DataSet` class — typed list with pre-computed mean, σ, σ_high, σ_low
- `Stats` class — sample standard deviation split into upper/lower halves
- `Histogram.read_data_file()` — whitespace-delimited file reader supporting
  arbitrary column selection (1-based)
- `Histogram.to_SI()` / `get_degree()` / `get_SI_degree()` — SI prefix helpers
- `increase_num_buckets_till_n_percent_in_edge()` and
  `reduce_num_buckets_till_n_percent_in_edge()` — bucket-count tuning helpers
- `ascii-histogram` CLI built with [Click](https://click.palletsprojects.com/)
  and [rich-click](https://github.com/ewels/rich-click)
- `uv pip install .` compatible packaging via [hatchling](https://hatch.pypa.io/)
  with `src/` layout


### Added

- `Histogram` class with middle-anchored, overflow-safe bucketing
- `DataSet` class — typed list with pre-computed mean, σ, σ_high, σ_low
- `Stats` class — sample standard deviation split into upper/lower halves
- `Histogram.read_data_file()` — whitespace-delimited file reader supporting
  arbitrary column selection (1-based)
- `Histogram.to_SI()` / `get_degree()` / `get_SI_degree()` — SI prefix helpers
- `increase_num_buckets_till_n_percent_in_edge()` and
  `reduce_num_buckets_till_n_percent_in_edge()` — auto bucket-count tuning
- `ascii-histogram` CLI built with [Click](https://click.palletsprojects.com/)
  and [rich-click](https://github.com/ewels/rich-click) with options:
  `--num-buckets`, `--bucket-size`, `--middle-value`, `--max-bar-width`,
  `--columns`, `--label`, `--units`, `--stats`
- `uv pip install .` compatible packaging via [hatchling](https://hatch.pypa.io/)
  with `src/` layout
