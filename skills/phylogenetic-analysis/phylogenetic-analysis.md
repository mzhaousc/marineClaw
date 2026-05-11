---
name: phylogenetic-analysis
display-name: Marine Phylogenetic Analysis
category: phylogenetics
short-description: Build phylogenetic trees from marine homologs using MSA and FastTree/IQ-TREE.
starting-prompt: Construct a phylogenetic tree for these marine homolog sequences.
---

# Marine Phylogenetic Analysis

This skill converts homolog collections into interpretable evolutionary trees.

## Inputs
- Homolog FASTA (typically from BLAST output)
- Optional outgroup information
- Optional preferred tree engine (FastTree or IQ-TREE)

## Default Pipeline
1. Align homologs with MAFFT.
2. Infer tree with FastTree for quick runs.
3. Use IQ-TREE for model-based, higher-rigor inference when needed.
4. Export Newick and short interpretation notes.

## Outputs
- `*.aln.fasta` alignment
- `*.tree.nwk` Newick tree
- Optional support value summary

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
bash scripts/build_tree.sh homologs.fa marine_phylo
python scripts/summarize_tree.py marine_phylo.tree.nwk
```

```bash
# Higher-rigor alternative (if IQ-TREE installed)
iqtree2 -s marine_phylo.aln.fasta -m MFP -B 1000 -T AUTO
```

### Suggested Plots
- `phylo_tree_annotated.png`
- `bootstrap_support_histogram.png`

### Troubleshooting
- Low bootstrap support: improve alignment quality and increase informative sites.
- Long-branch attraction risk: remove problematic sequences and compare model choices.
- Root ambiguity: test outgroup-rooted and midpoint-rooted trees.
