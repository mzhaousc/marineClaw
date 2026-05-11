---
name: marine-metagenomics
display-name: Marine Metagenomics Taxonomic Profiling
category: metagenomics
short-description: Classify marine environmental sequences and summarize taxonomic composition and diversity.
starting-prompt: Classify this marine metagenomics dataset and summarize dominant taxa.
---

# Marine Metagenomics Taxonomic Profiling

This skill targets eDNA and environmental sequencing scenarios.

## Inputs
- Reads/contigs FASTA or BLAST result table
- Optional marine taxonomy reference preference (SILVA/MarRef)

## Workflow
1. Classify sequence evidence into taxa.
2. Aggregate abundance by taxonomic label.
3. Compute basic diversity statistics.

## Outputs
- Taxon abundance profile
- Diversity metric summary

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
python scripts/tax_profile_from_blast.py blast_hits.tsv taxonomy_profile.csv
python scripts/diversity_index.py taxonomy_profile.csv
```

```python
import pandas as pd
df = pd.read_csv("taxonomy_profile.csv")
df.head(30).to_csv("taxonomy_top30.csv", index=False)
```

### Suggested Plots
- `taxonomy_stacked_barplot.png`
- `alpha_diversity_panel.png`

### Troubleshooting
- Low classified reads: check database version and input read quality.
- Dominant single taxon artifact: inspect contamination and host-removal step.
- Unstable diversity estimates: standardize depth (rarefaction/subsampling).
