"""
Independent validation IN THE scVI LATENT SPACE.

This is the rematch. validate_external.py scored deviation in raw gene space and
got AUC 0.29 (no separation) because the cross-lab batch shift drowned the biology.
Here we instead:

  1. load the trained healthy scVI reference (train_scvi_reference.py),
  2. map the external cohort in via scArches "surgery" (load_query_data) — this
     absorbs the new lab's technical fingerprint into a new batch embedding,
  3. score each external donor by Mahalanobis distance from the HEALTHY latent
     distribution, and
  4. report AUC: do disease donors separate from this study's OWN controls?

Same disease-blind principle throughout: surgery uses the BATCH label of the query
(one new category), never a disease label.

WHAT TO LOOK FOR
----------------
  AUC > 0.7  -> the latent space recovered the biology the batch effect was hiding. Win.
  AUC ~ 0.5  -> OVER-correction: surgery pulled disease onto healthy too; the signal
                was erased along with the batch. Informative failure — tune surgery
                (fewer epochs / freeze more) or n_latent.
  control Mahalanobis near the reference yardstick, disease well above it -> good sign.
  both control AND disease far above reference -> UNDER-correction (surgery didn't
                absorb the batch); train surgery longer.

RUN (Colab, GPU, after train_scvi_reference.py):
    !cd /content/HEALTH && \
        EXTERNAL_PATH=/content/covid_lung.h5ad \
        python scripts/validate_scvi_external.py
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import scanpy as sc
from scipy.sparse import issparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# ── Config (mirror validate_external.py) ─────────────────────────────────────────
EXTERNAL_PATH  = os.environ.get("EXTERNAL_PATH", "/content/covid_lung.h5ad")
REF_DIR        = os.path.join(ROOT, "models", "scvi_reference")
DISEASE_COL    = "disease"
DONOR_COL      = "donor_id"
CONTROL_TERMS  = ["normal", "control", "healthy"]
DISEASE_TERMS  = ["covid"]
MIN_CELLS      = 200
SURGERY_EPOCHS = int(os.environ.get("SCVI_SURGERY_EPOCHS", "100"))
OUT_CSV        = "external_validation_scvi.csv"
SEED           = 0


def _group_of(label: str) -> str | None:
    low = str(label).lower()
    if any(t in low for t in CONTROL_TERMS):
        return "control"
    if any(t in low for t in DISEASE_TERMS):
        return "disease"
    return None


def _counts_adata(adata):
    """AnnData with X = raw counts, keyed by Ensembl var_names (CellxGene convention)."""
    import anndata as ad
    if adata.raw is not None:
        Xc, var = adata.raw.X, adata.raw.var.copy()
    elif "counts" in adata.layers:
        Xc, var = adata.layers["counts"], adata.var.copy()
    else:
        Xc, var = adata.X, adata.var.copy()
    a = ad.AnnData(X=Xc.copy(), obs=adata.obs.copy(), var=var)
    probe = a.X[:50]
    probe = probe.toarray() if issparse(probe) else np.asarray(probe)
    nz = probe[probe > 0]
    looks = nz.size == 0 or (float(nz.max()) > 20 and np.allclose(nz, np.rint(nz)))
    print(f"  query counts: max={float(probe.max()):.1f} | looks like counts: {looks}")
    return a


def main() -> int:
    import scvi

    scvi.settings.seed = SEED

    ref = np.load(os.path.join(REF_DIR, "healthy_latent.npz"), allow_pickle=True)
    mu, cov = ref["mu"], ref["cov"]
    cov_inv = np.linalg.pinv(cov)
    M_ref = ref["donor_matrix"]
    self_d = np.array([float(np.sqrt((v - mu) @ cov_inv @ (v - mu))) for v in M_ref])
    ref_yardstick = float(np.median(self_d))
    ref_var_names = np.load(os.path.join(REF_DIR, "ref_var_names.npy"), allow_pickle=True)
    print(f"Reference: {M_ref.shape[0]} healthy donors, latent dim {M_ref.shape[1]}, "
          f"Mahalanobis yardstick (median) = {ref_yardstick:.2f}\n")

    # ── Load external cohort, assign donor groups ───────────────────────────────
    print(f"Loading {EXTERNAL_PATH} ...")
    adata = sc.read_h5ad(EXTERNAL_PATH)
    if DISEASE_COL not in adata.obs or DONOR_COL not in adata.obs:
        raise SystemExit(f"Set DISEASE_COL/DONOR_COL. obs has: {list(adata.obs.columns)}")
    # build per-donor group (first label wins)
    donor_group: dict[str, str] = {}
    for d, lab in zip(adata.obs[DONOR_COL].astype(str), adata.obs[DISEASE_COL].astype(str)):
        if d in donor_group:
            continue
        g = _group_of(lab)
        if g:
            donor_group[d] = g
    n_dis = sum(v == "disease" for v in donor_group.values())
    n_ctl = sum(v == "control" for v in donor_group.values())
    print(f"Donors: {n_dis} disease, {n_ctl} control")
    if not n_dis or not n_ctl:
        print(pd.Series(adata.obs[DISEASE_COL].astype(str)).value_counts().head(20).to_string())
        raise SystemExit("Need both disease and control donors — adjust TERMS.")

    # keep only labelled donors
    keep = adata.obs[DONOR_COL].astype(str).isin(donor_group).to_numpy()
    adata = adata[keep].copy()

    # ── Prepare query genes to match the reference, then scArches surgery ────────
    query = _counts_adata(adata)
    query.var_names_make_unique()
    print(f"Aligning query genes to reference ({len(ref_var_names)} genes) ...")
    scvi.model.SCVI.prepare_query_anndata(query, REF_DIR)  # subsets/zero-pads to ref genes

    print(f"scArches surgery ({SURGERY_EPOCHS} epochs) — absorbing this lab's batch signature ...")
    q_model = scvi.model.SCVI.load_query_data(query, REF_DIR)
    q_model.train(max_epochs=SURGERY_EPOCHS, plan_kwargs={"weight_decay": 0.0})
    Zq = q_model.get_latent_representation()

    # ── Per-donor latent pseudobulk -> Mahalanobis deviation from healthy ───────
    donors = query.obs[DONOR_COL].astype(str).to_numpy()
    rows = []
    for d in sorted(donor_group):
        sel = np.where(donors == d)[0]
        if sel.size < MIN_CELLS:
            continue
        v = Zq[sel].mean(axis=0)
        dist = float(np.sqrt((v - mu) @ cov_inv @ (v - mu)))
        rows.append({"donor": d, "group": donor_group[d], "n_cells": int(sel.size),
                     "mahalanobis": round(dist, 2)})
        print(f"  {donor_group[d]:7} {d:24} d={dist:6.2f}")

    df = pd.DataFrame(rows)
    df.to_csv(OUT_CSV, index=False)

    dis = df[df.group == "disease"]["mahalanobis"].to_numpy()
    ctl = df[df.group == "control"]["mahalanobis"].to_numpy()
    auc = float("nan")
    if len(dis) and len(ctl):
        wins = sum(x > y for x in dis for y in ctl) + 0.5 * sum(x == y for x in dis for y in ctl)
        auc = wins / (len(dis) * len(ctl))

    def med(a): return float(np.median(a)) if len(a) else float("nan")
    print("\n" + "=" * 74)
    print("INDEPENDENT VALIDATION — scVI latent space (vs raw-gene AUC 0.29)")
    print("=" * 74)
    print(df.sort_values("mahalanobis", ascending=False).to_string(index=False))
    print("-" * 74)
    print(f"Reference healthy yardstick (median Mahalanobis) = {ref_yardstick:.2f}")
    print(f"Control donors:  n={len(ctl):>3}   median = {med(ctl):6.2f}")
    print(f"Disease donors:  n={len(dis):>3}   median = {med(dis):6.2f}")
    print(f"Separation (AUC, P[disease > control]) = {auc:.2f}   (0.50 = none, 1.00 = perfect)")
    verdict = ("STRONG" if auc >= 0.85 else "MODERATE" if auc >= 0.70 else
               "WEAK" if auc >= 0.60 else "NONE")
    print(f"  -> {verdict} separation in the batch-corrected latent space")
    if auc < 0.6:
        print("  Diagnosis hint: control near yardstick + disease near yardstick => OVER-corrected"
              "\n                  control & disease both far above => UNDER-corrected (train surgery longer)")
    print(f"\nSaved: {OUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
