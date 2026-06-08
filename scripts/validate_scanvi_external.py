"""
Independent validation in the scANVI latent space, with PER-COMPARTMENT scoring.

Pipeline:
  1. load the trained healthy scANVI reference (train_scanvi_reference.py),
  2. map the external cohort in via scArches surgery (one new batch),
  3. let scANVI TRANSFER cell-type labels onto the external cells,
  4. for each donor, score Mahalanobis deviation from health WITHIN each predicted
     compartment, standardize against that compartment's healthy spread, and
     aggregate the most-deviant compartments (top-k mean),
  5. report AUC for the per-compartment score AND the whole-donor baseline.

Why per-compartment: COVID's interferon program lives in myeloid/epithelial cells.
A whole-donor average buries it; scoring inside each compartment surfaces it even if
a uniform cross-cohort offset elevates every donor.

Disease-blind throughout: surgery uses the batch label; label transfer uses healthy
cell-type labels; no disease label anywhere.

RUN (Colab GPU, in-kernel, after train_scanvi_reference.py):
    import os, sys, importlib
    os.environ["EXTERNAL_PATH"] = "/content/covid_lung.h5ad"
    sys.path.insert(0, "/content/SENEBICLABS/scripts")
    import validate_scanvi_external as V; importlib.reload(V); V.main()
"""

from __future__ import annotations

import os
import sys
import pickle

import numpy as np
import pandas as pd
import scanpy as sc
from scipy.sparse import issparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# ── Config ──────────────────────────────────────────────────────────────────────
EXTERNAL_PATH  = os.environ.get("EXTERNAL_PATH", "/content/covid_lung.h5ad")
REF_DIR        = os.path.join(ROOT, "models", "scanvi_reference")
DISEASE_COL    = "disease"
DONOR_COL      = "donor_id"
CONTROL_TERMS  = ["normal", "control", "healthy"]
DISEASE_TERMS  = ["covid"]
MIN_CELLS      = 200          # min cells for a donor to be scored
MIN_CELLS_CT   = 20           # min cells of a compartment to score it for a donor
TOPK           = 3            # aggregate the K most-deviant compartments per donor
SURGERY_EPOCHS = int(os.environ.get("SCVI_SURGERY_EPOCHS", "100"))
OUT_CSV        = "external_validation_scanvi.csv"
SEED           = 0


def _group_of(label):
    low = str(label).lower()
    if any(t in low for t in CONTROL_TERMS):
        return "control"
    if any(t in low for t in DISEASE_TERMS):
        return "disease"
    return None


def _counts_adata(adata):
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
    print(f"  query counts: max={float(probe.max()):.1f} | "
          f"looks like counts: {nz.size == 0 or (float(probe.max())>20 and np.allclose(nz, np.rint(nz)))}")
    return a


def _maha(v, mu, cov_inv):
    d = v - mu
    return float(np.sqrt(d @ cov_inv @ d))


def _auc(dis, ctl):
    if not len(dis) or not len(ctl):
        return float("nan")
    wins = sum(x > y for x in dis for y in ctl) + 0.5 * sum(x == y for x in dis for y in ctl)
    return wins / (len(dis) * len(ctl))


def main() -> int:
    import scvi
    scvi.settings.seed = SEED

    with open(os.path.join(REF_DIR, "reference.pkl"), "rb") as f:
        ref = pickle.load(f)
    batch_key, label_key = ref["batch_key"], ref["label_key"]
    ct_stats = ref["ct_stats"]
    print(f"Reference: {len(ct_stats)} compartments, latent {ref['n_latent']}, "
          f"whole-donor yardstick {ref['whole_yard']:.2f}\n")

    print(f"Loading {EXTERNAL_PATH} ...")
    adata = sc.read_h5ad(EXTERNAL_PATH)
    if DISEASE_COL not in adata.obs or DONOR_COL not in adata.obs:
        raise SystemExit(f"Set DISEASE_COL/DONOR_COL. obs has: {list(adata.obs.columns)}")
    donor_group = {}
    for d, lab in zip(adata.obs[DONOR_COL].astype(str), adata.obs[DISEASE_COL].astype(str)):
        if d not in donor_group and (g := _group_of(lab)):
            donor_group[d] = g
    n_dis = sum(v == "disease" for v in donor_group.values())
    n_ctl = sum(v == "control" for v in donor_group.values())
    print(f"Donors: {n_dis} disease, {n_ctl} control")
    if not n_dis or not n_ctl:
        print(pd.Series(adata.obs[DISEASE_COL].astype(str)).value_counts().head(20).to_string())
        raise SystemExit("Need both groups — adjust TERMS.")
    adata = adata[adata.obs[DONOR_COL].astype(str).isin(donor_group)].copy()

    # ── Surgery + label transfer ────────────────────────────────────────────────
    query = _counts_adata(adata)
    query.var_names_make_unique()
    query.obs[batch_key] = "external_query"          # one new batch
    query.obs[label_key] = "Unknown"                 # unlabeled -> scANVI predicts
    print(f"Aligning query genes to reference ({len(ref['var_names'])} genes) ...")
    scvi.model.SCANVI.prepare_query_anndata(query, REF_DIR)
    print(f"scArches surgery ({SURGERY_EPOCHS} epochs) ...")
    qm = scvi.model.SCANVI.load_query_data(query, REF_DIR)
    qm.train(max_epochs=SURGERY_EPOCHS, plan_kwargs={"weight_decay": 0.0})
    Zq = qm.get_latent_representation()
    pred = np.asarray(qm.predict())                  # transferred cell-type label per cell
    print(f"Transferred labels across {len(np.unique(pred))} compartments\n")

    # ── Per-donor scoring ───────────────────────────────────────────────────────
    donors = query.obs[DONOR_COL].astype(str).to_numpy()
    rows = []
    latent_rows = []          # (donor, group, whole-donor latent vector) for relative scoring
    for d in sorted(donor_group):
        sel = np.where(donors == d)[0]
        if sel.size < MIN_CELLS:
            continue
        # whole-donor baseline
        v = Zq[sel].mean(axis=0)
        latent_rows.append((d, donor_group[d], v))
        base = _maha(v, ref["whole_mu"], ref["whole_cov_inv"])
        # per-compartment standardized deviations
        comp = []
        for ct in np.unique(pred[sel]):
            if ct not in ct_stats:
                continue
            ct_cells = sel[pred[sel] == ct]
            if ct_cells.size < MIN_CELLS_CT:
                continue
            dd = _maha(Zq[ct_cells].mean(axis=0), ct_stats[ct]["mu"], ct_stats[ct]["cov_inv"])
            z = (dd - ct_stats[ct]["ref_med"]) / ct_stats[ct]["ref_std"]
            comp.append((z, ct))
        comp.sort(reverse=True)
        topk = [z for z, _ in comp[:TOPK]]
        score = float(np.mean(topk)) if topk else float("nan")
        drivers = ", ".join(f"{ct}({z:.1f})" for z, ct in comp[:TOPK])
        rows.append({"donor": d, "group": donor_group[d], "n_cells": int(sel.size),
                     "compartment_score": round(score, 2), "whole_donor": round(base, 2),
                     "top_compartments": drivers})
        print(f"  {donor_group[d]:7} {d:18} score={score:6.2f}  [{drivers}]")

    df = pd.DataFrame(rows)
    df.to_csv(OUT_CSV, index=False)

    dis = df[df.group == "disease"]["compartment_score"].dropna().to_numpy()
    ctl = df[df.group == "control"]["compartment_score"].dropna().to_numpy()
    bdis = df[df.group == "disease"]["whole_donor"].to_numpy()
    bctl = df[df.group == "control"]["whole_donor"].to_numpy()
    auc_c, auc_b = _auc(dis, ctl), _auc(bdis, bctl)

    # ── Relative-to-own-controls scoring (the "bring-your-own-controls" mode) ────
    # Score each donor by distance from the cohort's OWN control centroid in the
    # latent space, not the European reference. The shared batch+ancestry offset
    # cancels because both groups come from the same cohort. Leave-one-out for
    # controls so they are not trivially close to their own centroid.
    ctl_all = np.vstack([v for _, g, v in latent_rows if g == "control"])
    rel = {}
    for d, g, v in latent_rows:
        if g == "control":
            others = np.vstack([vv for dd, gg, vv in latent_rows
                                if gg == "control" and dd != d])
            centroid = others.mean(axis=0)
        else:
            centroid = ctl_all.mean(axis=0)
        rel[d] = float(np.linalg.norm(v - centroid))
    rdis = np.array([rel[d] for d, g, _ in latent_rows if g == "disease"])
    rctl = np.array([rel[d] for d, g, _ in latent_rows if g == "control"])
    auc_rel = _auc(rdis, rctl)

    def med(a): return float(np.median(a)) if len(a) else float("nan")
    print("\n" + "=" * 76)
    print("INDEPENDENT VALIDATION — scANVI, per-compartment (raw genes:0.29 | scVI whole:0.49)")
    print("=" * 76)
    print(df.sort_values("compartment_score", ascending=False).to_string(index=False))
    print("-" * 76)
    print(f"PER-COMPARTMENT  control median={med(ctl):6.2f}  disease median={med(dis):6.2f}"
          f"   AUC = {auc_c:.2f}")
    print(f"WHOLE-DONOR base control median={med(bctl):6.2f}  disease median={med(bdis):6.2f}"
          f"   AUC = {auc_b:.2f}")
    print(f"RELATIVE (own controls) control median={med(rctl):6.2f}  disease median={med(rdis):6.2f}"
          f"   AUC = {auc_rel:.2f}   <- the bring-your-own-controls mode")
    best = max(auc_c, auc_b, auc_rel)
    verdict = ("STRONG" if best >= 0.85 else "MODERATE" if best >= 0.70 else
               "WEAK" if best >= 0.60 else "NONE")
    print(f"  -> best separation: {verdict} (AUC {best:.2f})")
    print("\nRELATIVE is the product-relevant number: it scores against the cohort's own")
    print("controls, so batch and ancestry cancel. If it clears 0.7 where absolute (vs the")
    print("European reference) stayed ~0.5, the bring-your-own-controls mode works.")
    print(f"Saved: {OUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
