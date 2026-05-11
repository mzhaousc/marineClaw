import sys

import pandas as pd


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python filter_hits.py blast.tsv filtered.tsv")
    infile, outfile = sys.argv[1], sys.argv[2]
    df = pd.read_csv(infile, sep="\t", header=None)
    df.columns = ["qseqid", "sseqid", "pident", "length", "evalue", "bitscore", "stitle"]
    filtered = df[(df["pident"] >= 30) & (df["evalue"] <= 1e-5)].copy()
    filtered.to_csv(outfile, sep="\t", index=False)
    print(f"Saved {len(filtered)} rows to {outfile}")


if __name__ == "__main__":
    main()
