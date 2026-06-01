"""
Export demo h5ad files from hlca_full.h5ad for platform demonstration.

Run this in the Colab notebook where hlca_full.h5ad was downloaded.
After running, download demo_covid19.h5ad and demo_pulmonary_fibrosis.h5ad
and place them in the local data/ folder.

Usage (in Colab):
    !python export_demo_samples.py
    # or paste the cells directly into a notebook
"""

import scanpy as sc
import os

# ── Locate the HLCA full file ──────────────────────────────────────────────────
CANDIDATES = [
    'data/hlca_full.h5ad',
    '/content/hlca_full.h5ad',
    '/content/drive/MyDrive/hlca_full.h5ad',
    '/content/drive/MyDrive/HEALTH/data/hlca_full.h5ad',
]

hlca_path = None
for p in CANDIDATES:
    if os.path.exists(p):
        hlca_path = p
        break

if hlca_path is None:
    raise FileNotFoundError(
        "hlca_full.h5ad not found. Update CANDIDATES list with the correct path."
    )

print(f"Found HLCA at: {hlca_path}")

# ── Load with backed='r' — file stays on disk, only metadata in RAM ────────────
print("Opening (memory-mapped)...")
adata = sc.read_h5ad(hlca_path, backed='r')
print(f"Shape: {adata.n_obs:,} cells × {adata.n_vars:,} genes")

# ── Show disease breakdown ─────────────────────────────────────────────────────
print("\nCells per disease condition:")
print(adata.obs['disease'].value_counts().to_string())

# ── Helper: subset, subsample, save ───────────────────────────────────────────
def export_condition(adata, condition_name, out_path, n_cells=5000):
    print(f"\nExporting '{condition_name}'...")
    mask  = adata.obs['disease'] == condition_name
    count = mask.sum()
    if count == 0:
        print(f"  WARNING: no cells found for '{condition_name}' — skipping.")
        return
    print(f"  {count:,} cells found → subsampling to {min(n_cells, count):,}")
    subset = adata[mask].to_memory()
    if subset.n_obs > n_cells:
        sc.pp.subsample(subset, n_obs=n_cells, random_state=42)
    subset.write_h5ad(out_path)
    size_mb = os.path.getsize(out_path) / 1e6
    print(f"  Saved: {out_path} ({size_mb:.1f} MB)")

# ── Export demo conditions ─────────────────────────────────────────────────────
export_condition(adata, 'COVID-19',           'demo_covid19.h5ad')
export_condition(adata, 'pulmonary fibrosis', 'demo_pulmonary_fibrosis.h5ad')
export_condition(adata, 'COPD',               'demo_copd.h5ad')

print("\nDone. Download the demo_*.h5ad files and place them in your local data/ folder.")

# ── Colab download helper (paste in notebook if needed) ───────────────────────
# from google.colab import files
# files.download('demo_covid19.h5ad')
# files.download('demo_pulmonary_fibrosis.h5ad')
# files.download('demo_copd.h5ad')
