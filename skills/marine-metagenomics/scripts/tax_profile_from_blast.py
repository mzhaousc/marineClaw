import sys

import pandas as pd


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python tax_profile_from_blast.py blast.tsv tax_profile.csv")
    in_tsv, out_csv = sys.argv[1], sys.argv[2]
    df = pd.read_csv(in_tsv, sep="\t")
    if "stitle" not in df.columns:
        cols = [f"c{i}" for i in range(df.shape[1] - 1)] + ["stitle"]
        df.columns = cols
    labels = df["stitle"].astype(str).str.extract(r"\[(.*?)\]")[0].fillna("Unclassified")
    profile = labels.value_counts().reset_index()
    profile.columns = ["taxon", "count"]
    profile.to_csv(out_csv, index=False)
    print(f"Saved {out_csv}")


if __name__ == "__main__":
    main()
