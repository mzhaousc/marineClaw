---
name: marine-workflow-management
display-name: Marine Workflow Management (Snakemake/Nextflow)
category: workflow-management
short-description: Build reproducible marine genomics pipelines with Snakemake or Nextflow scaffolds and run manifests.
starting-prompt: Create a reproducible workflow scaffold for my marine genomics analysis and export run commands.
---

# Marine Workflow Management (Snakemake/Nextflow)

Integrated from `bioSkills` workflow-management concepts and scientific-agent-skills reproducibility practices.

## Goals
- Turn ad-hoc analysis steps into reproducible pipeline skeletons
- Keep command provenance and environment specification
- Facilitate multi-sample scaling and reruns

## Inputs
- Analysis steps (text or command list)
- Sample sheet (`sample_id`, `input_path`, optional condition/site)

## Outputs
- `Snakefile` or `main.nf` scaffold
- `config.yaml` / `samples.tsv`
- `commands.sh` and run instructions

## Example Scripts
```bash
python scripts/generate_snakemake_scaffold.py \
  --samples samples.tsv \
  --steps "qc,blast,annotation,report" \
  --outdir workflow_smk
```

## Suggested Plots / Reports
- `pipeline_dag.png` (if generated)
- `run_summary.tsv`
- `reproducibility_manifest.md`

## Troubleshooting
- Rule dependency issues: ensure explicit input/output paths per step.
- Environment drift: pin package versions in conda env files.
- Large cohort failures: test pipeline on 1-2 samples before full run.

## Version Compatibility
- Snakemake >= 8 (optional)
- Nextflow >= 24 (optional)
- Python >= 3.10
