---
name: marine-ecological-genomics-edna
display-name: Marine Ecological Genomics (eDNA and Biodiversity)
category: ecological-genomics
short-description: eDNA-centric marine ecological genomics workflow for biodiversity profiling, alpha/beta diversity, and site comparison.
starting-prompt: Analyze marine eDNA data to profile biodiversity across sampling sites and generate ecological metrics.
---

# Marine Ecological Genomics (eDNA and Biodiversity)

Integrated from `bioSkills` ecological-genomics patterns and adapted to marineClaw.

## Use Cases
- Coastal or reef eDNA biodiversity studies
- Temporal monitoring of marine community shifts
- Site-to-site community composition comparison

## Inputs
- Taxonomy-abundance table (`taxon`, `count`, optional `site`)
- Optional metadata (`site`, `temperature`, `salinity`, `depth`, etc.)

## Outputs
- `alpha_diversity.tsv` (Shannon/Simpson/richness)
- `beta_distance.tsv` (pairwise distances)
- `community_summary.tsv`

## Example Scripts
```bash
python scripts/compute_edna_diversity.py --input taxonomy_profile.csv --output-prefix edna
python scripts/summarize_sites.py --input taxonomy_profile.csv --group-col site --output edna_site_summary.tsv
```

## Suggested Plots
- `alpha_diversity_boxplot.png`
- `site_composition_stacked_barplot.png`
- `beta_distance_heatmap.png`

## Troubleshooting
- Unstable diversity metrics: normalize by sampling depth/read depth first.
- Site imbalance: ensure comparable sequencing depth and extraction protocol.
- Sparse taxa matrix: filter ultra-rare taxa before beta diversity.

## Version Compatibility
- Python >= 3.10
- pandas >= 2.0
- numpy >= 1.24
