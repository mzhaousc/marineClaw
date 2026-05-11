#!/bin/bash
set -e

# Example wrapper for taxonomy + resistome + optional pathways.
# Usage:
#   bash run_metagenomics_profile.sh R1.fastq.gz R2.fastq.gz output_dir kraken_db

R1="$1"
R2="$2"
OUT_DIR="$3"
KRAKEN_DB="$4"

mkdir -p "$OUT_DIR"

kraken2 --db "$KRAKEN_DB" \
  --paired "$R1" "$R2" \
  --report "${OUT_DIR}/kraken2_report.tsv" \
  --output "${OUT_DIR}/kraken2.out"

echo "Kraken2 done: ${OUT_DIR}/kraken2_report.tsv"
echo "You can continue with Bracken/RGI/HUMAnN3 depending on local install."
