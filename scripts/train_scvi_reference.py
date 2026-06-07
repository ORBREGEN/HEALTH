"""
Train a batch-aware scVI reference on HEALTHY HLCA cells, and save the healthy
latent distribution used to score deviation.

WHY (read this before running)
------------------------------
The current model scores deviation as absolute distance in RAW gene space. That
fails across labs (independent validation AUC 0.29) because each lab's technical
fingerprint shifts every gene for the whole cohort, sick or healthy alike, and
that shift is larger than the disease signal. See founders-understanding.md Part F.

scVI moves scoring into a LEARNED latent space that is told which batch each cell
came from, so it can factor the technical signature OUT. Crucially we condition on
the BATCH label only — NEVER the disease label — so the disease-blind principle is
preserved exactly: the model is still built from healthy cells only.

WHAT THIS SCRIPT PRODUCES
-------------------------
  models/scvi_reference/                      <- the trained scVI model (reload-able)
  models/scvi_reference/healthy_latent.npz    <- per-donor healthy latent pseudobulk:
                                                 mu (mean), cov (covariance), donor matrix
The validator (validate_scvi_external.py) loads both, maps an external cohort in via
scArches surgery, and scores Mahalanobis deviation from this healthy distribution.

FIRST-PASS NOTES
----------------
- This is the first swing. Goal: move the number and SEE what happens, not win.
- Watch for OVER-correction: if surgery later pulls disease onto healthy too, AUC
  stays ~0.5 — that means the latent space erased the biology. That is a real,
  expected possible outcome and is itself informative.

RUN (Colab, GPU runtime):
    !pip install scvi-tools
    !cd /content/HEALTH && \
        HLCA_PATH=/content/hlca_core.h5ad \
        SCVI_BATCH_KEY=dataset \
        python scripts/train_scvi_reference.py
(Use hlca_core for a faster first pass; hlca_full for the full reference.)
"""

from __future__ import annotations

import os
import sys

import numpy as np
import scanpy as sc
from scipy.sparse import issparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# ── Config ──────────────────────────────────────────────────────────────────────
HLCA_PATH      = os.environ.get("HLCA_PATH", "/content/hlca_core.h5ad")
OUT_DIR        = os.path.join(ROOT, "models", "scvi_reference")
DISEASE_COL    = "disease"
HEALTHY_VALUE  = "normal"
DONOR_COL      = "donor_id"
# Batch covariate = the technical/lab axis scVI should factor out. Try these in order.
BATCH_KEY      = os.environ.get("SCVI_BATCH_KEY", "")        # "" => auto-pick below
BATCH_CANDIDATES = ["dataset", "study", "sample", "batch", "assay", DONOR_COL]
N_HVG          = int(os.environ.get("SCVI_N_HVG", "2000"))   # genes scVI trains on
N_LATENT       = int(os.environ.get("SCVI_N_LATENT", "20"))  # latent dimensions
MAX_EPOCHS     = int(os.environ.get("SCVI_EPOCHS", "0"))     # 0 => scVI auto heuristic
MAX_CELLS      = int(os.environ.get("SCVI_MAX_CELLS", "300000"))  # subsample cap (first pass)
MIN_CELLS_DONOR = 50
SEED           = 0


def _counts_adata(sub):
    """Return an AnnData whose X is RAW COUNTS, keyed by Ensembl var_names.

    HLCA (CellxGene) convention: adata.X is log1p(CP10K), adata.raw.X is raw counts.
    """
    import anndata as ad
    if sub.raw is not None:
        Xc = sub.raw.X
        var = sub.raw.var.copy()
    elif "counts" in sub.layers:
        Xc = sub.layers["counts"]
        var = sub.var.copy()
    else:
        Xc = sub.X
        var = sub.var.copy()
    a = ad.AnnData(X=Xc.copy(), obs=sub.obs.copy(), var=var)
    # sanity: counts should be non-negative integers
    probe = a.X[:50]
    probe = probe.toarray() if issparse(probe) else np.asarray(probe)
    nz = probe[probe > 0]
    looks_counts = nz.size == 0 or (float(nz.max()) > 20 and np.allclose(nz, np.rint(nz)))
    print(f"  counts source: {'raw' if sub.raw is not None else ('layer' if 'counts' in sub.layers else 'X')} "
          f"| max={float(probe.max()):.1f} | looks like counts: {looks_counts}")
    if not looks_counts:
        print("  WARNING: source does not look like raw counts — scVI assumes counts.")
    return a


def main() -> int:
    import scvi
    scvi.settings.seed = SEED

    print(f"Loading {HLCA_PATH} (backed='r') ...")
    adata = sc.read_h5ad(HLCA_PATH, backed="r")
    print(f"  {adata.n_obs:,} cells x {adata.n_vars:,} genes")
    print(f"  obs columns: {list(adata.obs.columns)}\n")

    # ── Pick the batch covariate ────────────────────────────────────────────────
    batch_key = BATCH_KEY or next((c for c in BATCH_CANDIDATES if c in adata.obs.columns), None)
    if batch_key is None or batch_key not in adata.obs.columns:
        raise SystemExit(f"No batch column found. Set SCVI_BATCH_KEY to one of: {list(adata.obs.columns)}")
    print(f"Batch covariate (factored out): '{batch_key}' "
          f"({adata.obs[batch_key].astype(str).nunique()} categories)")

    # ── Healthy subset + subsample ──────────────────────────────────────────────
    healthy_mask = (adata.obs[DISEASE_COL].astype(str) == HEALTHY_VALUE).to_numpy()
    idx = np.where(healthy_mask)[0]
    print(f"Healthy cells (disease == '{HEALTHY_VALUE}'): {idx.size:,}")
    rng = np.random.default_rng(SEED)
    if idx.size > MAX_CELLS:
        idx = np.sort(rng.choice(idx, MAX_CELLS, replace=False))
        print(f"  subsampled to {idx.size:,} for this pass (SCVI_MAX_CELLS={MAX_CELLS})")

    print("Loading subset into memory ...")
    sub = adata[idx].to_memory()
    train = _counts_adata(sub)

    # ── Highly variable genes (scVI trains on these; query must match) ───────────
    print(f"Selecting {N_HVG} highly variable genes (seurat_v3, on counts) ...")
    sc.pp.highly_variable_genes(train, n_top_genes=N_HVG, flavor="seurat_v3",
                                batch_key=batch_key, subset=True)
    print(f"  training matrix: {train.n_obs:,} cells x {train.n_vars:,} genes")

    # ── Train scVI (batch-conditioned, NO disease label) ────────────────────────
    scvi.model.SCVI.setup_anndata(train, batch_key=batch_key)
    model = scvi.model.SCVI(train, n_latent=N_LATENT)
    print(f"\nTraining scVI (n_latent={N_LATENT}) ... this is the actual ML step.")
    model.train(max_epochs=(MAX_EPOCHS or None))

    os.makedirs(OUT_DIR, exist_ok=True)
    model.save(OUT_DIR, overwrite=True, save_anndata=False)
    # gene order scVI expects from any query — save explicitly for the validator
    np.save(os.path.join(OUT_DIR, "ref_var_names.npy"),
            np.asarray(train.var_names, dtype=object), allow_pickle=True)
    print(f"\nModel saved -> {OUT_DIR}")

    # ── Healthy latent distribution: per-donor latent pseudobulk ────────────────
    print("Computing per-donor healthy latent reference ...")
    Z = model.get_latent_representation()            # (cells x n_latent)
    donors = train.obs[DONOR_COL].astype(str).to_numpy()
    donor_vecs, kept = [], []
    for d in np.unique(donors):
        sel = np.where(donors == d)[0]
        if sel.size < MIN_CELLS_DONOR:
            continue
        donor_vecs.append(Z[sel].mean(axis=0))       # latent pseudobulk for donor d
        kept.append(d)
    M = np.vstack(donor_vecs)                          # (n_donors x n_latent)
    mu = M.mean(axis=0)
    cov = np.cov(M, rowvar=False) + 1e-4 * np.eye(M.shape[1])  # ridge for stability

    # reference self-distances: a yardstick for "normal" Mahalanobis
    cov_inv = np.linalg.pinv(cov)
    self_d = np.array([float(np.sqrt((v - mu) @ cov_inv @ (v - mu))) for v in M])

    np.savez(os.path.join(OUT_DIR, "healthy_latent.npz"),
             mu=mu, cov=cov, donor_matrix=M, donors=np.asarray(kept, dtype=object),
             batch_key=batch_key, n_latent=N_LATENT)
    print(f"  healthy donors in reference: {M.shape[0]} | latent dim: {M.shape[1]}")
    print(f"  reference Mahalanobis: median={np.median(self_d):.2f} "
          f"p90={np.percentile(self_d,90):.2f} (yardstick for 'normal')")
    print(f"  saved -> {os.path.join(OUT_DIR, 'healthy_latent.npz')}")
    print("\nNext: scripts/validate_scvi_external.py to map an external cohort in and score AUC.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
