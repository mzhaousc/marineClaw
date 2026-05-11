---
name: blast-sequence-search
display-name: Marine BLAST Sequence Search
category: sequence-search
short-description: Optimize BLAST parameters for marine genomics objectives and export robust homolog hit tables.
starting-prompt: Run a BLAST search for this marine sequence and generate a ranked homolog table.
---

# Marine BLAST Sequence Search

Use this skill for `blastn`, `blastp`, `blastx`, and `tblastn` in marine projects.

## Inputs
- Query FASTA (single or multiple sequences)
- Analysis goal (phylogenetic, functional, ortholog, structure, hgt)
- Database target (`nr`, `nt`, `swissprot`, `pdb`, or local marine DB)

## Decision Rules
- Phylogenetic: `evalue=1e-5`, high `max_hits` (500+), prioritize taxonomic breadth
- Functional transfer: `evalue=1e-5`, identity >40%, prefer curated DB (`swissprot`)
- Structure template: `evalue=1e-10`, prefer `pdb`, coverage >70%
- HGT scan: `evalue=1e-10`, `max_hits>=50`, do not over-filter taxonomy
- Ortholog screening: reciprocal BLAST required

## Outputs
- `outfmt6` TSV for downstream parsing
- XML (`outfmt5`) for traceability
- Filtered high-confidence hit set

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
# Core run
bash scripts/run_blast.sh query.fa /path/to/db blast_demo

# Post-filtering
python scripts/filter_hits.py blast_demo.tsv blast_demo.filtered.tsv
```

```python
import pandas as pd
df = pd.read_csv("blast_demo.filtered.tsv", sep="\t")
df["qcov"] = 100 * df["length"] / df["length"].max()
df.to_csv("blast_hits_with_cov.tsv", sep="\t", index=False)
```

### Suggested Plots
- `identity_vs_bitscore_scatter.png`
- `top_hit_taxonomy_barplot.png`

### Troubleshooting
- No hits: verify query type and switch `blastn`/`blastp`/`blastx`/`tblastn` accordingly.
- Too many weak hits: tighten `evalue`, add identity and coverage filters.
- Unexpected organisms: check database composition and contamination in input FASTA.
