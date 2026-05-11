---
name: biosynthetic-gene-clusters
display-name: Marine Biosynthetic Gene Clusters
category: natural-products
short-description: Detect and classify biosynthetic gene clusters in marine assemblies.
starting-prompt: Identify biosynthetic gene clusters in this marine genome assembly.
---

# Marine Biosynthetic Gene Clusters

This skill is designed for secondary metabolite potential mining.

## Inputs
- Genome assembly FASTA
- Optional antiSMASH result directory

## Workflow
1. Detect BGC regions (antiSMASH-style workflow).
2. Annotate cluster class (PKS, NRPS, terpene, etc.).
3. Summarize candidate novelty signals.

## Outputs
- BGC coordinates and type table
- Cluster summary report

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
# antiSMASH example
antismash assembly.fa --output-dir antismash_out
```

```python
import pandas as pd
# Example parsing stub; adapt to antiSMASH output format
df = pd.read_csv("bgc_calls.tsv", sep="\\t")
print(df["bgc_type"].value_counts())
```

### Suggested Plots
- `bgc_type_distribution.png`
- `cluster_length_distribution.png`

### Troubleshooting
- No clusters found: verify assembly continuity and antiSMASH installation.
- Over-split clusters: check contig fragmentation and region boundaries.
- Too many low-confidence calls: cross-check against MIBiG-like references.
