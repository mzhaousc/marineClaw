---
name: pathway-mapping
display-name: Pathway Mapping
category: annotation
short-description: Map annotated marine genes to pathway terms and estimate pathway completeness.
starting-prompt: Map these annotated marine genes to pathways and report completeness.
---

# Pathway Mapping

This skill uses annotation outputs (KO/EC-like mappings) to infer pathway-level functions.

## Inputs
- Functional annotation table
- Optional KO/EC columns

## Workflow
1. Normalize IDs and pathway labels.
2. Aggregate genes by pathway.
3. Compute simple completeness score per pathway.

## Outputs
- Gene-to-pathway mapping table
- Pathway completeness summary

## Expanded Usage and Troubleshooting

### Example Scripts
```python
import pandas as pd
ann = pd.read_csv("annotation_table.tsv", sep="\\t")
summary = ann.groupby("pathway").size().reset_index(name="gene_count")
summary.to_csv("pathway_summary.tsv", sep="\\t", index=False)
```

### Suggested Plots
- `pathway_gene_count_barplot.png`
- `pathway_completeness_heatmap.png`

### Troubleshooting
- Missing pathway labels: ensure KO/EC columns are correctly parsed.
- Over-fragmented pathways: normalize identifiers and merge synonyms.
- False completeness inflation: require minimum enzyme evidence confidence.
