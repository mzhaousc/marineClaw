---
name: sequencing-qc-fastqc-multiqc
display-name: Sequencing QC (FastQC + MultiQC)
category: sequencing-qc
short-description: Run FastQC/MultiQC on marine sequencing reads and generate interpretation-ready QC summaries.
starting-prompt: Perform QC for these marine FASTQ files and summarize key quality issues.
---

# Sequencing QC (FastQC + MultiQC)

Adapted from BioClaw runtime `bio-tools` quality-control patterns.

## Inputs
- FASTQ/FASTQ.GZ files (single-end or paired-end)

## Workflow
1. Run FastQC for each sample.
2. Aggregate reports with MultiQC.
3. Parse and summarize key quality flags (Q30, adapters, duplication, GC drift).

## Outputs
- `fastqc/` per-sample reports
- `multiqc_report.html`
- QC summary markdown

## Notes
- For marine metagenomics, elevated GC variability may be biologically plausible; annotate rather than auto-reject.

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
bash scripts/run_qc.sh /path/to/reads qc_out
```

```python
import pandas as pd
qc = pd.read_csv("qc_summary.tsv", sep="\\t")
print(qc.head())
```

### Suggested Plots
- `per_base_quality_boxplot.png`
- `gc_content_distribution.png`
- `duplication_rate_barplot.png`

### Troubleshooting
- FastQC fails on compressed inputs: check file integrity and extension consistency.
- MultiQC misses samples: ensure FastQC outputs are in expected folder hierarchy.
- Extreme adapter contamination: trim and rerun QC before downstream analyses.
