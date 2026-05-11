---
name: marine-protein-language-model-annotation
display-name: Marine Protein Language Model Annotation
category: protein-engineering
short-description: Use protein language model embeddings (ESM-style) for marine protein function clustering and prioritization.
starting-prompt: Compute protein embedding-based similarity for these marine proteins and suggest functional groups.
---

# Marine Protein Language Model Annotation

Integrated from scientific-agent-skills protein engineering directions (ESM-style workflows), adapted for marine protein candidates.

## Inputs
- Protein FASTA file
- Optional reference proteins with known function

## Outputs
- `protein_embeddings.tsv` (or reduced embedding summary)
- `protein_similarity.tsv`
- `function_cluster_summary.tsv`

## Example Scripts
```bash
python scripts/embedding_similarity_stub.py \
  --fasta proteins.fa \
  --output-prefix marine_plm
```

## Suggested Plots
- `embedding_pca_scatter.png`
- `similarity_heatmap.png`

## Troubleshooting
- Runtime too slow: batch sequences and cache intermediate embeddings.
- Poor separation: remove low-complexity or truncated sequences.
- Over-interpretation risk: treat embedding clusters as hypothesis, not final annotation.

## Version Compatibility
- Python >= 3.10
- pandas >= 2.0
- numpy >= 1.24
