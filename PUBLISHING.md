# marineClaw Publishing Checklist

Use this checklist before publishing marineClaw to GitHub or a public website.

## 1) Security and secrets
- Ensure `.env` is not committed.
- Rotate API keys if they were ever exposed in logs/history.
- Keep only `.env.example` in the repository.

## 2) Repository hygiene
- Keep `.gitignore` enabled to avoid committing runtime outputs and large raw data.
- Avoid committing large FASTQ/BAM/FASTA outputs; publish only small examples.
- Ensure generated temporary files are removed (`tmp/`, `logs/`, `outputs/`).

## 3) Reproducibility
- Verify `environment.yml` and `environment-minimal.yml` are up to date.
- Verify `requirements.txt` still matches Python runtime dependencies.
- Confirm each new skill has:
  - One markdown description file
  - At least one script example
  - Basic troubleshooting and expected outputs

## 4) Basic smoke tests
- `python -m marine_agent --list-skills`
- `python -m marine_agent --web`
- One-shot query test: `python -m marine_agent "run a marine metagenomics profiling plan"`

## 5) Website materials
- Publish `site/marineclaw-overview.html` on your website.
- Keep README and website overview in sync when skills are added.

## 6) HPC / cluster
- Document cluster-specific paths in private notes; public repo should use `HPC.md` and `.env.example` only.
- Do not commit real `BLASTDB` paths that expose internal filesystem layout if that is sensitive.

## 7) Suggested public release files
- `README.md`
- `LICENSE` (add one if missing, usually MIT)
- `environment.yml`
- `environment-minimal.yml`
- `requirements.txt`
- `marine_agent/`
- `skills/`
- `site/marineclaw-overview.html`
