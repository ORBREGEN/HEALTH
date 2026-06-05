"""
EXPERIMENT — per-gene technical noise floor via depth-downsampling simulation.

Idea (domain randomization, no disease knowledge): take HEALTHY cells, simulate
the same biology at different sequencing depths, and measure how much each gene's
pseudo-bulk moves under that purely technical perturbation. That per-gene movement
is its "technical noise floor". We then inflate each gene's reference std by it:

    effective_std = sqrt(biological_donor_std^2 + technical_std^2)

Genes that are technically unstable (the batch culprits — MFSD4B, RABGEF1, ...)
get a wider band, so a new cohort's technical offset no longer flags them. Genes
that are technically stable but biologically shifted in disease still flag.

The model never sees a disease. Only healthy cells are perturbed.

This patches models/respiratory_model/gene_stats.json in place (with a backup),
so you can immediately re-run validate_external (BENCH_LOCAL=1) and compare AUC.

RUN in Colab (needs HLCA Core — all healthy, ~5.5GB):
    download core to /content/hlca_core.h5ad, then
    !cd /content/SENEBICLABS && python scripts/experiment_technical_floor.py
"""

import json
import numpy as np
import scanpy as sc
from scipy.sparse import issparse, diags, coo_matrix

CORE_PATH       = "/content/hlca_core.h5ad"
MODEL_DIR       = "/content/SENEBICLABS/models/respiratory_model"
SYMBOL_FIELD    = "feature_name"
DONOR_COL       = "donor_id"
N_DONORS        = 40            # healthy donors sampled
CELLS_PER_DONOR = 2000
N_REPLICATES    = 6            # technical replicates per donor
DEPTH_FRACTIONS = [0.3, 0.5, 0.7]   # simulated sequencing-depth fractions


def _pseudobulk_log1p_cp10k(counts) -> np.ndarray:
    totals = np.asarray(counts.sum(axis=1)).ravel().astype(np.float64)
    totals[totals == 0] = 1.0
    if issparse(counts):
        Xn = diags(1.0 / totals) @ counts.astype(np.float64) * 1e4
        Xn = Xn.log1p()
        return np.asarray(Xn.mean(axis=0)).ravel()
    X = np.asarray(counts, dtype=np.float64)
    Xn = np.log1p(X / totals[:, None] * 1e4)
    return Xn.mean(axis=0)


def _downsample(counts, frac, rng):
    """Binomial downsampling of integer counts -> simulates lower sequencing depth."""
    if issparse(counts):
        c = counts.tocoo()
        newdata = rng.binomial(np.rint(c.data).astype(np.int64), frac)
        return coo_matrix((newdata, (c.row, c.col)), shape=counts.shape).tocsr()
    return rng.binomial(np.rint(counts).astype(np.int64), frac)


def main() -> int:
    print(f"Loading {CORE_PATH} (backed='r') ...")
    a = sc.read_h5ad(CORE_PATH, backed="r")

    use_raw = a.raw is not None
    src = a.raw if use_raw else a
    # symbols for the counts matrix we sample from
    var = src.var if use_raw else a.var
    rsym = (var[SYMBOL_FIELD].astype(str).to_numpy()
            if SYMBOL_FIELD in var.columns else np.asarray(src.var_names, dtype=str))

    # sanity: counts should be integers (raw). If .X is already normalized, warn.
    probe = src.X[:50, :]
    probe = probe.toarray() if issparse(probe) else np.asarray(probe)
    looks_counts = float(probe.max()) > 30 and np.allclose(probe[probe > 0], np.rint(probe[probe > 0]))
    print(f"counts source: {'adata.raw' if use_raw else 'adata.X'} | "
          f"max={probe.max():.1f} | looks like raw counts: {looks_counts}")
    if not looks_counts:
        print("WARNING: source doesn't look like raw counts; downsampling may be invalid.")

    donors = a.obs[DONOR_COL].astype(str).to_numpy()
    vc = a.obs[DONOR_COL].astype(str).value_counts()
    chosen = vc[vc >= CELLS_PER_DONOR].index.tolist()[:N_DONORS]
    print(f"Using {len(chosen)} healthy donors x {N_REPLICATES} technical replicates ...\n")

    rng = np.random.default_rng(0)
    per_donor_std = []
    for k, d in enumerate(chosen):
        pos = np.where(donors == d)[0]
        pos = np.sort(rng.choice(pos, CELLS_PER_DONOR, replace=False))
        X = src.X[pos, :]
        X = X.tocsr() if issparse(X) else np.asarray(X)
        reps = []
        for _ in range(N_REPLICATES):
            frac = float(rng.choice(DEPTH_FRACTIONS))
            reps.append(_pseudobulk_log1p_cp10k(_downsample(X, frac, rng)))
        reps = np.vstack(reps)
        per_donor_std.append(reps.std(axis=0))   # per-gene std across technical reps
        if k % 10 == 0:
            print(f"    donor {k+1}/{len(chosen)} ...", flush=True)

    tech_std = np.mean(np.vstack(per_donor_std), axis=0)   # average over donors
    tech_by_sym: dict[str, float] = {}
    for s, v in zip(rsym, tech_std):
        tech_by_sym[s] = max(tech_by_sym.get(s, 0.0), float(v))

    # ── Patch gene_stats.json: inflate std by the technical floor ───────────────
    gs_path = f"{MODEL_DIR}/gene_stats.json"
    gs = json.load(open(gs_path))
    json.dump(gs, open(f"{MODEL_DIR}/gene_stats.backup.json", "w"))
    patched = 0
    for g, st in gs.items():
        t = tech_by_sym.get(g)
        if t and t > 0:
            st["std"] = float(np.sqrt(float(st["std"]) ** 2 + t ** 2))
            patched += 1
    json.dump(gs, open(gs_path, "w"))

    print(f"\nPatched {patched}/{len(gs)} genes with a technical noise floor.")
    print(f"median technical_std = {np.median(tech_std):.3f} (log1p CP10K)")
    print(f"Backup saved: {MODEL_DIR}/gene_stats.backup.json")
    print("\nNow re-run validate_external with BENCH_LOCAL=1 to compare the AUC.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
