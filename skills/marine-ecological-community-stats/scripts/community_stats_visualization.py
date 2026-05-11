import argparse

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
from sklearn.metrics import pairwise_distances


def read_abundance(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=None, engine="python")
    if "feature" in df.columns:
        df = df.set_index("feature")
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--abundance", required=True, help="feature x sample table")
    ap.add_argument("--metadata", required=True, help="sample metadata table")
    ap.add_argument("--sample-col", default="sample")
    ap.add_argument("--group-col", default="site")
    ap.add_argument("--output-prefix", default="marine_comm")
    args = ap.parse_args()

    abundance = read_abundance(args.abundance)
    meta = pd.read_csv(args.metadata, sep=None, engine="python")
    samples = [c for c in abundance.columns if c in set(meta[args.sample_col])]
    if not samples:
        raise ValueError("No overlapping samples between abundance table and metadata.")

    x = abundance[samples].T.astype(float)
    x = np.log1p(x)

    # PCA
    pca = PCA(n_components=min(3, x.shape[0], x.shape[1]))
    scores = pca.fit_transform(x.values)
    score_df = pd.DataFrame(scores, columns=[f"PC{i+1}" for i in range(scores.shape[1])])
    score_df.insert(0, args.sample_col, x.index)
    score_df = score_df.merge(meta[[args.sample_col, args.group_col]], on=args.sample_col, how="left")
    score_df.to_csv(f"{args.output_prefix}_pca_scores.tsv", sep="\t", index=False)

    loadings = pd.DataFrame(
        pca.components_.T,
        index=x.columns,
        columns=[f"PC{i+1}" for i in range(pca.components_.shape[0])],
    )
    loadings.index.name = "feature"
    loadings.to_csv(f"{args.output_prefix}_pca_loadings.tsv", sep="\t")

    # Bray-Curtis distance and NMDS
    dist = pairwise_distances(x.values, metric="braycurtis")
    dist_df = pd.DataFrame(dist, index=x.index, columns=x.index)
    dist_df.to_csv(f"{args.output_prefix}_bray_distance.tsv", sep="\t")

    nmds = MDS(
        n_components=2,
        metric=False,
        dissimilarity="precomputed",
        random_state=42,
        n_init=4,
        max_iter=300,
    )
    nmds_coords = nmds.fit_transform(dist)
    nmds_df = pd.DataFrame(nmds_coords, columns=["NMDS1", "NMDS2"])
    nmds_df.insert(0, args.sample_col, x.index)
    nmds_df = nmds_df.merge(meta[[args.sample_col, args.group_col]], on=args.sample_col, how="left")
    nmds_df.to_csv(f"{args.output_prefix}_nmds_coordinates.tsv", sep="\t", index=False)

    report = [
        "# Community Stats Report",
        "",
        f"- Samples used: {x.shape[0]}",
        f"- Features used: {x.shape[1]}",
        f"- PCA variance explained: {', '.join([f'{v:.4f}' for v in pca.explained_variance_ratio_])}",
        f"- NMDS stress: {nmds.stress_:.4f}",
        "- PERMANOVA: run R template script on generated Bray-Curtis distance table.",
    ]
    with open(f"{args.output_prefix}_permanova_report.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(report) + "\n")

    print("Saved PCA/NMDS tables and PERMANOVA-ready distance matrix.")


if __name__ == "__main__":
    main()
