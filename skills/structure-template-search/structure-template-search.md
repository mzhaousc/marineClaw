---
name: structure-template-search
display-name: Structure Template Search
category: structure
short-description: Identify structural templates for marine proteins using PDB-focused homology search.
starting-prompt: Find structure templates for this marine protein sequence.
---

# Structure Template Search

This skill ranks plausible structure templates for downstream modeling.

## Inputs
- Protein FASTA
- Optional target DB (`pdb` preferred)

## Workflow
1. Run BLAST against PDB-oriented database.
2. Enforce stricter identity/coverage criteria.
3. Rank top templates with concise rationale.

## Outputs
- Template ranking table (identity, coverage, evalue)
- Suggested top candidates for modeling

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
blastp -query query.fa -db /path/to/pdb_db -evalue 1e-10 -outfmt 6 -out pdb_hits.tsv
```

```python
import pandas as pd
df = pd.read_csv("pdb_hits.tsv", sep="\\t", header=None)
df.head(20).to_csv("top_templates.tsv", sep="\\t", index=False)
```

### Suggested Plots
- `template_identity_coverage_scatter.png`
- `top_template_rank_plot.png`

### Troubleshooting
- No templates: try broader structure DB or lower identity cutoff carefully.
- Fragmented alignments: enforce query coverage threshold and remove partial hits.
- Inconsistent template quality: rank jointly by identity, coverage, and bitscore.
