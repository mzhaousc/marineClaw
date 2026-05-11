---
name: ortholog-identification
display-name: Ortholog Identification (RBH)
category: comparative-genomics
short-description: Identify orthologs with reciprocal BLAST and conservative identity/coverage filters.
starting-prompt: Find orthologous genes for this marine gene set using reciprocal BLAST.
---

# Ortholog Identification (RBH)

Use reciprocal best hits (RBH) for robust ortholog calls across species.

## Inputs
- Query protein/coding FASTA
- Target species database

## Workflow
1. Query -> target BLAST.
2. Target-best-hit -> query DB reverse BLAST.
3. Keep reciprocal best pairs passing identity and coverage thresholds.

## Outputs
- RBH pair table with confidence flags

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
# Forward and reverse BLAST runs (example names)
blastp -query speciesA.fa -db speciesB.db -out A_vs_B.tsv -outfmt 6
blastp -query speciesB.fa -db speciesA.db -out B_vs_A.tsv -outfmt 6
```

```python
import pandas as pd
a = pd.read_csv("A_vs_B.tsv", sep="\\t", header=None)
b = pd.read_csv("B_vs_A.tsv", sep="\\t", header=None)
print("Forward hits:", len(a), "Reverse hits:", len(b))
```

### Suggested Plots
- `ortholog_count_per_species_pair.png`
- `rbh_identity_distribution.png`

### Troubleshooting
- Very few RBH pairs: check gene prediction consistency and protein IDs.
- Inflated ortholog calls: increase identity/coverage requirements.
- Ambiguous many-to-many matches: keep best reciprocal pairs and mark ties.
