---
name: hgt-detection
display-name: Horizontal Gene Transfer Detection
category: evolution
short-description: Screen marine genes for possible HGT signatures using broad-taxonomy homology evidence.
starting-prompt: Perform HGT screening for these marine genes.
---

# Horizontal Gene Transfer Detection

Use this skill when evaluating unusual lineage patterns in marine genomes.

## Inputs
- Query genes/proteins (FASTA)
- Broad database selection (`nr` or equivalent)

## Workflow
1. Run broad BLAST search with high hit depth.
2. Inspect top-hit taxonomy distribution.
3. Flag genes with strong lineage incongruence.

## Outputs
- Candidate HGT gene table
- Supporting taxonomy evidence summary

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
blastp -query genes.fa -db nr -evalue 1e-10 -max_target_seqs 200 -outfmt 6 -out hgt_blast.tsv
```

```python
import pandas as pd
df = pd.read_csv("hgt_blast.tsv", sep="\\t", header=None)
print("Candidate evidence rows:", len(df))
```

### Suggested Plots
- `putative_origin_taxonomy_barplot.png`
- `hgt_candidate_score_distribution.png`

### Troubleshooting
- Too many false positives: require multi-evidence (taxonomy + phylogeny + composition).
- No candidates found: increase `max_target_seqs` and remove restrictive filters.
- Contamination artifacts: validate assemblies and sample provenance before claims.
