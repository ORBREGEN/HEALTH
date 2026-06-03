"""
Disease benchmark — sensitivity of the Healthy Respiratory Model across every
disease condition in the HLCA.

WHAT THIS DOES
--------------
For each disease in HLCA Full (everything except `normal`), it builds a
pseudo-bulk expression profile from the real disease cells and runs that profile
through the EXISTING model via the deployed API. It records the deviation score,
the flagged genes/pathways, and grades the output against an expected-biology key.

WHAT THIS DOES NOT DO
---------------------
It never retrains, rebuilds, or touches the model. The model stays disease-naive
(built only from `disease == 'normal'` cells). Disease cells are read ONLY to
create test inputs. The expectation key below is used solely to GRADE the model's
output — it is never sent to the model. The model sees only {gene_symbol: value}.

NORMALIZATION (must match the model build exactly)
--------------------------------------------------
Model build: raw counts -> per cell log1p(counts / total * 1e4)  [respiratory_model.py:_normalize]
This script reproduces that per cell, then averages across the disease's cells.

RUN
---
Colab (where hlca_full.h5ad lives):
    !git clone https://github.com/ORBREGEN/HEALTH.git
    %cd HEALTH
    # set HLCA_PATH below to your Drive path
    !python scripts/benchmark_diseases.py
"""

from __future__ import annotations

import sys
import json
import numpy as np
import pandas as pd
import requests
import scanpy as sc
from scipy.sparse import issparse

# ── Config ──────────────────────────────────────────────────────────────────────

HLCA_PATH    = "data/hlca_full.h5ad"     # in Colab: e.g. /content/drive/MyDrive/.../hlca_full.h5ad
API_URL      = "https://senebiclabs-api-777437555578.us-central1.run.app"
DISEASE_COL  = "disease"
SYMBOL_FIELD = "feature_name"            # HLCA var column holding HGNC symbols; falls back to var_names
CHUNK        = 20_000                    # cells per chunk — bounds memory on large diseases
OUT_CSV      = "disease_benchmark_results.csv"

# Expected biology per disease — the GRADING KEY ONLY. Never sent to the model.
# A disease "passes" if the model flags a substantial deviation AND surfaces at
# least one of the expected pathway/gene themes. Themes are matched case-insensitively
# against the model's returned pathway names and elevated gene symbols.
EXPECTED = {
    "pulmonary fibrosis":               ["fibros", "tgf", "emt", "col1a1", "col3a1", "fn1", "postn"],
    "non-specific interstitial pneumonia": ["fibros", "tgf", "col1a1", "emt"],
    "hypersensitivity pneumonitis":     ["fibros", "tgf", "immune", "myeloid", "macrophage"],
    "interstitial lung disease":        ["fibros", "tgf", "col1a1", "emt"],
    "COVID-19":                         ["interferon", "cytokine", "nf-kb", "myeloid", "cxcl10", "isg"],
    "pneumonia":                        ["myeloid", "cytokine", "nf-kb", "il6", "cxcl8", "neutrophil"],
    "COPD":                             ["airway", "mucocil", "mucus", "epithel", "muc5", "inflamm"],
    "pulmonary sarcoidosis":            ["macrophage", "myeloid", "immune", "granulom", "t cell"],
    "lung adenocarcinoma":              ["prolifer", "epithel", "cell cycle", "mki67"],
    "squamous cell lung carcinoma":     ["squamous", "krt5", "tp63", "prolifer", "epithel"],
    "lung large cell carcinoma":        ["prolifer", "epithel", "cell cycle"],
    "pleomorphic carcinoma":            ["prolifer", "epithel", "emt"],
    "lymphangioleiomyomatosis":         ["smooth muscle", "acta2", "myh11", "mtor"],
    "cystic fibrosis":                  ["airway", "mucus", "muc5", "inflamm", "epithel"],
    "chronic rhinitis":                 ["airway", "epithel", "goblet", "mucus", "inflamm"],
}

DEVIATION_PASS = 0.20   # a disease should score clearly above healthy (healthy ≈ 0.00)


# ── Pseudo-bulk ─────────────────────────────────────────────────────────────────

def pseudobulk_log1p_cp10k(adata, mask: np.ndarray, n_genes: int) -> np.ndarray:
    """Mean over cells of per-cell log1p(CP10K). Chunked + sparse-safe.

    Matches respiratory_model._normalize: raw counts -> log1p(counts/total*1e4).
    Returns a dense vector of length n_genes (the per-cell normalized mean).
    """
    idx = np.where(mask)[0]
    running = np.zeros(n_genes, dtype=np.float64)
    seen = 0
    for start in range(0, len(idx), CHUNK):
        rows = idx[start:start + CHUNK]
        X = adata.X[rows, :]
        if issparse(X):
            X = X.toarray()
        X = np.asarray(X, dtype=np.float64)
        totals = X.sum(axis=1, keepdims=True)
        totals[totals == 0] = 1.0                 # guard empty cells
        Xn = np.log1p(X / totals * 10_000.0)      # per-cell log1p CP10K
        running += Xn.sum(axis=0)
        seen += Xn.shape[0]
    if seen == 0:
        return running
    return running / seen


# ── Grading ─────────────────────────────────────────────────────────────────────

def grade(disease: str, report: dict) -> tuple[bool, str]:
    score    = report.get("overall_deviation_score", 0.0)
    pathways = [p.get("pathway", "").lower() for p in report.get("pathway_deviations", [])]
    elevated = [g.get("gene", "").lower() for g in report.get("gene_deviations", [])
                if g.get("direction") == "elevated"]
    haystack = " ".join(pathways + elevated)

    themes = EXPECTED.get(disease, [])
    theme_hit = any(t in haystack for t in themes) if themes else None

    score_ok = score >= DEVIATION_PASS
    if themes:
        ok = score_ok and bool(theme_hit)
        why = []
        if not score_ok: why.append(f"score {score*100:.0f}% < {DEVIATION_PASS*100:.0f}%")
        if not theme_hit: why.append("no expected biology flagged")
        return ok, ("; ".join(why) or "score + biology match")
    # No key for this disease — only check it deviates from healthy
    return score_ok, ("deviates" if score_ok else f"score {score*100:.0f}% low (no biology key)")


# ── Main ────────────────────────────────────────────────────────────────────────

def main() -> int:
    print(f"Loading {HLCA_PATH} (backed='r') ...")
    adata = sc.read_h5ad(HLCA_PATH, backed="r")

    # Use HGNC symbols to match the model's gene keys
    if SYMBOL_FIELD in adata.var.columns:
        symbols = adata.var[SYMBOL_FIELD].astype(str).to_numpy()
    else:
        print(f"  '{SYMBOL_FIELD}' not in var — falling back to var_names")
        symbols = np.asarray(adata.var_names, dtype=str)
    n_genes = len(symbols)

    diseases = [d for d in adata.obs[DISEASE_COL].astype(str).unique() if d.lower() != "normal"]
    diseases.sort()
    print(f"Found {len(diseases)} disease conditions to benchmark.\n")

    rows = []
    for disease in diseases:
        mask = (adata.obs[DISEASE_COL].astype(str) == disease).to_numpy()
        n_cells = int(mask.sum())
        if n_cells == 0:
            continue
        print(f"  [{disease}]  {n_cells:,} cells — building pseudo-bulk ...", flush=True)

        vec = pseudobulk_log1p_cp10k(adata, mask, n_genes)

        # Collapse duplicate symbols (keep max-expressed), drop zeros
        genes: dict[str, float] = {}
        for sym, val in zip(symbols, vec):
            v = float(val)
            if v <= 0.0:
                continue
            if sym not in genes or v > genes[sym]:
                genes[sym] = v

        try:
            r = requests.post(f"{API_URL}/api/v1/analyse",
                              json={"sample_id": disease, "gene_expression": genes},
                              timeout=120)
            report = r.json()
            if r.status_code != 200:
                rows.append({"disease": disease, "n_cells": n_cells, "status": f"HTTP {r.status_code}",
                             "score_%": None, "genes_flagged": None, "pathways": "", "pass": False})
                print(f"      HTTP {r.status_code}: {str(report)[:120]}")
                continue
        except Exception as exc:  # noqa: BLE001
            rows.append({"disease": disease, "n_cells": n_cells, "status": f"ERR {exc}",
                         "score_%": None, "genes_flagged": None, "pathways": "", "pass": False})
            continue

        score    = report.get("overall_deviation_score", 0.0)
        pathways = [p.get("pathway", "") for p in report.get("pathway_deviations", [])]
        ok, note = grade(disease, report)

        rows.append({
            "disease":       disease,
            "n_cells":       n_cells,
            "status":        "ok",
            "score_%":       round(score * 100, 1),
            "genes_flagged": len(report.get("gene_deviations", [])),
            "pathways":      " | ".join(pathways[:3]),
            "pass":          ok,
            "note":          note,
        })
        print(f"      score={score*100:5.1f}%  {'PASS' if ok else 'FAIL'}  ({note})")

    df = pd.DataFrame(rows).sort_values("score_%", ascending=False, na_position="last")
    df.to_csv(OUT_CSV, index=False)

    print("\n" + "=" * 78)
    print("DISEASE BENCHMARK — sensitivity of the healthy-lung model")
    print("=" * 78)
    with pd.option_context("display.max_rows", None, "display.width", 200,
                           "display.max_colwidth", 60):
        print(df.to_string(index=False))

    graded = df[df["status"] == "ok"]
    n_pass = int(graded["pass"].sum())
    n_tot  = len(graded)
    print("\n" + "-" * 78)
    print(f"Detected (deviation + expected biology): {n_pass}/{n_tot}  "
          f"({100*n_pass/max(n_tot,1):.0f}%)")
    print(f"Saved: {OUT_CSV}")
    print("\nReminder: the model never saw these diseases. It scored deviation from")
    print("healthy only. The expectation key graded the output, not the model.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
