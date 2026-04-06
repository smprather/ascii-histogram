# Changelog

All notable changes to this project will be documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
  `reduce_num_buckets_till_n_percent_in_edge()` — auto bucket-count tuning
- `ascii-histogram` CLI built with [Click](https://click.palletsprojects.com/)
  and [rich-click](https://github.com/ewels/rich-click) with options:
  `--num-buckets`, `--bucket-size`, `--middle-value`, `--max-bar-width`,
  `--columns`, `--label`, `--units`, `--stats`
- `uv pip install .` compatible packaging via [hatchling](https://hatch.pypa.io/)
  with `src/` layout
