---
name: galaxy-bridge-au
display-name: Galaxy Bridge (usegalaxy.org.au and local)
category: workflow-orchestration
short-description: Discover Galaxy tools, rank relevant candidates with multi-signal scoring, and execute workflows via Planemo.
starting-prompt: Discover relevant Galaxy tools for this marine analysis task and suggest or run a workflow.
---

# Galaxy Bridge (usegalaxy.org.au and local)

This skill ports the core idea of ClawBio Galaxy Bridge into marineClaw:  
**tool discovery + intelligent recommendation + executable workflow launch**.

## What This Skill Does

1. Query Galaxy tool catalog through API (AU instance or any Galaxy URL).
2. Score tools with a multi-signal strategy:
   - keyword overlap with task
   - section/category relevance
   - recency / popularity proxies (when available)
3. Suggest runnable tool/workflow candidates.
4. Execute workflows with Planemo against:
   - remote Galaxy (`--galaxy_url`, `--galaxy_user_key`)
   - local containerized Galaxy (`--engine docker_galaxy`)

## Inputs

- Natural language task description
- Optional tool keywords (`kraken2`, `rna-seq`, `variant`, `metagenomics`, etc.)
- Optional workflow file (`workflow.ga`) and job file (`job.yml`)
- Galaxy URL and API key

## Prerequisites

- Galaxy API key from:
  - `User > Preferences > Manage API key` on Galaxy AU (or other instance)
- `planemo` installed locally
- Optional Python package `bioblend` for programmable discovery

## Example Commands

### 1) Tool discovery + scoring
```bash
python scripts/galaxy_tool_discovery.py \
  --galaxy-url https://usegalaxy.org.au \
  --api-key YOUR_API_KEY \
  --query "marine shotgun metagenomics taxonomy and resistome" \
  --topk 30 \
  --output galaxy_tool_candidates.tsv
```

### 2) Run workflow against Galaxy AU
```bash
bash scripts/planemo_run_workflow.sh \
  https://usegalaxy.org.au \
  YOUR_API_KEY \
  workflow.ga \
  job.yml
```

### 3) Run workflow on local containerized Galaxy
```bash
planemo run --engine docker_galaxy --download_outputs workflow.ga job.yml
```

## Outputs

- `galaxy_tool_candidates.tsv` (ranked recommendations)
- `planemo_run.log` (execution log)
- downloaded workflow outputs (`--download_outputs`)
- optional reproducibility note (`commands.sh`)

## Troubleshooting

- `401 Unauthorized`: API key invalid or expired.
- `No compatible tools found`: broaden query terms and remove strict filters.
- `Planemo timeout`: use `--no_wait` for long runs, inspect job state in Galaxy history.
- `Input mapping errors`: verify `job.yml` input IDs match workflow input labels exactly.

## Security Notes

- Treat Galaxy API key like a password.
- Prefer environment variables or local secret files, avoid hardcoding keys in scripts.
