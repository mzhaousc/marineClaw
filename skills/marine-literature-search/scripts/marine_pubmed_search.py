import argparse
from xml.etree import ElementTree as ET

import pandas as pd
import requests


def build_query(user_query: str) -> str:
    marine_terms = "(marine OR ocean OR coastal OR reef OR coral OR algae OR plankton)"
    return f"({user_query}) AND {marine_terms} AND english[la]"


def esearch(query: str, retmax: int) -> list[str]:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": retmax,
        "sort": "date",
        "tool": "marineclaw",
        "email": "marineclaw@example.org",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("esearchresult", {}).get("idlist", [])


def efetch(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "tool": "marineclaw",
        "email": "marineclaw@example.org",
    }
    r = requests.get(url, params=params, timeout=45)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    rows = []
    for art in root.findall(".//PubmedArticle"):
        pmid = art.findtext(".//PMID", default="").strip()
        title = art.findtext(".//ArticleTitle", default="").strip()
        journal = art.findtext(".//Journal/Title", default="").strip()
        year = art.findtext(".//PubDate/Year", default="").strip()
        abstract = " ".join([(x.text or "") for x in art.findall(".//Abstract/AbstractText")]).strip()
        rows.append(
            {
                "pmid": pmid,
                "title": title,
                "journal": journal,
                "year": year,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
                "abstract": abstract[:500],
            }
        )
    return rows


def write_briefing(df: pd.DataFrame, path: str, query: str) -> None:
    lines = [f"# Marine Literature Briefing\n", f"Query: `{query}`\n", f"Total hits exported: {len(df)}\n", "## Top Papers\n"]
    for i, row in df.head(10).iterrows():
        lines.append(
            f"{i+1}. **{row['title']}**\n"
            f"   - Journal/Year: {row['journal']} ({row['year']})\n"
            f"   - PMID: {row['pmid']}\n"
            f"   - URL: {row['url']}\n"
        )
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser(description="Marine-focused PubMed search and briefing")
    ap.add_argument("--query", required=True)
    ap.add_argument("--max-results", type=int, default=20)
    ap.add_argument("--output-prefix", default="marine_lit")
    args = ap.parse_args()

    q = build_query(args.query)
    pmids = esearch(q, retmax=args.max_results)
    rows = efetch(pmids)
    df = pd.DataFrame(rows)
    tsv = f"{args.output_prefix}_hits.tsv"
    md = f"{args.output_prefix}_briefing.md"
    df.to_csv(tsv, sep="\t", index=False)
    write_briefing(df, md, q)
    print(f"Saved {len(df)} records to {tsv}")
    print(f"Saved briefing to {md}")


if __name__ == "__main__":
    main()
