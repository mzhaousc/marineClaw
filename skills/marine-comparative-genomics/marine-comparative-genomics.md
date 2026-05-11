---
name: marine-comparative-genomics
display-name: Marine Comparative Genomics
category: comparative-genomics
short-description: Compare marine genomes to derive core/pan patterns and species-specific gene content.
starting-prompt: Run comparative genomics for these marine genomes/species.
---

# Marine Comparative Genomics

Use this skill for multi-species marine genome comparisons.

## Inputs
- Gene/protein sets across species
- Optional ortholog group table

## Workflow
1. Cluster orthologous families across species.
2. Compute core and pan gene sets.
3. Report species-shared and species-specific content.

## Outputs
- Core/pan summary
- Species-specific candidate gene list

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
# Ortholog clustering tool examples (if installed)
# roary -e -n -p 8 *.gff
# get_homologues.pl -d proteomes/
```

```python
import pandas as pd
core = pd.read_csv("core_pan_summary.tsv", sep="\\t")
print(core.head())
```

### Suggested Plots
- `core_pan_curve.png`
- `species_specific_gene_counts.png`

### Troubleshooting
- Very small core genome: verify annotation consistency and clustering thresholds.
- Inflated pan genome: remove low-quality assemblies and fragmented ORFs.
- Cross-species ID mismatch: normalize identifiers before clustering.
