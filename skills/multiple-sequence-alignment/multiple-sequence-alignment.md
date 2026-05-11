---
name: multiple-sequence-alignment
display-name: Multiple Sequence Alignment (Marine)
category: alignment
short-description: Build marine homolog alignments with MAFFT/MUSCLE/Clustal Omega and export analysis-ready MSA files.
starting-prompt: Align these marine homologous sequences and produce an MSA for downstream analysis.
---

# Multiple Sequence Alignment (Marine)

Use this skill when homolog sequences are already collected from BLAST.

## Inputs
- FASTA file containing homologs
- Optional redundancy threshold
- Optional trimming preference

## Recommended Workflow
1. Remove near-identical redundancy if needed.
2. Run MAFFT (`--auto`) as default.
3. Optionally trim poorly aligned tails.
4. Export aligned FASTA and summary stats.

## Outputs
- Alignment FASTA
- Optional trimmed FASTA
- Sequence count and alignment length metrics

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
mafft --auto homologs.fa > homologs.aln.fa
```

```bash
# Optional trimming (if trimAl is available)
trimal -in homologs.aln.fa -out homologs.aln.trimmed.fa -automated1
```

```python
from Bio import AlignIO
aln = AlignIO.read("homologs.aln.fa", "fasta")
print("nseq =", len(aln), "alen =", aln.get_alignment_length())
```

### Suggested Plots
- `gap_fraction_per_position.png`
- `pairwise_identity_heatmap.png`

### Troubleshooting
- Excessive gaps: remove highly divergent or partial sequences before alignment.
- MAFFT memory issues: split input and align in batches.
- Downstream tree instability: trim poorly aligned columns first.
