---
name: motif-discovery
display-name: Motif Discovery
category: sequence-patterns
short-description: Discover conserved sequence motifs from marine homolog sets using k-mer or MEME-style workflows.
starting-prompt: Discover motifs from these marine homolog sequences.
---

# Motif Discovery

Use this skill after alignment or homolog retrieval when you need conserved patterns.

## Inputs
- Protein or nucleotide FASTA
- Optional motif length range

## Workflow
1. Remove duplicates/redundancy.
2. Run k-mer enrichment or motif finder.
3. Report consensus motifs and support counts.

## Outputs
- Ranked motif list
- Consensus sequence patterns

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
# Example using MEME (if installed)
meme sequences.fa -oc meme_out -nmotifs 10 -minw 6 -maxw 20
```

```python
from collections import Counter
seqs = [line.strip() for line in open("sequences.fa") if not line.startswith(">")]
k = 6
counts = Counter(s[i:i+k] for s in seqs for i in range(len(s)-k+1))
print(counts.most_common(10))
```

### Suggested Plots
- `motif_logo.png`
- `motif_position_density.png`

### Troubleshooting
- No significant motifs: increase sample size or broaden width range.
- Repetitive low-complexity motifs: mask low-complexity regions first.
- Overfitting to one clade: de-redundify homolog set before motif search.
