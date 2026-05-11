import sys

import pandas as pd


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python simple_enrichment.py annotations.csv summary.csv")
    in_csv, out_csv = sys.argv[1], sys.argv[2]
    df = pd.read_csv(in_csv)
    categories = ["kinase", "transport", "ribosomal", "photosystem", "membrane"]
    rows = []
    for c in categories:
        n = df["putative_function"].astype(str).str.contains(c, case=False, na=False).sum()
        rows.append({"category": c, "count": int(n)})
    pd.DataFrame(rows).sort_values("count", ascending=False).to_csv(out_csv, index=False)
    print(f"Saved {out_csv}")


if __name__ == "__main__":
    main()
