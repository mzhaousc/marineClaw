import sys

import pandas as pd


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python annotate_from_blast.py blast.tsv annotations.csv")
    blast_tsv, out_csv = sys.argv[1], sys.argv[2]
    df = pd.read_csv(blast_tsv, sep="\t")
    if "stitle" not in df.columns:
        # fallback for outfmt6 without header
        cols = [f"c{i}" for i in range(df.shape[1] - 1)] + ["stitle"]
        df.columns = cols
    ann = pd.DataFrame()
    ann["putative_function"] = df["stitle"].astype(str).str.split(" OS=").str[0]
    ann.to_csv(out_csv, index=False)
    print(f"Saved {len(ann)} annotations to {out_csv}")


if __name__ == "__main__":
    main()
