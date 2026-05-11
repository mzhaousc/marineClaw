---
name: protein-structure-predictor
display-name: Protein Structure Predictor (Boltz-style)
category: structure
short-description: Predict marine protein structures from sequence/YAML and summarize confidence metrics.
starting-prompt: Predict the structure for this marine protein sequence and report confidence.
---

# Protein Structure Predictor (Boltz-style)

Adapted from ClawBio `struct-predictor`, simplified for marineClaw.

## Inputs
- Protein sequence FASTA or YAML job file
- Optional complex definition (multi-chain)

## Workflow
1. Build prediction input (single chain or complex).
2. Execute local structure predictor (Boltz-compatible workflow when installed).
3. Parse confidence outputs (pLDDT/PAE when available).
4. Generate concise interpretation and reusable artifacts.

## Outputs
- Predicted structure file (`.cif`/`.pdb`)
- Confidence summary table
- Optional pLDDT/PAE plots

## Notes
- If predictor binary is unavailable, fall back to template search mode and clearly state limitation.

## Expanded Usage and Troubleshooting

### Example Scripts
```bash
# Example command (tool-dependent)
# boltz predict input.yaml --outdir struct_out
```

```python
import pandas as pd
conf = pd.read_csv("confidence_metrics.tsv", sep="\\t")
print(conf.describe())
```

### Suggested Plots
- `plddt_profile.png`
- `pae_heatmap.png`

### Troubleshooting
- Missing predictor binary: install/runtime-check before job submission.
- Low-confidence segments: annotate as flexible regions rather than over-interpreting.
- Complex inputs fail: validate chain IDs and YAML schema consistency.
