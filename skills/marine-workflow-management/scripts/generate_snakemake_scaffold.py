import argparse
from pathlib import Path

SNAKEFILE_TMPL = """configfile: "config.yaml"

rule all:
    input:
        "results/report.tsv"

rule report:
    input:
        "results/annotation.tsv"
    output:
        "results/report.tsv"
    shell:
        "cp {input} {output}"
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", required=True, help="samples tsv")
    ap.add_argument("--steps", default="qc,blast,annotation,report", help="comma-separated logical steps")
    ap.add_argument("--outdir", default="workflow_smk")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "results").mkdir(exist_ok=True)

    (outdir / "Snakefile").write_text(SNAKEFILE_TMPL, encoding="utf-8")
    (outdir / "config.yaml").write_text(
        f"samples: {Path(args.samples).name}\nsteps: {args.steps.split(',')}\n",
        encoding="utf-8",
    )

    src_samples = Path(args.samples)
    dst_samples = outdir / src_samples.name
    dst_samples.write_text(src_samples.read_text(encoding="utf-8"), encoding="utf-8")

    commands = [
        "snakemake -s Snakefile -j 4 --use-conda",
        "snakemake -s Snakefile --dag | dot -Tpng > pipeline_dag.png",
    ]
    (outdir / "commands.sh").write_text("\n".join(commands) + "\n", encoding="utf-8")
    (outdir / "reproducibility_manifest.md").write_text(
        "# Reproducibility Manifest\n\n- Engine: Snakemake\n- Steps: "
        + args.steps
        + "\n- Input sample sheet: "
        + src_samples.name
        + "\n",
        encoding="utf-8",
    )
    print(f"Scaffold created at: {outdir}")


if __name__ == "__main__":
    main()
