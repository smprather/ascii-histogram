# ascii-histogram

A fast, dependency-free ASCII histogram generator for the terminal — as a CLI tool and Python library.

Buckets are **auto-sized by default** using the 10th–90th percentile range of
your data, so extreme outliers never distort the scale — they land in the
`-Inf` / `+Inf` edge buckets instead.  Bucket edges always fall on clean,
human-readable values (exact multiples of the bucket size).

```
[auto] bucket_size=5.0, num_buckets=25, middle_value=-17.5
Min: -4260.5
Max: 5675.8
-Inf ->  -75  842 6.0% ************
 -75 ->  -70  128 0.9% *
 -70 ->  -65  155 1.1% **
 -65 ->  -60  249 1.8% ***
 -60 ->  -55  313 2.2% ****
 -55 ->  -50  418 3.0% ******
 -50 ->  -45  505 3.6% *******
 -45 ->  -40  646 4.6% *********
 -40 ->  -35  791 5.7% ***********
 -35 ->  -30  868 6.2% ************
 -30 ->  -25  880 6.3% *************
 -25 ->  -20  967 6.9% **************
 -20 ->  -15  929 6.6% *************
 -15 ->  -10  881 6.3% *************
 -10 ->   -5  912 6.5% *************
  -5 ->    0  701 5.0% **********
   0 ->    5  653 4.7% *********
   5 ->   10  515 3.7% *******
  10 ->   15  413 2.9% ******
  15 ->   20  322 2.3% ****
  20 ->   25  219 1.6% ***
  25 ->   30  166 1.2% **
  30 ->   35   99 0.7% *
  35 ->   40   76 0.5% *
  40 -> +Inf 1352 9.7% ********************
```

*Data above ranged from −4260 to +5676; the outliers are absorbed in the edge
buckets without stretching the scale.*

---

## Features

- **Auto-sized by default** — bucket width and placement derived from the bulk
  of the data (10th–90th percentile); no manual tuning required
- **Outlier-proof** — extreme values land in `±Inf` edge buckets and never
  inflate the bucket count or width
- **Clean edges** — bucket boundaries always fall on exact multiples of the
  bucket size (e.g. −75, −70, −65…, not −77.5, −72.5…)
- **Middle-anchored** — buckets are centred on a reference value derived from
  the median; override with `--middle-value` if needed
- **Multi-dataset side-by-side** — plot several columns from the same file in
  one table
- **Optional statistics** — mean, σ, σ_high, σ_low, min, max per dataset
- **Python library** — embed histograms in your own scripts with a clean API
- **Installable CLI** — `uv pip install .` drops an `ascii-histogram` command
  on your `PATH`

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

The auto-chosen `bucket_size`, `num_buckets`, and `middle_value` are always
printed to **stderr** so you can see exactly what was used and reproduce the
result manually if needed.

### Options

| Option | Short | Default | Description |
|---|---|---|---|
| `--min-buckets` | `-n` | `21` | Minimum number of buckets; the primary auto-sizing knob |
| `--bucket-size` | `-s` | *(auto)* | Bucket width — auto-sized when omitted |
| `--middle-value` | `-m` | *(auto)* | Centre bucket value — derived from the median when omitted |
| `--max-bar-width` | `-b` | `20` | Maximum bar width in characters |
| `--columns` | `-c` | `1` | Comma-separated 1-based column indices |
| `--label` | `-l` | — | Dataset label (repeat for multiple columns) |
| `--units` | `-u` | — | Units suffix appended to statistics values |
| `--stats` | | | Print per-dataset statistics after the histogram |
| `--help` | | | Show help and exit |

### Examples

```bash
# Fully automatic — just point at a file
ascii-histogram data.txt

# Force a specific bucket width (middle_value still auto-derived)
ascii-histogram data.txt --bucket-size 10

# Pin centre and width explicitly
ascii-histogram data.txt --bucket-size 10 --middle-value 0

# Increase minimum bucket count for finer texture
ascii-histogram data.txt --min-buckets 41

# Label a dataset and print statistics
ascii-histogram data.txt --label "latency" --units ms --stats

# Two columns side-by-side
ascii-histogram data.txt --columns 1,2 --label "before" --label "after" --units ms
```

---

## Python API

```python
from ascii_histogram import Histogram, DataSet

# Read a whitespace-delimited file (returns one list per column)
raw = Histogram.read_data_file("data.txt", columns=[1])

# Auto-size bucket parameters from the data
bucket_size, num_buckets, middle_value = Histogram.auto_size(raw[0], min_buckets=21)

# Build a histogram
h = Histogram(num_buckets=num_buckets, bucket_size=bucket_size, middle_value=middle_value)
h << DataSet(data_set=raw[0], label="latency", units="ms")

print(f"min={h.global_min()}  max={h.global_max()}")
print(h.gen_histogram())
```

### `Histogram.auto_size(data, min_buckets=21, bucket_size=None, middle_value=None)`

Returns `(bucket_size, num_buckets, middle_value)`.  Any non-`None` argument
is treated as fixed; the rest are derived automatically.

| Parameter | Strategy |
|---|---|
| `bucket_size` | `nice_ceil((q90 − q10) / min_buckets)` — rounded up to nearest {1, 2, 5} × 10ᵏ |
| `middle_value` | Median snapped so bucket *edges* land on exact multiples of `bucket_size` |
| `num_buckets` | Covers q10–q90 with cushion; always ≥ `min_buckets` and always odd |

Falls back to wider percentiles (q5–q95, then full range) when the central
band is zero-width, and to a single bucket when all values are identical.

### `Histogram` constructor

```python
Histogram(
    num_buckets: int    = 15,
    bucket_size: float  = 10,
    middle_value: float = 0.0,
    max_bar_height: int = 20,   # max bar width in characters
)
```

### `DataSet` constructor

```python
DataSet(
    data_set,            # iterable of numbers
    label: str   = "",
    units: str   = "",
    scale: float = 1.0,  # multiply every value by this before storing
)
```

After construction a `DataSet` exposes: `.mean`, `.sigma`, `.sigma_high`,
`.sigma_low`.

### Bucket-count tuning helpers

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
    core.py       # Histogram, DataSet, Stats classes + auto_size
    cli.py        # Click/rich-click CLI entry point
main.py           # dev shim → ascii_histogram.cli:main
histogram_core.py # compat shim → ascii_histogram.core
pyproject.toml
uv.lock
```

---

## License

MIT © 2026 Myles Prather — see [LICENSE](LICENSE).
