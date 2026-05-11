#!/bin/bash
set -e

# Usage:
#   bash build_tree.sh homologs.fasta [out_prefix]

INPUT_FASTA="$1"
OUT_PREFIX="${2:-marine_phylo}"

mafft --auto "$INPUT_FASTA" > "${OUT_PREFIX}.aln.fasta"
FastTree "${OUT_PREFIX}.aln.fasta" > "${OUT_PREFIX}.tree.nwk"

echo "Saved ${OUT_PREFIX}.aln.fasta and ${OUT_PREFIX}.tree.nwk"
