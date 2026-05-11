---
name: marine-ecological-community-stats
display-name: Marine Ecological Community Stats (PCA/NMDS/PERMANOVA)
category: ecological-genomics
short-description: Marine community statistics and visualization workflow including PCA, NMDS, and PERMANOVA-ready outputs.
starting-prompt: Run marine community-level PCA/NMDS and PERMANOVA from my abundance table and metadata.
---

# Marine Ecological Community Stats (PCA/NMDS/PERMANOVA)

Adapted from bioSkills ecological-genomics patterns for marine eDNA and metagenomic community comparison.

## Inputs
- Abundance matrix (`feature` x `sample`) or long table (`sample`, `feature`, `abundance`)
- Metadata table with `sample` and at least one grouping variable (for example `site` or `season`)

## Outputs
- `pca_scores.tsv`, `pca_loadings.tsv`
- `nmds_coordinates.tsv`
- `permanova_input_distance.tsv` and `permanova_report.md`

## Example Scripts
```bash
python scripts/community_stats_visualization.py \
  --abundance abundance.tsv \
  --metadata metadata.tsv \
  --sample-col sample \
  --group-col site \
  --output-prefix marine_comm

Rscript scripts/permanova_template.R \
  marine_comm_bray_distance.tsv metadata.tsv sample site marine_comm_permanova.tsv
```

## Suggested Plots
- `pca_scatter.png` (colored by site/season)
- `nmds_scatter.png`
- `top_loading_features_barplot.png`

## Troubleshooting
- Ordination unstable: remove near-zero-variance features and log/CLR transform if needed.
- Group separation disappears: check sequencing depth normalization and compositional effects.
- PERMANOVA significant but dispersion unequal: run beta-dispersion check before biological conclusion.

## Version Compatibility
- Python >= 3.10
- pandas >= 2.0
- numpy >= 1.24
- scikit-learn >= 1.3
