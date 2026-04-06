# Contributing

Thanks for your interest in contributing to ascii-histogram!

## Development setup

You'll need [uv](https://docs.astral.sh/uv/) and Python ≥ 3.14.

```bash
git clone https://github.com/smprather/ascii-histogram.git
cd ascii-histogram
uv pip install -e .
```

The editable install means changes to `src/ascii_histogram/` take effect immediately without reinstalling.

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

Keep the library (`core.py`) free of CLI concerns. Keep the CLI (`cli.py`) free of
histogram logic — it should only parse arguments, call the library, and print results.

## Running manually

```bash
# via the installed entry point
ascii-histogram histogram/foo.dat --stats

# or directly
uv run python main.py histogram/foo.dat --stats
```

## Submitting changes

1. Fork the repo and create a branch from `main`.
2. Make your changes with clear, focused commits.
3. Verify the CLI still works end-to-end (`ascii-histogram histogram/foo.dat --stats`).
4. Open a pull request describing what you changed and why.

## Code style

- Follow PEP 8.
- Keep functions focused — if a method is doing two things, split it.
- Add docstrings to public classes and non-trivial methods.
- No new runtime dependencies without discussion first.
