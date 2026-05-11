# marineClaw - Marine Genomics AI Agent

`marineClaw` is a local, skill-based agent for marine genomics and sequence-first analysis.  
It follows a `generate ↔ execute` loop and supports Python/R/Bash execution, with Bash prioritized for BLAST workflows.

## Scope
- Sequence search and BLAST parameter optimization
- MSA and phylogenetic tree construction
- Functional/domain/pathway annotation
- Ortholog and HGT screening
- Marine metagenomics and BGC/comparative genomics support

## Project Layout
- `marine_agent/` - runtime package (agent, config, executor, web UI, CLI)
- `skills/` - marine genomics skill folders (core + reused conversions)
- `requirements.txt` - Python dependencies

## Install

### Option A (recommended): Conda / Mamba
```bash
cd /home/mzhao/marineClaw
conda env create -f environment.yml
conda activate marineclaw
```

If you update dependencies later:
```bash
conda env update -f environment.yml --prune
```

### Option A2: Conda minimal (UI-first, no heavy bio CLI tools)
```bash
cd /home/mzhao/marineClaw
conda env create -f environment-minimal.yml
conda activate marineclaw-minimal
python -m marine_agent --web
```

### Option B: pip only
```bash
cd /home/mzhao/marineClaw
pip install -r requirements.txt
```

## Configure
Create `.env` at `/home/mzhao/marineClaw/.env` (optional):
```env
LLM_SOURCE=OpenAI
OPENAI_API_KEY=your_key
MARINE_AGENT_MODEL=gpt-4o
MARINE_AGENT_TIMEOUT=300
MARINE_AGENT_MAX_ITER=20

# Optional Galaxy Bridge settings
GALAXY_URL=https://usegalaxy.org.au
GALAXY_API_KEY=your_galaxy_api_key
```

You can copy from the template:
```bash
cp .env.example .env
```

## Notes on external bio tools

Some workflows require CLI tools that are best installed via conda/bioconda:
- `blast` (BLAST+)
- `mafft`
- `fasttree`
- `fastqc` and `multiqc`
- `hmmer`

`environment.yml` already includes these defaults.

## Run
### Web UI (recommended)
```bash
python -m marine_agent --web
```
Open [http://127.0.0.1:7860](http://127.0.0.1:7860).

### One-shot query
```bash
python -m marine_agent "BLAST this FASTA against nr and perform phylogenetic analysis"
```

### Interactive terminal
```bash
python -m marine_agent --interactive
```

### List skills
```bash
python -m marine_agent --list-skills
```

## Included Skills (26)
1. `blast-sequence-search`
2. `multiple-sequence-alignment`
3. `phylogenetic-analysis`
4. `functional-annotation`
5. `protein-domain-annotation`
6. `ortholog-identification`
7. `pathway-mapping`
8. `motif-discovery`
9. `structure-template-search`
10. `hgt-detection`
11. `marine-metagenomics`
12. `biosynthetic-gene-clusters`
13. `marine-comparative-genomics`
14. `shotgun-metagenomics-profiler` (adapted from ClawBio `claw-metagenomics`)
15. `pubmed-research-briefing` (adapted from ClawBio/BioClaw PubMed skills)
16. `protein-structure-predictor` (adapted from ClawBio `struct-predictor`)
17. `sequencing-qc-fastqc-multiqc` (adapted from BioClaw QC workflows)
18. `galaxy-bridge-au` (Galaxy tool discovery + recommendation + Planemo execution)
19. `alphafold-api-structure-prediction` (AlphaFold-compatible API prediction from FASTA)
20. `marine-literature-search` (marine-focused PubMed retrieval and evidence briefing)
21. `marine-public-dataset-retrieval` (marine SRA dataset discovery + manifest/commands export)
22. `marine-ecological-genomics-edna` (adapted from bioSkills ecological-genomics for marine eDNA biodiversity workflows)
23. `marine-workflow-management` (adapted from bioSkills workflow-management for reproducible Snakemake/Nextflow scaffolding)
24. `marine-protein-language-model-annotation` (adapted from scientific-agent-skills protein engineering ideas, ESM-style embedding workflows)
25. `marine-ecological-community-stats` (enhanced ecological-genomics stats: PCA/NMDS/PERMANOVA for marine community data)
26. `marine-nextflow-dsl2-workflow-template` (workflow-management expansion with Nextflow DSL2 modular scaffold)

## Galaxy Bridge (AU) Quick Start

Get API key from Galaxy AU:
- Login `https://usegalaxy.org.au`
- `User > Preferences > Manage API key`

Run tool discovery:
```bash
cd /home/mzhao/marineClaw
python skills/galaxy-bridge-au/scripts/galaxy_tool_discovery.py \
  --galaxy-url https://usegalaxy.org.au \
  --api-key "$GALAXY_API_KEY" \
  --query "marine shotgun metagenomics taxonomy and resistome" \
  --topk 30 \
  --output galaxy_tool_candidates.tsv
```

One-line auto route via marine-agent:
```bash
python -m marine_agent "Use Galaxy AU to discover tools for marine metagenomics and recommend a workflow"
```

If query includes `workflow.ga` and `job.yml`, marine-agent will also auto-attempt `planemo run`.

Run workflow with Planemo on Galaxy AU:
```bash
bash skills/galaxy-bridge-au/scripts/planemo_run_workflow.sh \
  https://usegalaxy.org.au "$GALAXY_API_KEY" workflow.ga job.yml
```

Run against fully local Galaxy container:
```bash
planemo run --engine docker_galaxy --download_outputs workflow.ga job.yml
```

## Optional SmartBLAST Integration
Use `marine_agent/smartblast_client.py` to call a running SmartBLAST follow-up API (`http://localhost:8000`).

## HPC deployment (Slurm, BLAST nr, parallelism)

See [HPC.md](HPC.md) for cluster setup, `BLASTDB`, scratch, job arrays, and multi-core BLAST.  
Template batch script: `hpc/slurm_blast_array.sh`.

## Publish-ready assets
- `.gitignore` for code-only publishing
- `.env.example` for safe configuration sharing
- `PUBLISHING.md` with release checklist
- `site/marineclaw-overview.html` for project website
- `LICENSE` (MIT)
