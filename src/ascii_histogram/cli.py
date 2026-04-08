import rich_click as click

from ascii_histogram.core import DataSet, Histogram

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = False


@click.command()
@click.argument("file", type=click.Path(exists=True, readable=True))
@click.option(
    "--min-buckets", "-n",
    default=21, show_default=True,
    type=click.IntRange(min=1),
    help="Minimum number of buckets; the primary auto-sizing knob.",
)
@click.option(
    "--bucket-size", "-s",
    default=None,
    type=float,
    help="Bucket width. Auto-sized from the data when omitted.",
)
@click.option(
    "--middle-value", "-m",
    default=None,
    type=float,
    help="Value at the centre of the middle bucket. Derived from the median when omitted.",
)
@click.option(
    "--max-bar-width", "-b",
    default=20, show_default=True,
    type=click.IntRange(min=1),
    help="Maximum bar width in characters.",
)
@click.option(
    "--columns", "-c",
    default="1", show_default=True,
    help="Comma-separated 1-based column indices to read from FILE.",
)
@click.option(
    "--label", "-l",
    multiple=True,
    help="Label for a dataset column. Repeat for multiple columns.",
)
@click.option(
    "--units", "-u",
    default="",
    help="Units string appended to statistics values.",
)
@click.option(
    "--stats", "show_stats",
    is_flag=True, default=False,
    help="Print per-dataset statistics after the histogram.",
)
@click.option(
    "--trim-edges/--no-trim-edges",
    default=True, show_default=True,
    help="Shift the bucket window so no empty interior bins sit adjacent to the "
         "±Inf overflow buckets.  Ignored when [bold]--middle-value[/bold] is set.",
)
def main(file, min_buckets, bucket_size, middle_value, max_bar_width, columns, label, units, show_stats, trim_edges):
    """Generate an ASCII histogram from a data file.

    FILE is a whitespace-delimited text file with one observation per row.
    Multiple columns can be plotted side-by-side using [bold]--columns[/bold].

    Bucket size and placement are [bold]auto-sized by default[/bold] using the
    10th–90th percentile range, so extreme outliers never distort the scale —
    they land in the ±Inf edge buckets instead.  Use [bold]--bucket-size[/bold]
    to override the width and [bold]--middle-value[/bold] to pin the centre.
    """
    cols = [int(c.strip()) for c in columns.split(",")]
    raw_sets = Histogram.read_data_file(file, columns=cols)

    # Auto-size from the combined data of all columns; any manually supplied
    # value is passed through and left unchanged.
    combined = [x for raw in raw_sets for x in raw]
    final_bs, final_nb, final_mv = Histogram.auto_size(
        combined,
        min_buckets=min_buckets,
        bucket_size=bucket_size,
        middle_value=middle_value,
        trim_empty_edges=trim_edges,
    )

    click.echo(
        f"[auto] bucket_size={final_bs}, num_buckets={final_nb}, middle_value={final_mv}",
        err=True,
    )

    h = Histogram(
        num_buckets=final_nb,
        bucket_size=final_bs,
        middle_value=final_mv,
        max_bar_height=max_bar_width,
    )

    datasets = []
    for i, raw in enumerate(raw_sets):
        lbl = label[i] if i < len(label) else f"col{cols[i]}"
        ds = DataSet(data_set=raw, label=lbl, units=units)
        h << ds
        datasets.append(ds)

    click.echo(f"Min: {h.global_min()}")
    click.echo(f"Max: {h.global_max()}")
    click.echo(h.gen_histogram())

    if show_stats:
        for ds in datasets:
            u = f" {ds.units}" if ds.units else ""
            click.echo(f"[{ds.label}]")
            click.echo(f"  N:           {len(ds)}")
            click.echo(f"  Mean:        {ds.mean:.4f}{u}")
            click.echo(f"  Sigma:       {ds.sigma:.4f}{u}")
            click.echo(f"  Sigma High:  {ds.sigma_high:.4f}{u}")
            click.echo(f"  Sigma Low:   {ds.sigma_low:.4f}{u}")
            click.echo(f"  Min:         {min(ds):.4f}{u}")
            click.echo(f"  Max:         {max(ds):.4f}{u}")
