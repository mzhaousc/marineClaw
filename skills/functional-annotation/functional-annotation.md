---
name: functional-annotation
display-name: Functional Annotation (Marine)
category: annotation
short-description: Transfer conservative functional labels from BLAST homologs and produce enrichment-ready summaries.
starting-prompt: Annotate these marine gene/protein hits and summarize likely function.
---

# Functional Annotation (Marine)

This skill maps BLAST evidence to practical functional labels for marine targets.

## Inputs
- BLAST result table (`outfmt6` plus description/title column)
- Optional curated-reference preference (`swissprot`)

## Workflow
1. Prioritize curated hits when possible.
2. Parse best-hit descriptions into putative function labels.
3. Summarize counts for broad biological categories.

## Outputs
- Per-gene putative function table
- Category summary for downstream pathway or enrichment analysis

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
python scripts/annotate_from_blast.py blast_hits.tsv annotations.csv
python scripts/simple_enrichment.py annotations.csv functional_summary.csv
```

```python
import pandas as pd
ann = pd.read_csv("annotations.csv")
print(ann["putative_function"].value_counts().head(20))
```

### Suggested Plots
- `functional_category_barplot.png`
- `annotation_evidence_distribution.png`

### Troubleshooting
- Too many generic labels: prioritize SwissProt-like curated hits.
- Contradictory functions: keep top-k hits and attach evidence score/identity.
- Sparse annotation: relax thresholds slightly, then manually inspect top results.
