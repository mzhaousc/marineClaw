import argparse
import math

import pandas as pd


def shannon(counts):
    total = sum(counts)
    if total <= 0:
        return 0.0
    ps = [c / total for c in counts if c > 0]
    return -sum(p * math.log(p) for p in ps)


def simpson(counts):
    total = sum(counts)
    if total <= 0:
        return 0.0
    ps = [c / total for c in counts if c > 0]
    return 1.0 - sum(p * p for p in ps)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="taxonomy profile CSV with at least taxon,count and optional site")
    ap.add_argument("--output-prefix", default="edna")
    args = ap.parse_args()

    df = pd.read_csv(args.input)
    if "site" not in df.columns:
        df["site"] = "all"

    out = []
    for site, g in df.groupby("site"):
        counts = g["count"].astype(float).tolist()
        out.append(
            {
                "site": site,
                "richness": int((g["count"] > 0).sum()),
                "shannon": shannon(counts),
                "simpson": simpson(counts),
                "total_count": float(g["count"].sum()),
            }
        )

    out_df = pd.DataFrame(out)
    out_df.to_csv(f"{args.output_prefix}_alpha_diversity.tsv", sep="\t", index=False)
    print(f"Saved {args.output_prefix}_alpha_diversity.tsv")


if __name__ == "__main__":
    main()
