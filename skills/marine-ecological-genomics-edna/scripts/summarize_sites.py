import argparse

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="CSV with site,taxon,count")
    ap.add_argument("--group-col", default="site")
    ap.add_argument("--output", default="edna_site_summary.tsv")
    args = ap.parse_args()

    df = pd.read_csv(args.input)
    required = {args.group_col, "taxon", "count"}
    miss = required - set(df.columns)
    if miss:
        raise ValueError(f"Missing required columns: {sorted(miss)}")

    summary = (
        df.groupby(args.group_col)
        .agg(
            taxa_detected=("taxon", "nunique"),
            total_count=("count", "sum"),
            mean_count=("count", "mean"),
            median_count=("count", "median"),
        )
        .reset_index()
    )
    summary.to_csv(args.output, sep="\t", index=False)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
