"""
Train a batch-aware, cell-type-aware scANVI reference on HEALTHY HLCA cells, and
save BOTH a whole-donor and a PER-CELL-TYPE healthy latent distribution.

WHY scANVI (read founders-understanding.md too)
-----------------------------------------------
First pass with plain scVI gave latent-space AUC 0.49 — no separation. Diagnosis:
(1) vanilla scVI over-integrated and washed the disease signal, and (2) scoring the
whole-donor average diluted the interferon program, which concentrates in specific
compartments (myeloid, epithelial).

scANVI fixes both:
  - it conditions on CELL-TYPE labels (healthy HLCA labels — NEVER disease), so the
    latent space preserves compartment structure instead of collapsing it. This is
    the HLCA's own integration method. Disease-blind is fully preserved: cell type is
    not disease information.
  - it transfers cell-type labels onto any query cohort, which lets us score deviation
    PER COMPARTMENT rather than as one blunt per-donor number.

WHAT THIS SAVES
---------------
  models/scanvi_reference/                 <- the trained scANVI model
  models/scanvi_reference/reference.pkl    <- whole-donor + per-cell-type healthy
                                              latent stats (mean, covariance, and the
                                              healthy Mahalanobis distribution used to
                                              standardize each compartment)

RUN (Colab GPU, in-kernel — NOT !python, so output streams):
    import os, sys, importlib
    os.environ["HLCA_PATH"]      = "/content/hlca_core.h5ad"
    os.environ["SCVI_MAX_CELLS"] = "100000"
    sys.path.insert(0, "/content/SENEBICLABS/scripts")
    import train_scanvi_reference as T; importlib.reload(T); T.main()
"""

from __future__ import annotations

import os
import sys
import pickle

import numpy as np
import scanpy as sc
from scipy.sparse import issparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# ── Config ──────────────────────────────────────────────────────────────────────
HLCA_PATH       = os.environ.get("HLCA_PATH", "/content/hlca_core.h5ad")
OUT_DIR         = os.path.join(ROOT, "models", "scanvi_reference")
DISEASE_COL     = "disease"
HEALTHY_VALUE   = "normal"
DONOR_COL       = "donor_id"
BATCH_KEY       = os.environ.get("SCVI_BATCH_KEY", "")
BATCH_CANDIDATES = ["dataset", "study", "sample", "batch", "assay", DONOR_COL]
# Cell-type label scANVI conditions on. ann_level_2 = compartment resolution
# (airway/alveolar epithelium, myeloid, lymphoid, endothelium, fibroblast, ...).
LABEL_KEY       = os.environ.get("SCANVI_LABEL_KEY", "ann_level_2")
N_HVG           = int(os.environ.get("SCVI_N_HVG", "2000"))
N_LATENT        = int(os.environ.get("SCVI_N_LATENT", "20"))
SCVI_EPOCHS     = int(os.environ.get("SCVI_EPOCHS", "80"))
SCANVI_EPOCHS   = int(os.environ.get("SCANVI_EPOCHS", "20"))
MAX_CELLS       = int(os.environ.get("SCVI_MAX_CELLS", "100000"))
MIN_CELLS_DONOR = 50          # whole-donor pseudobulk
MIN_CELLS_CT_DONOR = 20       # per (cell-type, donor) pseudobulk
MIN_DONORS_PER_CT  = 20       # cell types with fewer reference donors are skipped
RIDGE           = 1e-2        # covariance regularization (latent dim ~ donors)
SEED            = 0


def _counts_adata(sub):
    """AnnData with X = raw counts (HLCA: adata.raw.X), carrying obs."""
    import anndata as ad
    if sub.raw is not None:
        Xc, var = sub.raw.X, sub.raw.var.copy()
    elif "counts" in sub.layers:
        Xc, var = sub.layers["counts"], sub.var.copy()
    else:
        Xc, var = sub.X, sub.var.copy()
    a = ad.AnnData(X=Xc.copy(), obs=sub.obs.copy(), var=var)
    probe = a.X[:50]
    probe = probe.toarray() if issparse(probe) else np.asarray(probe)
    nz = probe[probe > 0]
    looks = nz.size == 0 or (float(nz.max()) > 20 and np.allclose(nz, np.rint(nz)))
    print(f"  counts: max={float(probe.max()):.1f} | looks like counts: {looks}")
    return a


def _mahalanobis_set(M, mu, cov_inv):
    diff = M - mu
    return np.sqrt(np.einsum("ij,jk,ik->i", diff, cov_inv, diff))


def main() -> int:
    import scvi
    scvi.settings.seed = SEED

    print(f"Loading {HLCA_PATH} (backed='r') ...")
    adata = sc.read_h5ad(HLCA_PATH, backed="r")
    print(f"  {adata.n_obs:,} cells x {adata.n_vars:,} genes")

    batch_key = BATCH_KEY or next((c for c in BATCH_CANDIDATES if c in adata.obs.columns), None)
    if batch_key is None:
        raise SystemExit(f"No batch column. obs has: {list(adata.obs.columns)}")
    if LABEL_KEY not in adata.obs.columns:
        raise SystemExit(f"Label column '{LABEL_KEY}' not found. obs has: {list(adata.obs.columns)}")
    print(f"Batch covariate: '{batch_key}' ({adata.obs[batch_key].astype(str).nunique()} cats)")
    print(f"Cell-type label: '{LABEL_KEY}' ({adata.obs[LABEL_KEY].astype(str).nunique()} cats)")

    healthy_mask = (adata.obs[DISEASE_COL].astype(str) == HEALTHY_VALUE).to_numpy()
    idx = np.where(healthy_mask)[0]
    print(f"Healthy cells: {idx.size:,}")
    rng = np.random.default_rng(SEED)
    if idx.size > MAX_CELLS:
        idx = np.sort(rng.choice(idx, MAX_CELLS, replace=False))
        print(f"  subsampled to {idx.size:,}")

    print("Loading subset into memory ... (a few minutes, not frozen)")
    sub = adata[idx].to_memory()
    train = _counts_adata(sub)
    train.obs[LABEL_KEY] = train.obs[LABEL_KEY].astype(str)

    print(f"Selecting {N_HVG} HVGs (seurat_v3, on counts) ...")
    sc.pp.highly_variable_genes(train, n_top_genes=N_HVG, flavor="seurat_v3",
                                batch_key=batch_key, subset=True)

    # ── scVI then scANVI (cell-type-aware) ──────────────────────────────────────
    scvi.model.SCVI.setup_anndata(train, batch_key=batch_key)
    scvi_model = scvi.model.SCVI(train, n_latent=N_LATENT)
    print(f"\nTraining scVI ({SCVI_EPOCHS} epochs) ...")
    scvi_model.train(max_epochs=SCVI_EPOCHS)

    print(f"\nTraining scANVI ({SCANVI_EPOCHS} epochs, label='{LABEL_KEY}') ... biology-preserving step.")
    scanvi_model = scvi.model.SCANVI.from_scvi_model(
        scvi_model, unlabeled_category="Unknown", labels_key=LABEL_KEY)
    scanvi_model.train(max_epochs=SCANVI_EPOCHS)

    os.makedirs(OUT_DIR, exist_ok=True)
    scanvi_model.save(OUT_DIR, overwrite=True, save_anndata=False)
    print(f"Model saved -> {OUT_DIR}")

    # ── Build healthy latent reference (whole-donor + per-cell-type) ────────────
    print("Computing healthy latent reference ...")
    Z = scanvi_model.get_latent_representation()
    donors = train.obs[DONOR_COL].astype(str).to_numpy()
    labels = train.obs[LABEL_KEY].astype(str).to_numpy()

    # whole-donor
    dvecs, _ = [], None
    for d in np.unique(donors):
        sel = np.where(donors == d)[0]
        if sel.size >= MIN_CELLS_DONOR:
            dvecs.append(Z[sel].mean(axis=0))
    M = np.vstack(dvecs)
    whole_mu = M.mean(axis=0)
    whole_cov_inv = np.linalg.pinv(np.cov(M, rowvar=False) + RIDGE * np.eye(N_LATENT))
    whole_yard = float(np.median(_mahalanobis_set(M, whole_mu, whole_cov_inv)))
    print(f"  whole-donor: {M.shape[0]} donors | Mahalanobis yardstick={whole_yard:.2f}")

    # per-cell-type
    ct_stats = {}
    for ct in np.unique(labels):
        ct_mask = labels == ct
        vecs = []
        for d in np.unique(donors[ct_mask]):
            sel = np.where(ct_mask & (donors == d))[0]
            if sel.size >= MIN_CELLS_CT_DONOR:
                vecs.append(Z[sel].mean(axis=0))
        if len(vecs) < MIN_DONORS_PER_CT:
            continue
        Mc = np.vstack(vecs)
        mu = Mc.mean(axis=0)
        cov_inv = np.linalg.pinv(np.cov(Mc, rowvar=False) + RIDGE * np.eye(N_LATENT))
        dd = _mahalanobis_set(Mc, mu, cov_inv)
        ct_stats[ct] = {"mu": mu, "cov_inv": cov_inv,
                        "ref_med": float(np.median(dd)),
                        "ref_std": float(dd.std() + 1e-6),
                        "n_donors": int(Mc.shape[0])}
    print(f"  per-cell-type references: {len(ct_stats)} compartments "
          f"({', '.join(sorted(ct_stats)[:8])}{' ...' if len(ct_stats) > 8 else ''})")

    ref = {"whole_mu": whole_mu, "whole_cov_inv": whole_cov_inv, "whole_yard": whole_yard,
           "ct_stats": ct_stats, "batch_key": batch_key, "label_key": LABEL_KEY,
           "n_latent": N_LATENT, "var_names": np.asarray(train.var_names, dtype=object)}
    with open(os.path.join(OUT_DIR, "reference.pkl"), "wb") as f:
        pickle.dump(ref, f)
    print(f"  saved -> {os.path.join(OUT_DIR, 'reference.pkl')}")
    print("\nNext: scripts/validate_scanvi_external.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
