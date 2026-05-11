---
name: marine-nextflow-dsl2-workflow-template
display-name: Marine Nextflow DSL2 Workflow Template
category: workflow-management
short-description: Generate a marine genomics Nextflow DSL2 template with modular processes and sample-sheet driven execution.
starting-prompt: Build a Nextflow DSL2 workflow scaffold for my marine genomics pipeline with sample sheet support.
---

# Marine Nextflow DSL2 Workflow Template

Adapted from bioSkills workflow-management patterns, specialized for marineClaw reproducible workflows.

## Inputs
- `samples.tsv` containing sample identifiers and input paths
- Step list (for example: `qc,blast,annotation,report`)

## Outputs
- `main.nf` (DSL2 pipeline entry)
- `nextflow.config`
- `modules/` process stubs
- `params.yaml` and run commands

## Example Scripts
```bash
python scripts/generate_nextflow_dsl2_template.py \
  --samples samples.tsv \
  --steps qc,blast,annotation,report \
  --outdir workflow_nf
```

## Typical Run Commands
```bash
cd workflow_nf
nextflow run main.nf -profile standard -params-file params.yaml
nextflow run main.nf -profile docker -params-file params.yaml
```

## Troubleshooting
- Channel mismatch: ensure each module emits expected tuple schema.
- Resume behavior unexpected: inspect `.nextflow.log` and use `-resume` only after fixing process definitions.
- Container failures: verify profile-specific container and executor settings in `nextflow.config`.

## Version Compatibility
- Nextflow >= 24
- DSL2 enabled
- Java >= 11
- Python >= 3.10 (for scaffold generator only)
