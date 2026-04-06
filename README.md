# ascii-histogram

A fast, dependency-free ASCII histogram generator for the terminal — as a CLI tool and Python library.

Buckets are aligned to a **middle value** (default `0.0`), so bins always land on clean, human-readable boundaries regardless of the data range. Edge buckets absorb overflow, so no data point is ever dropped.

```
 -Inf -> -90.0  664  4.7% ******
-90.0 -> -80.0  245  1.7% **
-80.0 -> -70.0  184  1.3% *
-70.0 -> -60.0   40  0.3%
-60.0 -> -50.0   42  0.3%
-50.0 -> -40.0  176  1.2% *
-40.0 -> -30.0  938  6.6% ********
-30.0 -> -20.0 2189 15.4% ********************
-20.0 -> -10.0 1883 13.3% *****************
-10.0 ->   0.0 1851 13.0% ****************
  0.0 ->  10.0 1166  8.2% **********
 10.0 ->  20.0  733  5.2% ******
 20.0 ->  30.0  639  4.5% *****
 30.0 ->  40.0  554  3.9% *****
 40.0 ->  50.0  386  2.7% ***
 50.0 ->  60.0  350  2.5% ***
 60.0 ->  70.0  154  1.1% *
 70.0 ->  80.0   58  0.4%
 80.0 ->  90.0   43  0.3%
 90.0 ->  +Inf 1907 13.4% *****************
```

---

## Features

- **Middle-anchored buckets** — bins are centred on a reference value, so edges land on round numbers
- **Overflow buckets** — `-Inf` and `+Inf` edge rows capture every data point
- **Multi-dataset side-by-side** — plot several columns from the same file in one table
- **Optional statistics** — mean, σ, σ_high, σ_low, min, max per dataset
- **Python library** — embed histograms in your own scripts with a clean API
- **Installable CLI** — `uv pip install .` drops an `ascii-histogram` command on your `PATH`

---

## Installation

**Requires Python ≥ 3.14.**

```bash
# from the repo root
uv pip install .
```

For development (editable install):

```bash
uv pip install -e .
```

Or run directly without installing:

```bash
uv run python main.py data.txt
```

---

## CLI Usage

```
ascii-histogram [OPTIONS] FILE
```

`FILE` must be a whitespace-delimited text file with one observation per row.  
Multiple columns are supported — see `--columns`.

### Options

| Option | Short | Default | Description |
|---|---|---|---|
| `--num-buckets` | `-n` | `31` | Number of buckets |
| `--bucket-size` | `-s` | `10.0` | Width of each bucket |
| `--middle-value` | `-m` | `0.0` | Value aligned to the centre of the middle bucket |
| `--max-bar-width` | `-b` | `20` | Maximum bar width in characters |
| `--columns` | `-c` | `1` | Comma-separated 1-based column indices |
| `--label` | `-l` | — | Label for a dataset column (repeat for multiple) |
| `--units` | `-u` | — | Units string appended to statistics values |
| `--stats` | | | Print per-dataset statistics after the histogram |
| `--help` | | | Show help and exit |

### Examples

```bash
# Basic — column 1, bucket width 10, centred on 0
ascii-histogram data.txt

# Customise buckets
ascii-histogram data.txt --num-buckets 20 --bucket-size 5 --middle-value 0

# Label a dataset and print statistics
ascii-histogram data.txt --label "latency" --units ms --stats

# Two columns side-by-side from the same file
ascii-histogram data.txt --columns 1,2 --label "before" --label "after" --units ms --stats
```

---

## Python API

```python
from ascii_histogram import Histogram, DataSet

# Read a whitespace-delimited file (returns one list per column)
raw = Histogram.read_data_file("data.txt", columns=[1])

# Build a histogram
h = Histogram(num_buckets=20, bucket_size=10, middle_value=0.0, max_bar_height=20)
h << DataSet(data_set=raw[0], label="latency", units="ms")

print(f"min={h.global_min()}  max={h.global_max()}")
print(h.gen_histogram())
```

### `Histogram` constructor

```python
Histogram(
    num_buckets: int   = 15,   # number of buckets
    bucket_size: float = 10,   # width of each bucket
    middle_value: float = 0.0, # value at the centre of the middle bucket
    max_bar_height: int = 20,  # max bar width in characters
)
```

### `DataSet` constructor

```python
DataSet(
    data_set,        # iterable of numbers
    label: str = "", # human-readable name
    units: str = "", # units suffix for display
    scale: float = 1.0, # multiply every value by this before storing
)
```

After construction a `DataSet` exposes: `.mean`, `.sigma`, `.sigma_high`, `.sigma_low`.

### Bucket-sizing helpers

```python
# Grow num_buckets until edge buckets each hold < n% of data
h.increase_num_buckets_till_n_percent_in_edge(n=5, max_buckets=40)

# Shrink num_buckets until an edge bucket holds > n% of data
h.reduce_num_buckets_till_n_percent_in_edge(n=5, min_buckets=3)
```

---

## Project layout

```
src/
  ascii_histogram/
    __init__.py   # public re-exports
    core.py       # Histogram, DataSet, Stats classes
    cli.py        # Click/rich-click CLI entry point
main.py           # dev shim → ascii_histogram.cli:main
histogram_core.py # compat shim → ascii_histogram.core
pyproject.toml
uv.lock
```

---

## License

MIT © 2026 Myles Prather — see [LICENSE](LICENSE).

