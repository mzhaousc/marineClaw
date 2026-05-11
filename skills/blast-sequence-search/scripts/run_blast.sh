#!/bin/bash
set -e

# Usage:
#   bash run_blast.sh query.fasta db_prefix [out_prefix]

QUERY_FASTA="$1"
DB_PREFIX="$2"
OUT_PREFIX="${3:-blast_run}"

blastp \
  -query "$QUERY_FASTA" \
  -db "$DB_PREFIX" \
  -evalue 1e-5 \
  -max_target_seqs 200 \
  -outfmt "6 qseqid sseqid pident length evalue bitscore stitle" \
  -out "${OUT_PREFIX}.tsv"

blastp \
  -query "$QUERY_FASTA" \
  -db "$DB_PREFIX" \
  -evalue 1e-5 \
  -max_target_seqs 200 \
  -outfmt 5 \
  -out "${OUT_PREFIX}.xml"

echo "Saved ${OUT_PREFIX}.tsv and ${OUT_PREFIX}.xml"
