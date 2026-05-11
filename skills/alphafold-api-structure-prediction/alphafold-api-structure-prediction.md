---
name: alphafold-api-structure-prediction
display-name: AlphaFold API Structure Prediction
category: structure
short-description: Predict protein structure from FASTA using an AlphaFold-compatible API endpoint.
starting-prompt: Use AlphaFold API to predict structure for this FASTA file and summarize confidence metrics.
---

# AlphaFold API Structure Prediction

This skill predicts protein structures from FASTA input through an AlphaFold-compatible API.

## Inputs
- FASTA file path (single protein sequence preferred)
- Optional model/version name
- Optional output directory

## API Configuration

Set environment variables before running:

```bash
export ALPHAFOLD_API_URL="https://your-alphafold-api.example.com"
export ALPHAFOLD_API_KEY="your_api_key"
```

Expected API behavior (generic contract):
- `POST /predict` -> returns `job_id`
- `GET /jobs/{job_id}` -> returns status (`queued|running|completed|failed`)
- `GET /jobs/{job_id}/result` -> returns result metadata and file URLs

## Example Script

```bash
python scripts/run_alphafold_api.py \
  --fasta input.fa \
  --output-dir af_out
```

## Outputs
- `af_out/result.json` (raw API response)
- predicted structure file (`.pdb` or `.cif`, depending on API)
- confidence metrics table (`plddt`, optional `pae`)

## Suggested Plots
- `plddt_profile.png`
- `pae_heatmap.png`

## Troubleshooting
- 401/403 auth error: verify `ALPHAFOLD_API_KEY`.
- Job stuck queued: API cluster busy; retry later or use smaller sequence.
- Missing structure file: inspect `result.json` for provider-specific output keys.
- Very low confidence: likely disordered region or poor homolog coverage.
