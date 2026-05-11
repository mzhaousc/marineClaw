#!/bin/bash
#SBATCH --job-name=mc_blast
#SBATCH --array=1-10%4
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=logs/blast_%A_%a.out
#SBATCH --error=logs/blast_%A_%a.err
#
# marineClaw HPC example: one BLAST job per array task (e.g. per query file).
#
# Before first run:
#   mkdir -p logs queries out
#   export BLASTDB=/path/to/your/blastdb   # or set in .env and source before sbatch
#
# Prepare queries/queries.txt with one filename per line (no path), e.g.:
#   sample1.fa
#   sample2.fa
#
# Submit: sbatch slurm_blast_array.sh
#
set -euo pipefail

module load blast+ 2>/dev/null || true

: "${BLASTDB:?Set BLASTDB to the directory containing nr.* volumes}"

QUERY_LIST="${QUERY_LIST:-queries/queries.txt}"
DB_NAME="${BLAST_DB:-nr}"
THREADS="${SLURM_CPUS_PER_TASK:-4}"

mapfile -t FILES < <(grep -v '^\s*$' "$QUERY_LIST" || true)
IDX=$((SLURM_ARRAY_TASK_ID - 1))
if [[ $IDX -lt 0 ]] || [[ $IDX -ge ${#FILES[@]} ]]; then
  echo "Array task $SLURM_ARRAY_TASK_ID has no query (list has ${#FILES[@]} lines)."
  exit 0
fi

QFILE="${FILES[$IDX]}"
QP="${QUERY_LIST%/*}/$QFILE"
if [[ ! -f "$QP" ]]; then
  QP="$QFILE"
fi
if [[ ! -f "$QP" ]]; then
  echo "Query not found: $QFILE"
  exit 1
fi

STEM=$(basename "$QFILE" .fa)
STEM=$(basename "$STEM" .faa)
STEM=$(basename "$STEM" .fasta)
OUTDIR="${OUT_DIR:-out}"
mkdir -p "$OUTDIR"

blastp -db "$DB_NAME" -query "$QP" -outfmt 6 \
  -num_threads "$THREADS" \
  -evalue 1e-5 \
  -max_target_seqs 500 \
  -out "${OUTDIR}/${STEM}_vs_${DB_NAME}.tsv"

echo "Wrote ${OUTDIR}/${STEM}_vs_${DB_NAME}.tsv"
