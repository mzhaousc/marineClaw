import argparse
import json
from pathlib import Path

import pandas as pd
import requests


def build_query(q: str) -> str:
    marine_terms = "(marine OR ocean OR coastal OR reef OR coral OR algae OR plankton)"
    return f"({q}) AND {marine_terms}"


def search_sra(query: str, retmax: int) -> list[str]:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "sra",
        "term": query,
        "retmode": "json",
        "retmax": retmax,
        "sort": "relevance",
        "tool": "marineclaw",
        "email": "marineclaw@example.org",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("esearchresult", {}).get("idlist", [])


def summarize_ids(ids: list[str]) -> list[dict]:
    if not ids:
        return []
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "sra",
        "id": ",".join(ids),
        "retmode": "json",
        "tool": "marineclaw",
        "email": "marineclaw@example.org",
    }
    r = requests.get(url, params=params, timeout=45)
    r.raise_for_status()
    data = r.json()
    rows = []
    for uid in data.get("result", {}).get("uids", []):
        rec = data["result"].get(uid, {})
        title = str(rec.get("title", ""))
        rows.append(
            {
                "source": "SRA",
                "uid": uid,
                "accession": rec.get("accession", ""),
                "title": title,
                "organism": rec.get("organism", ""),
                "study": rec.get("study", ""),
                "url": f"https://www.ncbi.nlm.nih.gov/sra/{rec.get('accession','')}",
            }
        )
    return rows


def write_download_commands(df: pd.DataFrame, path: str) -> None:
    lines = [
        "#!/bin/bash",
        "set -e",
        "# Auto-generated dataset retrieval commands",
        "# Requires SRA Toolkit (prefetch/fasterq-dump) for SRR/SRA accessions",
        "",
    ]
    for acc in df["accession"].dropna().astype(str).tolist():
        if acc.startswith(("SRR", "ERR", "DRR")):
            lines.append(f"prefetch {acc}")
            lines.append(f"fasterq-dump {acc} -O data/{acc}")
            lines.append("")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Retrieve marine public dataset manifests")
    ap.add_argument("--query", required=True)
    ap.add_argument("--max-results", type=int, default=50)
    ap.add_argument("--output-prefix", default="marine_data")
    args = ap.parse_args()

    query = build_query(args.query)
    ids = search_sra(query, retmax=args.max_results)
    rows = summarize_ids(ids)
    df = pd.DataFrame(rows)

    manifest = f"{args.output_prefix}_manifest.tsv"
    shell = f"{args.output_prefix}_download_commands.sh"
    summary = f"{args.output_prefix}_summary.md"
    raw = f"{args.output_prefix}_raw.json"

    df.to_csv(manifest, sep="\t", index=False)
    write_download_commands(df, shell)

    with open(summary, "w", encoding="utf-8") as f:
        f.write("# Marine Public Dataset Retrieval Summary\n\n")
        f.write(f"Query: `{query}`\n\n")
        f.write(f"Records: {len(df)}\n\n")
        if len(df):
            f.write("Top entries:\n")
            for _, r in df.head(10).iterrows():
                f.write(f"- {r.get('accession','')} | {r.get('title','')[:120]}\n")

    with open(raw, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    print(f"Saved manifest: {manifest}")
    print(f"Saved commands: {shell}")
    print(f"Saved summary: {summary}")


if __name__ == "__main__":
    main()
