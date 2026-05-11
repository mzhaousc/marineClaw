#!/bin/bash
set -e

# Usage:
#   bash run_qc.sh reads_dir out_dir

READS_DIR="$1"
OUT_DIR="$2"
FASTQC_DIR="${OUT_DIR}/fastqc"

mkdir -p "$FASTQC_DIR"

fastqc "${READS_DIR}"/*.fastq* -o "$FASTQC_DIR"
multiqc "$FASTQC_DIR" -o "$OUT_DIR"

echo "QC finished. See ${OUT_DIR}/multiqc_report.html"
