# Contributing

Thanks for your interest in contributing to ascii-histogram!

## Development setup

You will need [uv](https://docs.astral.sh/uv/) and Python ≥ 3.14.

```bash
git clone https://github.com/smprather/ascii-histogram.git
cd ascii-histogram
uv pip install -e .
```

The editable install means changes to `src/ascii_histogram/` take effect
immediately without reinstalling.

## Project layout

```
src/
  ascii_histogram/
    __init__.py   # public re-exports
    core.py       # Histogram, DataSet, Stats — pure library, no I/O
    cli.py        # Click / rich-click entry point
main.py           # dev convenience shim
histogram_core.py # backwards-compat shim
```

Keep the library (`core.py`) free of CLI concerns. Keep the CLI (`cli.py`)
free of histogram logic — it should only parse arguments, call the library,
and print results.

## Verifying changes

Generate some test data and run the tool end-to-end:

```bash
python -c "
import random, math
random.seed(42)
data = [random.gauss(-20, 25) for _ in range(1000)]
with open('/tmp/test.txt', 'w') as f:
    for v in data: f.write(f'{v:.3f}\n')
"
ascii-histogram /tmp/test.txt --stats
```

Check that:
- The `[auto]` line on stderr reports sensible `bucket_size`, `num_buckets`,
  and `middle_value` values
- Bucket edges are clean multiples of `bucket_size`
- Overflow edge buckets (`-Inf` / `+Inf`) hold a small fraction of the data

## Submitting changes

1. Fork the repo and create a branch from `main`.
2. Make your changes with clear, focused commits.
3. Open a pull request describing what changed and why.

## Code style

- Follow PEP 8.
- Keep functions focused — if a method is doing two things, split it.
- Add docstrings to public classes and non-trivial methods.
- No new runtime dependencies without discussion first.
