---
name: shotgun-metagenomics-profiler
display-name: Shotgun Metagenomics Profiler (Kraken2/Bracken/RGI/HUMAnN3)
category: metagenomics
short-description: Comprehensive marine shotgun metagenomics profiling with taxonomy, resistome, and pathway outputs.
starting-prompt: Run a marine shotgun metagenomics profile for these FASTQ files and summarize taxonomy, ARGs, and pathways.
---

# Shotgun Metagenomics Profiler

Adapted from reusable ideas in ClawBio `claw-metagenomics` skill and aligned to marineClaw execution style.

## Inputs
- Paired-end FASTQ: `R1.fastq.gz`, `R2.fastq.gz` (preferred)
- Or single FASTQ for exploratory mode
- Optional DB paths: Kraken2 DB, HUMAnN3 DB, CARD

## Workflow
1. Taxonomic classification with Kraken2.
2. Species-level abundance refinement with Bracken.
3. ARG screening with RGI/CARD (strict/perfect priorities).
4. Optional pathway profiling with HUMAnN3.
5. Diversity summary (Shannon/Simpson/richness/evenness).

## Outputs
- `taxonomy_profile.tsv`
- `resistome_profile.tsv`
- `pathway_abundance.tsv` (optional)
- Diversity summary table and report

## Notes
- For marine environmental samples, start with conservative confidence threshold and broad reference DB.
- Export intermediate commands for reproducibility in final report.

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
bash scripts/run_metagenomics_profile.sh sample_R1.fastq.gz sample_R2.fastq.gz profile_out /path/to/kraken_db
```

```bash
# Optional downstream tools (if installed)
# bracken -d /path/to/kraken_db -i profile_out/kraken2_report.tsv -o profile_out/bracken_species.tsv -l S -r 150
# rgi main -i contigs.fna -o profile_out/rgi --clean
```

### Suggested Plots
- `taxonomy_composition_barplot.png`
- `resistome_heatmap.png`
- `diversity_indices_panel.png`

### Troubleshooting
- Kraken2 memory errors: use smaller DB or allocate more RAM.
- Low taxonomy resolution: verify read length and host-decontamination workflow.
- Inconsistent resistome signal: ensure CARD/RGI DB versions are compatible.
