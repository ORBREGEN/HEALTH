"""
Independent validation — run an EXTERNAL lung dataset through the deployed model
and test whether disease donors separate from that study's OWN healthy controls.

WHY THIS IS THE REAL TEST
-------------------------
The benchmark used HLCA-derived data — the same atlas the model was built from.
This script uses a *different* study (different patients, different sequencing).
Crucially, it compares disease donors against the healthy controls *from the same
study*, so batch/technical differences cancel: we measure deviation relative to
that lab's own healthy baseline, not an absolute score. That is what isolates real
biological signal from batch artefacts.

WHAT IT DOES
------------
For every donor in the external dataset, it builds a pseudo-bulk profile
(mean of adata.X over that donor's cells), scores it through the model, then
compares the deviation scores of disease donors vs. control donors and reports
the biology flagged in the disease group. The model never saw this data.

CONFIGURE the block below for your dataset, then run in Colab:
    !cd /content/SENEBICLABS && BENCH_LOCAL=0 python scripts/validate_external.py
(or BENCH_LOCAL=1 to score against a locally-built model).
"""

from __future__ import annotations

import os
import numpy as np
import pandas as pd
import requests
import scanpy as sc
from scipy.sparse import issparse

# ── Config — EDIT FOR YOUR DATASET ──────────────────────────────────────────────
# Default: Melms et al. 2021 "A molecular single-cell lung atlas of lethal
# COVID-19" — an independent study (not the HLCA) with COVID-19 + normal controls.
# Download: https://datasets.cellxgene.cziscience.com/75c059c8-8fb7-4e6e-a618-a3e01ac42060.h5ad
EXTERNAL_PATH = "/content/covid_lung.h5ad"
API_URL       = "https://senebiclabs-api-777437555578.us-central1.run.app"
DISEASE_COL   = "disease"            # obs column with disease labels
DONOR_COL     = "donor_id"           # obs column identifying donors/samples
SYMBOL_FIELD  = "feature_name"       # var column with HGNC symbols
# Which obs values count as healthy controls vs the disease of interest.
# Matched case-insensitively (substring).
CONTROL_TERMS = ["normal", "control", "healthy"]
DISEASE_TERMS = ["covid"]
CHUNK         = 20_000
MIN_CELLS     = 200                  # donors with fewer cells are skipped
OUT_CSV       = "external_validation_results.csv"

# ── Local vs API scoring (same mechanism as the benchmark) ──────────────────────
USE_LOCAL = os.environ.get("BENCH_LOCAL") == "1"
_local_analyse = None
if USE_LOCAL:
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.services.anomaly_detector import analyse as _local_analyse  # noqa: E402


def score_profile(sample_id: str, genes: dict) -> tuple[dict | None, str]:
    if USE_LOCAL:
        try:
            return _local_analyse(sample_id, genes).model_dump(), ""
        except Exception as exc:  # noqa: BLE001
            return None, f"local error: {exc}"
    try:
        r = requests.post(f"{API_URL}/api/v1/analyse",
                          json={"sample_id": sample_id, "gene_expression": genes}, timeout=120)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"
        return r.json(), ""
    except Exception as exc:  # noqa: BLE001
        return None, f"api error: {exc}"


def _group_of(label: str) -> str | None:
    low = label.lower()
    if any(t in low for t in CONTROL_TERMS):
        return "control"
    if any(t in low for t in DISEASE_TERMS):
        return "disease"
    return None


def main() -> int:
    print(f"Loading {EXTERNAL_PATH} (backed='r') ...")
    adata = sc.read_h5ad(EXTERNAL_PATH, backed="r")

    if SYMBOL_FIELD in adata.var.columns:
        symbols = adata.var[SYMBOL_FIELD].astype(str).to_numpy()
    else:
        print(f"  '{SYMBOL_FIELD}' not in var — using var_names")
        symbols = np.asarray(adata.var_names, dtype=str)
    n_genes = len(symbols)

    if DISEASE_COL not in adata.obs or DONOR_COL not in adata.obs:
        print(f"  obs columns available:\n{list(adata.obs.columns)}")
        raise SystemExit(f"Set DISEASE_COL / DONOR_COL to match your dataset.")

    disease_arr = adata.obs[DISEASE_COL].astype(str).to_numpy()
    donor_arr   = adata.obs[DONOR_COL].astype(str).to_numpy()

    # Map each donor -> group (disease/control), skipping donors whose label is neither
    donor_group: dict[str, str] = {}
    for d, lab in zip(donor_arr, disease_arr):
        if d in donor_group:
            continue
        g = _group_of(lab)
        if g:
            donor_group[d] = g
    donors = sorted(donor_group)
    n_dis = sum(1 for d in donors if donor_group[d] == "disease")
    n_ctl = sum(1 for d in donors if donor_group[d] == "control")
    print(f"Donors: {n_dis} disease, {n_ctl} control "
          f"(disease terms={DISEASE_TERMS}, control terms={CONTROL_TERMS})\n")
    if n_dis == 0 or n_ctl == 0:
        print("Unique disease labels in this dataset:")
        print(pd.Series(disease_arr).value_counts().head(20).to_string())
        raise SystemExit("Need both disease and control donors — adjust the TERMS lists above.")

    # Single sequential pass: accumulate per-donor pseudo-bulk (sums + counts)
    didx   = {d: i for i, d in enumerate(donors)}
    sums   = np.zeros((len(donors), n_genes), dtype=np.float64)
    counts = np.zeros(len(donors), dtype=np.int64)
    N = adata.n_obs
    print(f"Streaming {N:,} cells in {CHUNK:,}-row chunks ...", flush=True)
    for start in range(0, N, CHUNK):
        end = min(start + CHUNK, N)
        dlabels = donor_arr[start:end]
        present = [d for d in np.unique(dlabels) if d in didx]
        if not present:
            continue
        X = adata.X[start:end, :]
        X = X.tocsr() if issparse(X) else np.asarray(X, dtype=np.float64)
        for d in present:
            sel = np.where(dlabels == d)[0]
            sub = X[sel, :]
            i = didx[d]
            sums[i]   += np.asarray(sub.sum(axis=0)).ravel() if issparse(sub) else sub.sum(axis=0)
            counts[i] += len(sel)
        if (start // CHUNK) % 20 == 0:
            print(f"    {end:,}/{N:,} ...", flush=True)

    # Score each donor
    rows = []
    for d in donors:
        i = didx[d]
        n = int(counts[i])
        if n < MIN_CELLS:
            continue
        vec = sums[i] / counts[i]
        genes: dict[str, float] = {}
        for sym, val in zip(symbols, vec):
            v = float(val)
            if v > 0 and (sym not in genes or v > genes[sym]):
                genes[sym] = v
        report, err = score_profile(f"{donor_group[d]}:{d}", genes)
        if report is None:
            print(f"  {d} ({donor_group[d]}): {err}")
            continue
        score = report.get("overall_deviation_score", 0.0)
        elevated = [g["gene"] for g in sorted(report.get("gene_deviations", []),
                    key=lambda x: -x.get("z_score", 0)) if g.get("direction") == "elevated"][:8]
        pathways = [p.get("pathway", "") for p in report.get("pathway_deviations", [])]
        rows.append({
            "donor": d, "group": donor_group[d], "n_cells": n,
            "score_%": round(score * 100, 1),
            "top_elevated": ", ".join(elevated),
            "pathways": " | ".join(pathways[:3]),
        })
        print(f"  {donor_group[d]:7} {d:24} {score*100:5.1f}%", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT_CSV, index=False)

    # ── Report: do disease donors separate from this study's controls? ──────────
    dis = df[df.group == "disease"]["score_%"].to_numpy()
    ctl = df[df.group == "control"]["score_%"].to_numpy()

    print("\n" + "=" * 74)
    print("INDEPENDENT VALIDATION — disease vs. this study's own healthy controls")
    print("=" * 74)
    print(df.sort_values("score_%", ascending=False).to_string(index=False))

    def med(a): return float(np.median(a)) if len(a) else float("nan")
    # Rank-based separation (Mann-Whitney U / AUC): P(disease score > control score)
    auc = float("nan")
    if len(dis) and len(ctl):
        wins = sum(1 for x in dis for y in ctl if x > y) + 0.5 * sum(1 for x in dis for y in ctl if x == y)
        auc = wins / (len(dis) * len(ctl))

    print("\n" + "-" * 74)
    print(f"Disease donors:  n={len(dis):>3}   median deviation = {med(dis):5.1f}%")
    print(f"Control donors:  n={len(ctl):>3}   median deviation = {med(ctl):5.1f}%")
    print(f"Separation (AUC, P[disease > control]) = {auc:.2f}")
    print(f"  1.00 = perfect separation · 0.50 = no separation")
    verdict = ("STRONG" if auc >= 0.85 else "MODERATE" if auc >= 0.70 else
               "WEAK" if auc >= 0.60 else "NONE")
    print(f"  -> {verdict} separation on data the model never saw")
    print(f"\nSaved: {OUT_CSV}")
    print("\nThe model was built only from healthy cells and never saw this study.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
