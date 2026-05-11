import argparse
import re
from collections import Counter

import pandas as pd
import requests


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_+-]+", (text or "").lower()))


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def score_tool(query_tokens: set[str], tool: dict) -> dict:
    name = tool.get("name", "")
    desc = tool.get("description", "")
    section = tool.get("panel_section_name", "")
    labels = " ".join(tool.get("labels", []) or [])

    text_tokens = tokenize(f"{name} {desc} {labels}")
    section_tokens = tokenize(section)

    keyword_score = jaccard(query_tokens, text_tokens)
    section_score = jaccard(query_tokens, section_tokens)
    label_score = jaccard(query_tokens, tokenize(labels))

    # light prior: common bio tool names get slight bump if explicitly mentioned
    prior = 0.0
    for t in ["kraken", "bracken", "humann", "blast", "fastqc", "multiqc", "bwa", "samtools"]:
        if t in query_tokens and t in text_tokens:
            prior += 0.05

    score = 0.65 * keyword_score + 0.20 * section_score + 0.15 * label_score + prior
    return {
        "id": tool.get("id", ""),
        "name": name,
        "description": desc,
        "section": section,
        "labels": labels,
        "score": round(score, 6),
        "keyword_score": round(keyword_score, 6),
        "section_score": round(section_score, 6),
        "label_score": round(label_score, 6),
    }


def fetch_tools(galaxy_url: str, api_key: str) -> list[dict]:
    url = f"{galaxy_url.rstrip('/')}/api/tools"
    resp = requests.get(
        url,
        params={"in_panel": "true"},
        headers={"x-api-key": api_key},
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, list) else []


def main() -> None:
    ap = argparse.ArgumentParser(description="Discover and rank Galaxy tools with multi-signal scoring.")
    ap.add_argument("--galaxy-url", required=True)
    ap.add_argument("--api-key", required=True)
    ap.add_argument("--query", required=True, help="Natural language task/query")
    ap.add_argument("--topk", type=int, default=30)
    ap.add_argument("--output", default="galaxy_tool_candidates.tsv")
    args = ap.parse_args()

    tools = fetch_tools(args.galaxy_url, args.api_key)
    q_tokens = tokenize(args.query)

    scored = [score_tool(q_tokens, t) for t in tools if isinstance(t, dict)]
    scored = sorted(scored, key=lambda x: x["score"], reverse=True)
    top = scored[: args.topk]

    df = pd.DataFrame(top)
    df.to_csv(args.output, sep="\t", index=False)
    print(f"Fetched {len(tools)} tools; wrote top {len(df)} to {args.output}")

    # quick section summary for console usability
    cnt = Counter([x.get("section", "unknown") for x in top])
    print("Top sections:", dict(cnt))


if __name__ == "__main__":
    main()
