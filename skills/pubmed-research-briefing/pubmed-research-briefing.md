---
name: pubmed-research-briefing
display-name: PubMed Research Briefing
category: literature
short-description: Retrieve recent PubMed papers and generate structured briefings for marine genes, pathways, and diseases.
starting-prompt: Search PubMed for recent papers on this marine genomics topic and summarize key findings.
---

# PubMed Research Briefing

Adapted from ClawBio `pubmed-summariser` and BioClaw `pubmed-search`.

## Inputs
- Query term (gene symbol, pathway, disease, or marine ecology topic)
- Optional filters: year range, journal, publication type

## Workflow
1. Run PubMed search via NCBI Entrez (`esearch`).
2. Fetch article records (`efetch` XML).
3. Parse title, authors, journal, date, abstract snippet, PMID URL.
4. Produce structured markdown summary and machine-readable table.

## Outputs
- Top paper summary in markdown
- `pubmed_hits.tsv` with metadata

## Notes
- Use exact, non-hallucinated citations only.
- Prefer recent papers unless user asks for historical context.

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
python scripts/pubmed_fetch.py "marine microbiome antibiotic resistance" pubmed_hits.tsv 15
```

```python
import pandas as pd
hits = pd.read_csv("pubmed_hits.tsv", sep="\\t")
hits.groupby("year").size().to_csv("publication_year_counts.csv")
```

### Suggested Plots
- `publication_year_trend.png`
- `journal_frequency_barplot.png`

### Troubleshooting
- Too few results: broaden terms, include synonyms and acronym expansions.
- Noisy results: constrain by title field or publication window.
- API/network failures: retry with smaller `retmax` and backoff.
