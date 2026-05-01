# AGENTS.md — ascii-histogram project context

Compressed project knowledge for agentic sessions. Read this instead of the
source when re-familiarising after a context loss.

---

## Identity

| | |
|---|---|
| **Repo** | https://github.com/smprather/ascii-histogram |
| **Language** | Python ≥ 3.14 |
| **Package name** | `ascii-histogram` (PyPI) / `ascii_histogram` (import) |
| **CLI command** | `ascii-histogram` |
| **Version** | 0.1.0 (unreleased; next meaningful bump when auto-sizing ships as stable) |
| **License** | MIT © 2026 Myles Prather |
| **Build backend** | hatchling, src layout |
| **Package manager** | uv |

---

## Repository layout

```
src/ascii_histogram/
  __init__.py       re-exports: Histogram, DataSet, Stats
  core.py           all library logic (no I/O except read_data_file)
  cli.py            Click/rich-click entry point, calls core only

main.py             shim: from ascii_histogram.cli import main
histogram_core.py   shim: re-exports from ascii_histogram.core (compat)

pyproject.toml      hatchling build, scripts entry point, deps
uv.lock             locked deps
README.md           user-facing docs
CHANGELOG.md        keep-a-changelog format; [Unreleased] section active
CONTRIBUTING.md     dev setup, verify-changes recipe
AGENTS.md           ← this file
```

---

## Dependencies (runtime)

```
click>=8.3.2
rich>=14.3.3
rich-click>=1.9.7   # wraps click decorators; USE_RICH_MARKUP=True in cli.py
```

No numpy. All math is pure Python.

---

## Core library — `src/ascii_histogram/core.py`

### Module-level helpers

```python
_nice_ceil(x: float) -> float
```
Rounds `x` **up** to the nearest value in {1, 2, 5} × 10ᵏ.
Uses `+1e-9` epsilon on comparisons to guard float imprecision.
Returns `1.0` for `x <= 0`.

```python
_next_odd(n) -> int
```
Returns `n` if odd, `n+1` if even (used to keep `num_buckets` symmetric).

```python
_pad_and_justify(s, width, justify) -> str
```
String padding helper. `justify` first char: `l`/`r`/`c`.

---

### class `Stats`

```python
Stats(data_set, sum_=None)
```
Computes mean, sigma (sample std dev), sigma_high, sigma_low.
`sigma_high`/`sigma_low` are one-sided standard deviations for values
≥ mean and < mean respectively (asymmetric spread measure).

Attributes: `.mean`, `.sigma`, `.sigma_high`, `.sigma_low`

---

### class `DataSet(list)`

```python
DataSet(data_set, label="", units="", scale=1.0)
```
A `list` of floats with metadata + pre-computed stats.
`scale` multiplies every value at construction time.
Raises `ValueError` on Inf/NaN.

Attributes: `.label`, `.units`, `.mean`, `.sigma`, `.sigma_high`, `.sigma_low`

Internal: `_recalc_stats(total=None)` — re-runs Stats; call if you mutate
the list directly (unusual).

---

### class `Histogram`

```python
Histogram(num_buckets=15, bucket_size=10, middle_value=0.0, max_bar_height=20)
```

**Bucket geometry:**
```
_min_edge = middle_value - bucket_size/2 - (num_buckets-1)/2 * bucket_size
_max_edge_of_min_bucket = _min_edge + bucket_size          ← overflow boundary
_min_edge_of_max_bucket = _min_edge + (num_buckets-1) * bucket_size  ← overflow boundary
```
- Bucket 0 (index 0): catches everything **below** `_max_edge_of_min_bucket` → displayed as `-Inf -> X`
- Bucket N-1 (index -1): catches everything **above** `_min_edge_of_max_bucket` → displayed as `X -> +Inf`
- Middle bucket index: `(num_buckets-1) // 2`, centred on `middle_value`

**Clean-edge invariant (maintained by `auto_size`):**
`middle_value ≡ bucket_size/2  (mod bucket_size)`
⟹ all edges are exact multiples of `bucket_size`.

#### Static methods

```python
Histogram.snap_to(value, ref_value, interval) -> float
# = round((value - ref_value) / interval) * interval + ref_value

Histogram.read_data_file(file_name, columns=None) -> list[list[float]]
# columns: 1-based list, default [1]. Returns one list per column.
# Skips blank lines. Each token split on whitespace.

Histogram.to_SI(f, decimal_places=3, degree=None) -> str
# Formats with SI prefix. prefixes = [' ','k','M','G','T','P','E','Z','Y','y','x','a','f','p','n','u','m']

Histogram.get_degree(f) -> int          # round(log10(|f|))
Histogram.get_SI_degree(f) -> int       # floor((log10(|f|)+1)/3)
```

#### `Histogram.auto_size(data, min_buckets=21, bucket_size=None, middle_value=None, trim_empty_edges=True)`

**Returns:** `(bucket_size, num_buckets, middle_value)` — any non-None arg is pinned.

**Algorithm:**
```
1. Sort data. Compute pct() via linear interpolation.
2. bulk_range = pct(90) - pct(10)
   fallback: pct(95)-pct(5), then sd[-1]-sd[0], then 0
3. IF bucket_size is None:
     bucket_size = 1.0 if bulk_range==0 else _nice_ceil(bulk_range / min_buckets)
4. IF middle_value is None:
     if bulk_range==0: middle_value = float(sd[0])
     else: middle_value = round((median - bucket_size/2) / bucket_size) * bucket_size
                          + bucket_size/2
     # This satisfies the clean-edge invariant.
5. IF bulk_range==0: num_buckets = 1
   ELSE: n_interior = ceil(bulk_range / bucket_size)
         num_buckets = max(min_buckets, _next_odd(n_interior + 4))
         # +4 = 2 edge overflow + 2 cushion
6. IF trim_empty_edges is True AND middle_value was not explicit:
     Shift middle_value to collapse empty interior buckets adjacent to ±Inf.
```

**Outlier handling:** outliers naturally land in edge buckets (step 5 ignores them entirely). `num_buckets` is NEVER inflated for outliers.

**Corner case — all identical values:** `bulk_range=0` → `bucket_size=1.0`, `num_buckets=1`, `middle_value=sd[0]`.

#### Instance methods

```python
h << data_set                    # appends to h.data_sets; returns h (chainable)
h.global_min() -> float          # min across all data_sets
h.global_max() -> float          # max across all data_sets
h.bucketize()                    # populates self.bucket_sets; must be called before
                                 # accessing _min_edge etc. (gen_histogram calls it)
h.gen_histogram() -> str         # calls bucketize(); returns formatted string + trailing \n
```

**`gen_histogram` output format** (per dataset: 3 extra cols — count, pct%, bar):
```
  -Inf ->   -75   842  6.0% ************
   -75 ->   -70   128  0.9% *
   ...
    40 -> +Inf  1352  9.7% ********************
```
- Col 0: left edge (right-justified)
- Col 1: `->` (right-justified)
- Col 2: right edge (right-justified)
- Per dataset: count (right), pct% (right), `*` bar (left)
- `bucket_edge_format`: decimal places = `max(0, -floor(log10(bucket_size)))`;
  integer results returned as `int` (no `.0`)

```python
h.reduce_num_buckets_till_n_percent_in_edge(n, reduce_per_iter=2, min_buckets=3)
h.increase_num_buckets_till_n_percent_in_edge(n, increase_per_iter=2, max_buckets=30, print_dots=True)
# Both print '.' to stdout during iteration. Not used by auto_size.
# WARNING: increase_num_buckets... is unsuitable for outlier-heavy data
#          (it tries to shrink edge buckets, which outliers always fill).
#          Use auto_size instead.
```

---

## CLI — `src/ascii_histogram/cli.py`

Entry point: `ascii_histogram.cli:main`

```
ascii-histogram [OPTIONS] FILE
```

| Option | Short | Default | Notes |
|---|---|---|---|
| `--min-buckets` | `-n` | `21` | Drives auto_size min_buckets |
| `--bucket-size` | `-s` | None | Float; if given, pinned in auto_size |
| `--middle-value` | `-m` | None | Float; if given, pinned in auto_size |
| `--max-bar-width` | `-b` | `20` | Passed as max_bar_height to Histogram |
| `--columns` | `-c` | `"1"` | Comma-separated 1-based indices |
| `--label` | `-l` | — | Multiple; default `colN` |
| `--units` | `-u` | `""` | Appended to stats values |
| `--stats` | — | False | Prints mean/sigma/etc per dataset to stdout |
| `--trim-edges` | — | True | Shift window to eliminate empty edge buckets |

**Flow:**
1. Parse `columns` → `cols: list[int]`
2. `Histogram.read_data_file(file, columns=cols)` → `raw_sets`
3. `combined = [x for raw in raw_sets for x in raw]`  ← all columns pooled for auto_size
4. `Histogram.auto_size(combined, min_buckets, bucket_size, middle_value, trim_empty_edges=trim_edges)` → finals
5. Echo `[auto] bucket_size=..., num_buckets=..., middle_value=...` to **stderr**
6. Build `Histogram(num_buckets, bucket_size, middle_value, max_bar_height=max_bar_width)`
7. Build `DataSet` per column, `h << ds`
8. Print `Min:`, `Max:`, `h.gen_histogram()` to stdout
9. If `--stats`: print stats block per dataset to stdout

**Multi-column note:** all columns share the same bucket geometry (derived from
combined data). This only makes sense when columns are in comparable units.

---

## Key design decisions (rationale preserved)

| Decision | Rationale |
|---|---|
| Auto-size uses q10–q90, not min/max or std dev | Robust to extreme outliers without needing explicit outlier removal |
| `_nice_ceil` uses {1,2,5}×10ᵏ, not all powers-of-10 | Powers-of-10 only (e.g. raw=5.1→10) is too coarse; {1,2,5} gives much better texture |
| `middle_value ≡ bucket_size/2 (mod bucket_size)` | Ensures all edges land on exact multiples of bucket_size (not half-steps) |
| `num_buckets` always odd | Symmetric around `middle_value`; middle bucket is exactly centred |
| `+4` cushion in num_buckets formula | 2 edge overflow buckets + 2 breathing room so bulk data doesn't crowd edges |
| `trim_empty_edges` (default True) | Collapses interior buckets that would be empty because of median-centring but carry no data, tracking the actual data spread better |
| Outliers go to ±Inf edge buckets, never inflate count | Core philosophy: outliers are "accounted for" not "accommodated" |
| No numpy dependency | IQR/percentile is <15 lines of pure Python; keep deps minimal |
| Combined data for multi-column auto_size | Simplest correct behaviour; document that columns should be same-unit |
| `auto_size` params are pinnable individually | Allows partial manual control without losing auto-sizing for the rest |
| `increase_num_buckets_till_n_percent_in_edge` NOT used by CLI | It fights outliers by adding buckets — wrong strategy for this use case |

---

## Build & run

```bash
# Install (editable for dev)
uv pip install -e .

# Run CLI
ascii-histogram data.txt
ascii-histogram data.txt -s 10 -m 0 --stats
ascii-histogram data.txt -n 41           # finer texture

# Run without installing
uv run python main.py data.txt

# Quick test (generate data + run)
python -c "
import random; random.seed(42)
data = [random.gauss(-20,25) for _ in range(1000)]
open('/tmp/t.txt','w').write('\n'.join(f'{v:.3f}' for v in data))
"
ascii-histogram /tmp/t.txt --stats
```

---

## Git history summary

```
a05d90b  docs: update README for edge-trimming feature
86e8e75  Add edge-trimming to auto_size; add latency test dataset
5007c19  Add AGENTS.md: compressed project knowledge for agentic sessions
eb9a807  Fix docs: remove stale duplicate content, update CONTRIBUTING examples
84f75c8  Add auto-sizing: IQR-based bucket_size, clean edges, smart num_buckets
```

---

## Current status & potential next work

**Done:**
- Full port from Ruby; all original functionality preserved
- Auto-sizing (the hard problem) — solved and working well
- Edge-trimming to eliminate empty interior buckets
- `uv pip install .` compatible packaging
- Rich-click CLI with good help output
- README, CHANGELOG, CONTRIBUTING all clean

**Known minor quirk:**
- All-identical-values corner case: `num_buckets=1` produces a single row
  showing `X -> +Inf  N 100%` (the `-Inf` label gets overwritten by the
  last-bucket edge label when index 0 == index -1). Cosmetic only.

**Potential future work (not started):**
- `--output-format json` for machine-readable histogram data
- Pipe support: `cat data.txt | ascii-histogram -` (stdin as FILE)
- `--filter` to exclude outliers above/below a threshold before sizing
- Color output option (rich `Text` rendering of the bar column)
- `uv run ascii-histogram` style entry via `[tool.uv.scripts]`
