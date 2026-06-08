"""
Build a standardized AnnData from GSE136831 (Adams et al. 2020, IPF lung atlas),
memory-safely, for the relative-scoring validation.

WHY: Adams/Kaminski is NOT one of the 14 HLCA-core datasets the model trained on, so
it is an independent cohort — a strong cross-disease replication (fibrosis) of the
relative-scoring result. It lives on GEO, not CELLxGene.

MEMORY-SAFE: the full matrix is ~312k cells and OOMs a normal runtime if read whole.
Instead we (1) pick only IPF + Control cells, capped per donor, then (2) STREAM the
sparse .mtx in chunks, keeping only those cells' entries. Never holds the full matrix.

Output: /content/adams_ipf.h5ad   (disease: IPF / Control; COPD dropped)
Validate with DISEASE_TERMS="IPF" CONTROL_TERMS="Control".

Tunables (env): ADAMS_PER_DONOR (cells kept per donor, default 1000).

RUN (Colab, in-kernel):
    import sys, importlib
    sys.path.insert(0, "/content/SENEBICLABS/scripts")
    import load_adams_ipf as L; importlib.reload(L); L.main()
"""

from __future__ import annotations

import gzip
import os
import urllib.request

import anndata as ad
import numpy as np
import pandas as pd
import scipy.sparse as sp

BASE = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE136nnn/GSE136831/suppl"
FILES = {
    "mtx":   "GSE136831_RawCounts_Sparse.mtx.gz",
    "genes": "GSE136831_AllCells.GeneIDs.txt.gz",
    "bc":    "GSE136831_AllCells.cellBarcodes.txt.gz",
    "meta":  "GSE136831_AllCells.Samples.CellType.MetadataTable.txt.gz",
}
DEST = "/content/gse136831"
OUT = "/content/adams_ipf.h5ad"
PER_DONOR = int(os.environ.get("ADAMS_PER_DONOR", "1000"))
KEEP_DISEASE = {"ipf", "control"}        # drop COPD to cut memory and stay on-target
CHUNK = 5_000_000                        # mtx triplet rows per streamed chunk
SEED = 0


def _dl(name: str) -> str:
    os.makedirs(DEST, exist_ok=True)
    path = os.path.join(DEST, name)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        print(f"  downloading {name} ...", flush=True)
        urllib.request.urlretrieve(f"{BASE}/{name}", path)
    return path


def _mtx_header(path):
    """Return (n_rows, n_cols, n_skip) where n_skip = lines before the data."""
    n_skip = 0
    with gzip.open(path, "rt") as f:
        for line in f:
            n_skip += 1
            if line.startswith("%"):
                continue
            parts = line.split()
            return int(parts[0]), int(parts[1]), n_skip
    raise RuntimeError("no dims line in mtx")


def main() -> int:
    print("Files (cached if already downloaded) ...")
    mtx_p = _dl(FILES["mtx"]); genes_p = _dl(FILES["genes"])
    bc_p = _dl(FILES["bc"]);   meta_p = _dl(FILES["meta"])

    genes = pd.read_csv(genes_p, sep="\t")
    ens_col = next((c for c in genes.columns
                    if genes[c].astype(str).str.startswith("ENSG").mean() > 0.5), genes.columns[0])
    sym_col = next((c for c in genes.columns if c != ens_col), ens_col)
    ensembl = genes[ens_col].astype(str).str.split(".").str[0].to_numpy()
    symbols = genes[sym_col].astype(str).to_numpy()
    n_genes = len(ensembl)

    barcodes = pd.read_csv(bc_p, sep="\t", header=None).iloc[:, 0].astype(str).to_numpy()
    meta = pd.read_csv(meta_p, sep="\t")
    bc_col = next((c for c in meta.columns
                   if meta[c].astype(str).isin(set(barcodes)).mean() > 0.5), meta.columns[0])
    meta = meta.set_index(meta[bc_col].astype(str)).reindex(barcodes)
    dis_col = next(c for c in meta.columns if meta[c].astype(str)
                   .str.contains("IPF|Control|COPD", case=False, na=False).mean() > 0.3)
    don_col = next(c for c in meta.columns if "subject" in c.lower() or "donor" in c.lower())
    disease = meta[dis_col].astype(str).to_numpy()
    donor = meta[don_col].astype(str).to_numpy()
    print(f"  genes={n_genes}, cells={len(barcodes)} | disease='{dis_col}' donor='{don_col}'")

    # ── Choose cells: IPF + Control, capped per donor ───────────────────────────
    dlow = pd.Series(disease).str.lower().to_numpy()
    elig = np.isin(dlow, list(KEEP_DISEASE))
    rng = np.random.default_rng(SEED)
    keep0 = []                                  # 0-indexed cell positions to keep
    for d in np.unique(donor[elig]):
        pos = np.where(elig & (donor == d))[0]
        if pos.size > PER_DONOR:
            pos = rng.choice(pos, PER_DONOR, replace=False)
        keep0.append(pos)
    keep0 = np.sort(np.concatenate(keep0))
    n_keep = keep0.size
    print(f"  keeping {n_keep:,} cells across {np.unique(donor[keep0]).size} IPF+Control donors "
          f"(cap {PER_DONOR}/donor)")

    # lookups over 1-indexed cell columns
    new_idx = np.full(len(barcodes) + 1, -1, dtype=np.int64)
    new_idx[keep0 + 1] = np.arange(n_keep)

    # ── Orientation: which mtx field is the cell index ──────────────────────────
    d0, d1, n_skip = _mtx_header(mtx_p)
    if d0 == n_genes and d1 == len(barcodes):
        gene_field, cell_field = 0, 1          # rows=genes, cols=cells
    elif d0 == len(barcodes) and d1 == n_genes:
        gene_field, cell_field = 1, 0
    else:
        gene_field, cell_field = 0, 1
        print(f"  WARNING: unexpected dims {d0}x{d1}; assuming genes x cells")
    print(f"  streaming mtx ({d0}x{d1}); skip {n_skip} header lines ...", flush=True)

    rows, cols, vals = [], [], []              # lists of small int32/float32 arrays
    reader = pd.read_csv(mtx_p, compression="gzip", sep=r"\s+", skiprows=n_skip,
                         header=None, names=["a", "b", "v"], chunksize=CHUNK,
                         dtype={"a": np.int64, "b": np.int64, "v": np.float32})
    seen = 0
    for ci, chunk in enumerate(reader):
        cell1 = chunk["b"].to_numpy() if cell_field == 1 else chunk["a"].to_numpy()
        gene1 = chunk["a"].to_numpy() if gene_field == 0 else chunk["b"].to_numpy()
        nr = new_idx[cell1]
        m = nr >= 0
        if m.any():
            rows.append(nr[m].astype(np.int32))
            cols.append((gene1[m] - 1).astype(np.int32))
            vals.append(chunk["v"].to_numpy()[m].astype(np.float32))
        seen += len(chunk)
        if ci % 10 == 0:
            print(f"    {seen:,} entries scanned ...", flush=True)

    rows = np.concatenate(rows); cols = np.concatenate(cols); vals = np.concatenate(vals)
    print(f"  kept {rows.size:,} nonzero entries; building matrix ...")
    X = sp.coo_matrix((vals, (rows, cols)), shape=(n_keep, n_genes)).tocsr()

    obs = pd.DataFrame({"disease": disease[keep0], "donor_id": donor[keep0]},
                       index=pd.Index(barcodes[keep0], name="cell"))
    var = pd.DataFrame({"feature_name": symbols}, index=pd.Index(ensembl, name="ensembl"))
    adata = ad.AnnData(X=X, obs=obs, var=var)
    adata.var_names_make_unique()

    print(f"\nBuilt AnnData: {adata.n_obs:,} cells x {adata.n_vars:,} genes")
    print("disease counts:\n" + adata.obs["disease"].value_counts().to_string())
    print(f"donors: {adata.obs['donor_id'].nunique()}")
    adata.write_h5ad(OUT)
    print(f"\nSaved -> {OUT}")
    print('Validate with: DISEASE_TERMS="IPF"  CONTROL_TERMS="Control"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
