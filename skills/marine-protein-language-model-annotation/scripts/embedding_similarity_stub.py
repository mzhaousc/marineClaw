import argparse
import hashlib

import numpy as np
import pandas as pd


def read_fasta(path):
    seq_id = None
    seq_buf = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if seq_id is not None:
                    yield seq_id, "".join(seq_buf)
                seq_id = line[1:].split()[0]
                seq_buf = []
            else:
                seq_buf.append(line)
    if seq_id is not None:
        yield seq_id, "".join(seq_buf)


def fake_embedding(seq, dim=32):
    # Deterministic stub embedding for local development.
    h = hashlib.sha256(seq.encode("utf-8")).digest()
    seed = int.from_bytes(h[:8], "little")
    rng = np.random.default_rng(seed)
    vec = rng.normal(0, 1, dim)
    return vec / (np.linalg.norm(vec) + 1e-12)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fasta", required=True)
    ap.add_argument("--output-prefix", default="marine_plm")
    args = ap.parse_args()

    entries = list(read_fasta(args.fasta))
    if not entries:
        raise ValueError("No sequences found in FASTA.")

    ids = [x[0] for x in entries]
    embs = np.vstack([fake_embedding(x[1]) for x in entries])
    emb_df = pd.DataFrame(embs, index=ids)
    emb_df.index.name = "protein_id"
    emb_path = f"{args.output_prefix}_protein_embeddings.tsv"
    emb_df.to_csv(emb_path, sep="\t")

    sim = embs @ embs.T
    sim_df = pd.DataFrame(sim, index=ids, columns=ids)
    sim_path = f"{args.output_prefix}_protein_similarity.tsv"
    sim_df.to_csv(sim_path, sep="\t")

    summary = pd.DataFrame(
        {
            "protein_id": ids,
            "cluster_hint": np.argmax(embs[:, :3], axis=1),
        }
    )
    summary_path = f"{args.output_prefix}_function_cluster_summary.tsv"
    summary.to_csv(summary_path, sep="\t", index=False)
    print(f"Saved: {emb_path}, {sim_path}, {summary_path}")


if __name__ == "__main__":
    main()
