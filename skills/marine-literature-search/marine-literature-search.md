---
name: marine-literature-search
display-name: Marine Literature Search and Briefing
category: literature
short-description: Search marine-focused literature in PubMed and generate structured evidence briefings.
starting-prompt: Search recent literature about this marine genomics topic and summarize key papers.
---

# Marine Literature Search and Briefing

This skill focuses on marine biology, marine microbiome, marine genomics, coral/algae research, and ocean-related omics topics.

## Inputs
- Topic query (e.g. `coral bleaching transcriptomics`, `marine resistome metagenomics`)
- Optional year range and max results

## Workflow
1. Expand query with marine-aware synonyms.
2. Search PubMed (`esearch`).
3. Fetch detailed metadata (`efetch` XML).
4. Export table and produce a concise evidence briefing.

## Example Script
```bash
python scripts/marine_pubmed_search.py \
  --query "coral bleaching transcriptomics" \
  --max-results 20 \
  --output-prefix marine_lit
```

## Outputs
- `marine_lit_hits.tsv` (PMID/title/journal/year/url/abstract)
- `marine_lit_briefing.md` (top-paper summary)

## Suggested Plots
- `publication_year_trend.png`
- `journal_distribution.png`
- `keyword_frequency_barplot.png`

## Troubleshooting
- Too few results: add broader marine terms (ocean, coastal, reef, algae, plankton).
- Noisy results: constrain with title keywords and recent-year filter.
- API/network throttling: reduce `--max-results` and add retry intervals.
