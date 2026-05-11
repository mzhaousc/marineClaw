# Deploying marineClaw on HPC (Slurm / shared filesystem)

This guide assumes a typical academic cluster: **login node** for editing and submitting jobs, **compute nodes** for heavy BLAST and I/O, a **shared** `$HOME` or project filesystem, and optionally **local scratch** (`$SLURM_TMPDIR` or `/scratch/$USER`).

## 1. What runs where

| Component | Typical placement |
|-----------|-------------------|
| `marine_agent` (Python, LLM calls, Gradio) | Login node or a **GPU/interactive** partition if you use local LLMs |
| BLAST+ against **nr** | **Compute nodes** only (multi-core, long walltime) |
| Large BLAST databases | Shared read-only directory (e.g. `$SCRATCH/blastdb` or module-provided path) |
| Agent `MARINE_AGENT_WORKDIR` | Per-job **scratch** (fast local disk) when possible |

Do not run full **nr** searches on the login node; use `sbatch` / `srun` (or your site’s equivalent).

## 2. Install software

Use your site’s **modules** or **Conda** (often already documented on the cluster).

```bash
# Example: load BLAST (names vary by site)
module load blast+/2.14.1   # or: module spider blast

# Recommended: use the repo env for the agent
cd /path/to/marineClaw
conda env create -f environment.yml   # or environment-minimal.yml for UI-only
conda activate marineclaw
pip install -r requirements.txt       # if not fully covered by conda
```

## 3. Configure environment (`.env`)

Copy the template and edit on the cluster (never commit real keys).

```bash
cp .env.example .env
```

Important variables for HPC + BLAST:

| Variable | Purpose |
|----------|---------|
| `BLASTDB` | Directory containing BLAST volumes (e.g. `nr.*` from `makeblastdb`). BLAST+ resolves `-db nr` against this path. |
| `MARINE_AGENT_WORKDIR` | Where the agent writes executed artifacts; use **scratch** for large runs. |
| `MARINE_AGENT_HPC_MODE` | Set to `1` or `true` so the LLM system prompt includes HPC/BLAST threading hints. |
| `MARINE_AGENT_BLAST_NUM_THREADS` | Optional fixed thread count for prompts (e.g. `16`). If unset, prompts suggest `${SLURM_CPUS_PER_TASK}`. |
| `MARINE_AGENT_TIMEOUT` | Raise for long BLAST jobs started **from** the agent (default 300s may be too low for nr). |

Example fragment:

```env
MARINE_AGENT_HPC_MODE=true
BLASTDB=/scratch/$USER/blastdb
MARINE_AGENT_WORKDIR=/scratch/$USER/marineclaw_work
MARINE_AGENT_BLAST_NUM_THREADS=16
MARINE_AGENT_TIMEOUT=86400
```

Note: expand `$USER` in `.env` only if your shell or dotenv usage supports it; many sites use a **fully expanded** path in `.env`.

## 4. Building a local **nr** database (one-time, large)

NCBI **nr** is huge; storage and download policies are site-specific. Common patterns:

1. Download FASTA (or use `update_blastdb.pl` from NCBI) into a dedicated directory on **scratch** or a **project** volume.
2. Run `makeblastdb` on a **compute node** (interactive or batch job with enough memory).

Example (protein **nr**; adjust paths and memory to your site):

```bash
#!/bin/bash
#SBATCH --job-name=mknr
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=24:00:00

set -euo pipefail
module load blast+    # if needed

DB_DIR=/scratch/$USER/blastdb
mkdir -p "$DB_DIR"
cd "$DB_DIR"

# Example: you already have nr.faa in this directory
makeblastdb -in nr.faa -dbtype prot -out nr -parse_seqids -taxid_map prot.accession2taxid  # taxid_map optional

# Point BLAST+ at this directory
export BLASTDB="$DB_DIR"
```

After this, `blastp -db nr -query query.fa ...` works when `BLASTDB` includes `$DB_DIR`.

For **pre-built** NCBI BLAST databases, follow current NCBI documentation and your cluster’s mirrored data (many sites provide `/path/to/blastdb` — set `BLASTDB` to that path).

## 5. Parallelism: threads vs many jobs

- **Single query, multi-core:** use BLAST+ **`-num_threads`**, aligned with Slurm **`--cpus-per-task`**:

  ```bash
  blastp -db nr -query query.fa -outfmt 6 -num_threads ${SLURM_CPUS_PER_TASK:-4} -out hits.tsv
  ```

- **Many queries (e.g. one FASTA per sample):** use a **job array** or **GNU parallel** so each task uses its own cores and I/O. See `hpc/slurm_blast_array.sh`.

The interactive agent does **not** replace a full workflow engine; for hundreds of samples, generate a Snakemake/Nextflow workflow (see skills `marine-workflow-management` and `marine-nextflow-dsl2-workflow-template`) and submit that as one pipeline job.

## 6. Running the agent on the cluster

**Batch BLAST** is usually submitted with `sbatch`; the **Gradio UI** needs a network-forwarded port or an interactive session.

```bash
# List skills (login node)
python -m marine_agent --list-skills

# One-shot query (short jobs only on login node; long BLAST → wrap in sbatch yourself or raise timeout)
python -m marine_agent "Outline a blastp command against nr with threads from Slurm"

# Web UI on a node with port forwarding (example)
srun --pty bash
conda activate marineclaw
cd /path/to/marineClaw
python -m marine_agent --web --host 0.0.0.0 --port 7860
# From laptop: ssh -L 7860:node:7860 user@cluster
```

CLI flags for bind address/port depend on your `cli.py`; if `--host` is not implemented, use Gradio defaults and SSH tunnel to `127.0.0.1` on the compute node.

## 7. API keys and offline policy

LLM calls require outbound network and API keys unless you use **Ollama** on the cluster. Store keys only in `.env` (ignored by git). For air-gapped systems, run the model on an allowed node or copy generated scripts to batch jobs without live LLM access.

## 8. Files added for HPC

- `hpc/slurm_blast_array.sh` — template **job array** for per-sample BLAST against `nr` with `BLASTDB` and threads.
- `.env.example` — documents `BLASTDB`, `MARINE_AGENT_HPC_MODE`, and thread defaults.

## 9. Site-specific checklist

- [ ] Quota sufficient for nr (or use shared central BLAST DB).
- [ ] `module load` / Conda BLAST version matches DB format.
- [ ] `BLASTDB` exported in **batch** scripts (`#SBATCH` jobs), not only login shell.
- [ ] Scratch cleanup policy (purge old `MARINE_AGENT_WORKDIR` outputs).
- [ ] Walltime and `--mem` for `makeblastdb` and first `blastp` test.
