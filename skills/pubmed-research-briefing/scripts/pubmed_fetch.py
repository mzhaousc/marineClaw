import sys
from xml.etree import ElementTree as ET

import requests


def esearch(term: str, retmax: int = 10) -> list[str]:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": f"{term} AND english[la]",
        "retmode": "json",
        "retmax": retmax,
        "sort": "date",
        "tool": "marineclaw",
        "email": "marineclaw@example.org",
    }
    r = requests.get(url, params=params, timeout=20)
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
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    items = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID", default="")
        title = article.findtext(".//ArticleTitle", default="").strip()
        journal = article.findtext(".//Journal/Title", default="").strip()
        year = article.findtext(".//PubDate/Year", default="")
        abst = " ".join([t.text or "" for t in article.findall(".//Abstract/AbstractText")]).strip()
        items.append(
            {
                "pmid": pmid,
                "title": title,
                "journal": journal,
                "year": year,
                "abstract": abst[:500],
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
            }
        )
    return items


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("Usage: python pubmed_fetch.py 'query term' output.tsv [retmax]")
    term = sys.argv[1]
    out_tsv = sys.argv[2]
    retmax = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    pmids = esearch(term, retmax=retmax)
    items = efetch(pmids)
    with open(out_tsv, "w", encoding="utf-8") as f:
        f.write("pmid\ttitle\tjournal\tyear\turl\tabstract\n")
        for x in items:
            row = "\t".join(
                [
                    x["pmid"].replace("\t", " "),
                    x["title"].replace("\t", " "),
                    x["journal"].replace("\t", " "),
                    x["year"].replace("\t", " "),
                    x["url"].replace("\t", " "),
                    x["abstract"].replace("\t", " ").replace("\n", " "),
                ]
            )
            f.write(row + "\n")
    print(f"Saved {len(items)} PubMed records to {out_tsv}")


if __name__ == "__main__":
    main()
