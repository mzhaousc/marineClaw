import argparse
from pathlib import Path


MAIN_NF = """nextflow.enable.dsl=2

include { QC } from './modules/qc'
include { BLAST } from './modules/blast'
include { ANNOTATION } from './modules/annotation'
include { REPORT } from './modules/report'

workflow {
    Channel
        .fromPath(params.samples)
        .splitCsv(header: true, sep: '\\t')
        .map { row -> tuple(row.sample_id, file(row.input_path)) }
        .set { sample_ch }

    qc_ch = QC(sample_ch)
    blast_ch = BLAST(qc_ch)
    anno_ch = ANNOTATION(blast_ch)
    REPORT(anno_ch)
}
"""

PROCESS_TMPL = """process {NAME} {{
    tag "{{sample_id}}"
    input:
    tuple val(sample_id), path(input_file)
    output:
    tuple val(sample_id), path("{out_name}")
    script:
    \"\"\"
    cp $input_file {out_name}
    \"\"\"
}}
"""

CONFIG = """params {
  samples = "samples.tsv"
}

profiles {
  standard {
    process.executor = "local"
  }
  docker {
    docker.enabled = true
  }
}
"""


def write_module(mod_dir: Path, name: str, out_name: str) -> None:
    content = PROCESS_TMPL.format(NAME=name, out_name=out_name)
    (mod_dir / f"{name.lower()}.nf").write_text(content, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", required=True)
    ap.add_argument("--steps", default="qc,blast,annotation,report")
    ap.add_argument("--outdir", default="workflow_nf")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    modules = outdir / "modules"
    modules.mkdir(parents=True, exist_ok=True)

    (outdir / "main.nf").write_text(MAIN_NF, encoding="utf-8")
    (outdir / "nextflow.config").write_text(CONFIG, encoding="utf-8")
    (outdir / "params.yaml").write_text('samples: "samples.tsv"\n', encoding="utf-8")
    (outdir / "commands.sh").write_text(
        "nextflow run main.nf -profile standard -params-file params.yaml\n"
        "nextflow run main.nf -profile docker -params-file params.yaml\n",
        encoding="utf-8",
    )

    src = Path(args.samples)
    (outdir / "samples.tsv").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    write_module(modules, "QC", "qc.done")
    write_module(modules, "BLAST", "blast.tsv")
    write_module(modules, "ANNOTATION", "annotation.tsv")
    write_module(modules, "REPORT", "report.tsv")

    print(f"Nextflow DSL2 template created at: {outdir}")


if __name__ == "__main__":
    main()
