---
name: marine-public-dataset-retrieval
display-name: Marine Public Dataset Retrieval
category: data-retrieval
short-description: Discover and prepare retrieval manifests for marine public omics datasets (SRA/GEO/ENA).
starting-prompt: Find public marine omics datasets for this topic and export a downloadable manifest.
---

# Marine Public Dataset Retrieval

This skill identifies marine-relevant public datasets and creates a reproducible retrieval manifest.

## Supported Sources
- NCBI SRA
- GEO (via Entrez search)
- ENA (European Nucleotide Archive)

## Inputs
- Topic query (e.g. `marine metagenome coral reef`, `algal transcriptome stress`)
- Optional organism and assay constraints
- Optional max records

## Workflow
1. Build marine-specific query terms.
2. Query NCBI/ENA endpoints.
3. Normalize metadata fields (accession, title, platform, links).
4. Export manifest and download command templates.

## Example Script
```bash
python scripts/marine_dataset_retrieve.py \
  --query "marine metagenome coral reef" \
  --max-results 50 \
  --output-prefix marine_data
```

## Outputs
- `marine_data_manifest.tsv`
- `marine_data_download_commands.sh`
- `marine_data_summary.md`

## Suggested Plots
- `dataset_year_distribution.png`
- `dataset_source_pie.png`
- `organism_frequency_barplot.png`

## Troubleshooting
- Few hits: broaden query and remove strict assay terms.
- Missing metadata fields: keep raw accession and source URL for fallback retrieval.
- Download command failures: validate accession type (SRR/SRX/SRA/GSE/ERR) before execution.
