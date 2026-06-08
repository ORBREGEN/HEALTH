"""
Build a standardized AnnData from GSE136831 (Adams et al. 2020, IPF lung atlas) for
the relative-scoring validation.

WHY: Adams/Kaminski is NOT one of the 14 HLCA-core datasets the model trained on, so
it is an independent cohort for our model — a strong cross-disease replication of the
relative-scoring result (it tests fibrosis, the biology the model recovered in-house).
It lives on GEO (not CELLxGene), so we assemble the .h5ad here to match what
validate_scanvi_external expects: raw counts, obs['disease'], obs['donor_id'], and
Ensembl-id var_names.

Output: /content/adams_ipf.h5ad   (disease values include IPF / Control / COPD)
Then validate with DISEASE_TERMS="IPF" CONTROL_TERMS="Control".

RUN (Colab, in-kernel — streams output, avoids subprocess buffering):
    import sys, importlib
    sys.path.insert(0, "/content/SENEBICLABS/scripts")
    import load_adams_ipf as L; importlib.reload(L); L.main()

Note: the raw matrix is ~312k cells. Reading it needs memory; if the runtime OOMs,
set ADAMS_MAX_CELLS (e.g. 150000) to subsample after load.
"""

from __future__ import annotations

import gzip
import os
import urllib.request

import anndata as ad
import numpy as np
import pandas as pd
import scipy.io
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
MAX_CELLS = int(os.environ.get("ADAMS_MAX_CELLS", "0"))   # 0 = keep all
SEED = 0


def _dl(name: str) -> str:
    os.makedirs(DEST, exist_ok=True)
    path = os.path.join(DEST, name)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        print(f"  downloading {name} ...", flush=True)
        urllib.request.urlretrieve(f"{BASE}/{name}", path)
    return path


def main() -> int:
    print("Downloading GSE136831 supplementary files (a few minutes) ...")
    mtx_p = _dl(FILES["mtx"]); genes_p = _dl(FILES["genes"])
    bc_p = _dl(FILES["bc"]);   meta_p = _dl(FILES["meta"])

    genes = pd.read_csv(genes_p, sep="\t")
    print(f"  genes file cols: {list(genes.columns)} ({len(genes)} rows)")
    barcodes = pd.read_csv(bc_p, sep="\t", header=None).iloc[:, 0].astype(str).to_numpy()
    print(f"  barcodes: {len(barcodes)} (first: {barcodes[0]})")
    meta = pd.read_csv(meta_p, sep="\t")
    print(f"  metadata cols: {list(meta.columns)} ({len(meta)} rows)")

    print("Reading sparse matrix (slow, ~minutes) ...", flush=True)
    with gzip.open(mtx_p, "rb") as f:
        X = scipy.io.mmread(f).tocsr()
    print(f"  raw matrix shape: {X.shape}")

    # Orient to cells x genes by matching dims to gene/barcode counts
    ng, nc = len(genes), len(barcodes)
    if X.shape == (ng, nc):
        X = X.T.tocsr()
    elif X.shape == (nc, ng):
        pass
    elif X.shape[0] == ng:
        X = X.T.tocsr()
    print(f"  oriented to {X.shape} (cells x genes)")
    # tolerate off-by-one header rows
    barcodes = barcodes[:X.shape[0]]
    genes = genes.iloc[:X.shape[1]]

    # Gene IDs: Ensembl column (values start with ENSG), version-stripped to match HLCA
    ens_col = next((c for c in genes.columns
                    if genes[c].astype(str).str.startswith("ENSG").mean() > 0.5), genes.columns[0])
    sym_col = next((c for c in genes.columns if c != ens_col), ens_col)
    ensembl = genes[ens_col].astype(str).str.split(".").str[0].to_numpy()
    symbols = genes[sym_col].astype(str).to_numpy()
    print(f"  Ensembl col '{ens_col}', symbol col '{sym_col}'")

    # Metadata: align to barcode order, find disease + donor columns
    bc_col = next((c for c in meta.columns
                   if meta[c].astype(str).isin(set(barcodes)).mean() > 0.5), None)
    if bc_col is not None:
        meta = meta.set_index(meta[bc_col].astype(str)).reindex(barcodes)
    else:
        print("  WARNING: no barcode column matched; assuming metadata is in matrix order")
        meta = meta.iloc[:len(barcodes)].set_index(pd.Index(barcodes))
    dis_col = next((c for c in meta.columns if meta[c].astype(str)
                    .str.contains("IPF|Control|COPD", case=False, na=False).mean() > 0.3), None)
    don_col = next((c for c in meta.columns if "subject" in c.lower() or "donor" in c.lower()), None)
    print(f"  disease col: '{dis_col}'  donor col: '{don_col}'")

    obs = pd.DataFrame(index=pd.Index(barcodes, name="cell"))
    obs["disease"] = meta[dis_col].astype(str).to_numpy() if dis_col else "unknown"
    obs["donor_id"] = meta[don_col].astype(str).to_numpy() if don_col else "unknown"

    var = pd.DataFrame({"feature_name": symbols}, index=pd.Index(ensembl, name="ensembl"))
    adata = ad.AnnData(X=X, obs=obs, var=var)
    adata.var_names_make_unique()

    if MAX_CELLS and adata.n_obs > MAX_CELLS:
        rng = np.random.default_rng(SEED)
        keep = np.sort(rng.choice(adata.n_obs, MAX_CELLS, replace=False))
        adata = adata[keep].copy()
        print(f"  subsampled to {adata.n_obs:,} cells (ADAMS_MAX_CELLS={MAX_CELLS})")

    print(f"\nBuilt AnnData: {adata.n_obs:,} cells x {adata.n_vars:,} genes")
    print("disease counts:\n" + adata.obs["disease"].value_counts().to_string())
    print(f"donors: {adata.obs['donor_id'].nunique()}")
    adata.write_h5ad(OUT)
    print(f"\nSaved -> {OUT}")
    print('Validate with: DISEASE_TERMS="IPF"  CONTROL_TERMS="Control"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
