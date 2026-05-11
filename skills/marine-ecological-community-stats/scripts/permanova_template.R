# Reference: vegan 2.6+ | Verify API if version differs
suppressPackageStartupMessages({
  library(vegan)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 5) {
  stop("Usage: Rscript permanova_template.R <distance_tsv> <metadata_tsv> <sample_col> <group_col> <output_tsv>")
}

dist_file <- args[1]
meta_file <- args[2]
sample_col <- args[3]
group_col <- args[4]
out_file <- args[5]

dmat <- read.table(dist_file, header = TRUE, sep = "\t", check.names = FALSE, row.names = 1)
meta <- read.table(meta_file, header = TRUE, sep = "\t", check.names = FALSE)

common_samples <- intersect(rownames(dmat), meta[[sample_col]])
if (length(common_samples) < 3) {
  stop("Need at least 3 overlapping samples for PERMANOVA.")
}

dmat <- dmat[common_samples, common_samples, drop = FALSE]
meta_sub <- meta[match(common_samples, meta[[sample_col]]), , drop = FALSE]

if (!group_col %in% colnames(meta_sub)) {
  stop(paste("group_col not found:", group_col))
}

dist_obj <- as.dist(dmat)
formula_obj <- as.formula(paste("dist_obj ~", group_col))
res <- adonis2(formula_obj, data = meta_sub, permutations = 999, by = "margin")

out <- as.data.frame(res)
out$term <- rownames(out)
rownames(out) <- NULL
write.table(out, file = out_file, sep = "\t", quote = FALSE, row.names = FALSE)
cat("PERMANOVA result saved to:", out_file, "\n")
