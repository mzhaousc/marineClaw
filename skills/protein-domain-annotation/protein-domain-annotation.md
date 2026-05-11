---
name: protein-domain-annotation
display-name: Protein Domain Annotation
category: annotation
short-description: Annotate protein domains using HMMER/Pfam with fallback to trusted BLAST descriptions.
starting-prompt: Perform protein domain annotation for these marine proteins.
---

# Protein Domain Annotation

Use this skill for domain-centric interpretation, especially when full-length proteins are available.

## Inputs
- Protein FASTA
- Optional `Pfam-A.hmm` path

## Workflow
1. Run `hmmscan` against Pfam if model DB is available.
2. Filter domain hits by e-value and coverage.
3. Add fallback labels from curated BLAST descriptions if needed.

## Outputs
- Domain hit table (`domain`, `evalue`, `coverage`, `target`)

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
hmmscan --domtblout domtblout.tsv /path/to/Pfam-A.hmm proteins.fa > hmmscan.log
```

```python
import pandas as pd
df = pd.read_csv("domtblout.tsv", sep=r"\\s+", comment="#", header=None)
print("domain hits:", len(df))
```

### Suggested Plots
- `domain_architecture_per_protein.png`
- `domain_evalue_distribution.png`

### Troubleshooting
- No domain hits: confirm Pfam HMM DB path and protein sequence format.
- Too many weak domains: apply stricter e-value and domain coverage cutoffs.
- Overlapping domains: prioritize trusted domain models and inspect architecture logic.
