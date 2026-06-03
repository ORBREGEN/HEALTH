"""
Respiratory Intelligence Engine — Healthy Reference Model

Builds a statistical model of the healthy human respiratory system from the
HLCA Full dataset (disease == 'normal' cells only).

Eight artefacts are produced and saved to RESPIRATORY_MODEL_DIR:
  meta.json                      build provenance and parameters
  cell_type_composition.json     expected cell type fractions per donor ± std
  gene_stats.json                mean, std, percentiles per gene in healthy tissue
  cell_type_profiles.json        per-cell-type expression of top marker genes
  pathway_baselines.json         healthy baseline activity for 12 biological pathways
  fetal_reference.json           fetal vs adult gene signatures (developmental context)
  spatial_baselines.json         region-specific baselines from Visium tissue sections
  gene_stats_by_cell_type.json   per-CT mean/std for CT-enriched genes (5th analysis dimension)

Usage:
    build_respiratory_model()   # one-time build (~10 min, requires hlca_full.h5ad)
    model = load_model()        # load artefact into memory for serving
    model_is_built()            # check whether the 5 core artefacts exist
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from app.core.config import settings
from app.core.exceptions import DataNotAvailableError

logger = logging.getLogger(__name__)

# ── Build configuration ────────────────────────────────────────────────────────

CELL_TYPE_COLUMN     = "ann_finest_level"
DISEASE_COLUMN       = "disease"
HEALTHY_VALUE        = "normal"
GLOBAL_SAMPLE_SIZE   = 15_000   # cells sampled for global gene stats
CELLS_PER_TYPE       = 500      # cells sampled per cell type
MIN_CELLS_FOR_TYPE   = 100      # cell types with fewer cells are skipped
MIN_EXPRESSING_FRAC  = 0.05     # genes expressed in <5% of donors are excluded
TOP_MARKER_GENES     = 50       # top N genes stored per cell type profile
MIN_CELLS_PER_DONOR  = 50       # donors with fewer healthy cells give noisy pseudo-bulk; skipped
DONOR_CHUNK          = 20_000   # cells per chunk when summing a donor's pseudo-bulk


# ── Model dataclass ────────────────────────────────────────────────────────────

@dataclass
class RespiratoryModel:
    """
    In-memory representation of the Healthy Respiratory Model.

    Loaded from JSON artefacts. The five core artefacts are always present;
    fetal_reference and spatial_baselines are optional (they require additional
    datasets and are loaded if available).
    """
    meta:               dict
    composition:        dict   # cell_type → {mean_fraction, std_fraction, n_donors, compartment}
    gene_stats:         dict   # gene → {mean, std, p5, p25, p75, p95, pct_expressing}
    cell_type_profiles: dict   # cell_type → {n_cells, compartment, marker_gene_stats: {gene: {mean, std}}}
    pathway_baselines:  dict   # pathway_name → {trigger_mean_expr, genes_tracked, ...}
    fetal_reference:    dict = field(default_factory=dict)   # optional
    spatial_baselines:  dict = field(default_factory=dict)   # optional
    ct_gene_stats:      dict = field(default_factory=dict)   # optional — cell_type → {gene: {mean, std, p5, p95}}

    # ── Convenience properties ─────────────────────────────────────────────────

    @property
    def n_cells(self) -> int:
        # notebook saves as 'n_cells'; legacy key was 'n_healthy_cells'
        return self.meta.get("n_cells") or self.meta.get("n_healthy_cells", 0)

    @property
    def n_donors(self) -> int:
        return self.meta.get("n_donors", 0)

    @property
    def n_genes(self) -> int:
        return len(self.gene_stats)

    @property
    def n_pathways(self) -> int:
        return len(self.pathway_baselines)

    @property
    def built_at(self) -> str:
        return self.meta.get("built_at", "")

    @property
    def has_fetal_reference(self) -> bool:
        return bool(self.fetal_reference.get("fetal_enriched"))

    @property
    def has_spatial_baselines(self) -> bool:
        bronchus   = self.spatial_baselines.get("bronchus", {})
        parenchyma = self.spatial_baselines.get("parenchyma", {})
        return "n_spots" in bronchus or "n_spots" in parenchyma

    @property
    def has_ct_gene_stats(self) -> bool:
        return bool(self.ct_gene_stats)


# ── Artefact file names ────────────────────────────────────────────────────────
# These must match the names produced by notebooks/02_build_respiratory_model.ipynb

_CORE_FILES = [
    "meta.json",
    "cell_type_composition.json",
    "gene_stats.json",
    "cell_type_profiles.json",
    "pathway_baselines.json",
]

_OPTIONAL_FILES = [
    "fetal_reference.json",
    "spatial_baselines.json",
]


# ── Build ──────────────────────────────────────────────────────────────────────

def build_respiratory_model() -> dict:
    """
    Build the Healthy Respiratory Model from HLCA Full normal cells.

    Computes the seven artefacts and saves them to settings.RESPIRATORY_MODEL_DIR.
    Requires hlca_full.h5ad at settings.HLCA_FULL_PATH.
    Runtime: ~10 minutes on Colab or a machine with the data on local disk.
    """
    try:
        import anndata as ad
        from scipy.sparse import issparse
    except ImportError:
        raise RuntimeError("anndata and scipy are required: pip install anndata scipy")

    hlca_path = settings.HLCA_FULL_PATH
    if not hlca_path.exists():
        raise DataNotAvailableError(str(hlca_path))

    logger.info("Loading HLCA Full with backed='r' ...")
    adata = ad.read_h5ad(hlca_path, backed="r")
    logger.info("Loaded: %s cells × %s genes", adata.n_obs, adata.n_vars)

    # ── Filter to healthy cells ────────────────────────────────────────────────
    healthy_obs = adata.obs[adata.obs[DISEASE_COLUMN] == HEALTHY_VALUE].copy()
    n_healthy   = len(healthy_obs)
    n_donors    = healthy_obs["donor_id"].nunique() if "donor_id" in healthy_obs.columns else 0
    logger.info("Healthy cells (disease == 'normal'): %s across %s donors", n_healthy, n_donors)

    # Key genes by HGNC symbol (e.g. COL1A1), not the CellxGene Ensembl var_names
    # (ENSG…). Submissions, pathways, and the demo all use symbols. feature_name is
    # per-column and shares column order with adata.X, so this stays aligned.
    if "feature_name" in adata.var.columns:
        gene_names = list(adata.var["feature_name"].astype(str))
    else:
        gene_names = list(adata.var_names)

    # ── Step 1: Cell type composition per donor ────────────────────────────────
    logger.info("Computing cell type composition ...")
    composition = _compute_composition(healthy_obs)

    # ── Step 2: Sample-level gene statistics (per healthy donor) ──────────────
    # Real submissions are sample-level profiles (bulk or pseudo-bulk), not single
    # cells. So the reference must be sample-level: build each healthy donor's
    # pseudo-bulk (mean of adata.X over that donor's cells), then take mean/std
    # ACROSS donors. Donor-to-donor std is the right yardstick for a sample — a
    # disease sample's shift becomes significant, exactly like bulk RNA-seq DE.
    # (Per-cell std, used before, is so large that averaged samples never deviate.)
    logger.info("Building per-donor pseudo-bulk reference ...")
    donor_matrix, n_donors_used = _per_donor_pseudobulk(adata, healthy_obs, len(gene_names))
    logger.info("Per-donor matrix: %s donors x %s genes", n_donors_used, len(gene_names))

    # adata.X is already log1p(CP10K); donor pseudo-bulk stays in that space.
    gene_stats = _compute_gene_stats(donor_matrix, gene_names)
    logger.info("Gene statistics computed (across %s donors): %s genes tracked",
                n_donors_used, len(gene_stats))

    # ── Step 3: Per-cell-type gene profiles + CT-specific gene stats ─────────
    logger.info("Computing per-cell-type gene profiles ...")
    cell_type_profiles, ct_gene_stats = _compute_cell_type_profiles(
        adata, healthy_obs, gene_names, gene_stats
    )

    # ── Step 4: Pathway baselines ─────────────────────────────────────────────
    logger.info("Computing pathway baselines ...")
    pathway_baselines = _compute_pathway_baselines(gene_stats)

    # ── Save artefacts ─────────────────────────────────────────────────────────
    out_dir = settings.RESPIRATORY_MODEL_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "built_at":            datetime.now(timezone.utc).isoformat(),
        "n_cells":             int(n_healthy),
        "n_donors":            int(n_donors),
        "n_genes":             int(len(gene_stats)),
        "n_cell_types":        int(len(cell_type_profiles)),
        "n_pathways":          int(len(pathway_baselines)),
        "source_file":         hlca_path.name,
        "disease_filter":      f"{DISEASE_COLUMN} == {HEALTHY_VALUE}",
        "normalization":       "log1p(CP10K)",
        "gene_stats_basis":    "per-donor pseudo-bulk (mean/std across donors)",
        "n_donors_in_ref":     int(n_donors_used),
        "cell_type_column":    CELL_TYPE_COLUMN,
        "cells_per_type":      CELLS_PER_TYPE,
        "min_cells_for_type":  MIN_CELLS_FOR_TYPE,
        "min_cells_per_donor": MIN_CELLS_PER_DONOR,
        "min_expressing_frac": MIN_EXPRESSING_FRAC,
    }

    n_ct_entries = sum(len(v) for v in ct_gene_stats.values())
    meta["n_ct_gene_entries"] = n_ct_entries

    _save_json(meta,               out_dir / "meta.json")
    _save_json(composition,        out_dir / "cell_type_composition.json")
    _save_json(gene_stats,         out_dir / "gene_stats.json")
    _save_json(cell_type_profiles, out_dir / "cell_type_profiles.json")
    _save_json(pathway_baselines,  out_dir / "pathway_baselines.json")
    _save_json(ct_gene_stats,      out_dir / "gene_stats_by_cell_type.json")

    logger.info("Healthy Respiratory Model saved to %s", out_dir)
    return meta


def _normalize(X_raw: np.ndarray) -> np.ndarray:
    """Normalize raw counts to log1p(CP10K). (Kept for raw-count inputs; the HLCA
    build uses adata.X directly since it is already log1p CP10K.)"""
    totals = X_raw.sum(axis=1, keepdims=True)
    totals = np.where(totals == 0, 1, totals)
    return np.log1p(X_raw / totals * 10_000)


def _per_donor_pseudobulk(adata, healthy_obs, n_genes: int):
    """Build a (n_donors x n_genes) matrix of per-donor pseudo-bulk profiles.

    Each donor's profile is the per-gene mean of adata.X (already log1p CP10K)
    over that donor's healthy cells. Memory-safe: sums each donor's cells in
    sparse chunks, never densifying. Donors with < MIN_CELLS_PER_DONOR cells are
    skipped to avoid noisy profiles.
    """
    from scipy.sparse import issparse as _issparse

    healthy_mask = (adata.obs[DISEASE_COLUMN] == HEALTHY_VALUE).to_numpy()
    donor_col    = adata.obs["donor_id"].to_numpy()

    rows = []
    for donor in sorted(healthy_obs["donor_id"].unique()):
        pos = np.where(healthy_mask & (donor_col == donor))[0]
        if len(pos) < MIN_CELLS_PER_DONOR:
            continue
        acc  = np.zeros(n_genes, dtype=np.float64)
        seen = 0
        for s in range(0, len(pos), DONOR_CHUNK):
            chunk = pos[s:s + DONOR_CHUNK]
            X = adata.X[chunk, :]
            if _issparse(X):
                acc += np.asarray(X.sum(axis=0)).ravel()
            else:
                acc += np.asarray(X, dtype=np.float64).sum(axis=0)
            seen += len(chunk)
        rows.append(acc / seen)

    if not rows:
        raise RuntimeError("No donors met MIN_CELLS_PER_DONOR; cannot build reference.")
    return np.vstack(rows), len(rows)


def _compute_composition(healthy_obs) -> dict:
    """Per-donor cell type fractions → mean ± std across donors (each donor equally weighted)."""
    import pandas as pd

    donor_fractions = (
        healthy_obs
        .groupby("donor_id")[CELL_TYPE_COLUMN]
        .value_counts(normalize=True)
        .unstack(fill_value=0.0)
    )
    mean_f = donor_fractions.mean(axis=0)
    std_f  = donor_fractions.std(axis=0)
    n_w    = (donor_fractions > 0).sum(axis=0)

    return {
        ct: {
            "mean_fraction": float(mean_f[ct]),
            "std_fraction":  float(std_f[ct]),
            "n_donors":      int(n_w[ct]),
            "compartment":   _infer_compartment(ct),
        }
        for ct in mean_f.index
    }


def _compute_gene_stats(X_norm: np.ndarray, gene_names: list[str]) -> dict:
    """Per-gene statistics from a normalized expression matrix."""
    pct_expr  = (X_norm > 0).mean(axis=0)
    keep_mask = pct_expr >= MIN_EXPRESSING_FRAC
    kept      = [g for g, k in zip(gene_names, keep_mask) if k]
    X_kept    = X_norm[:, keep_mask]
    pct_kept  = pct_expr[keep_mask]

    p5, p25, p75, p95 = np.percentile(X_kept, [5, 25, 75, 95], axis=0)
    means = X_kept.mean(axis=0)
    stds  = X_kept.std(axis=0)

    return {
        gene: {
            "mean":           float(means[i]),
            "std":            float(stds[i]),
            "p5":             float(p5[i]),
            "p25":            float(p25[i]),
            "p75":            float(p75[i]),
            "p95":            float(p95[i]),
            "pct_expressing": float(pct_kept[i]),
        }
        for i, gene in enumerate(kept)
    }


CT_GENE_MIN_PCT  = 0.10   # gene must be expressed in ≥10% of this cell type's cells
CT_GENE_MIN_SPAN = 0.5    # ct_mean - global_mean must be ≥ this (enrichment filter)


def _compute_cell_type_profiles(
    adata, healthy_obs, gene_names: list[str], gene_stats: dict
) -> tuple[dict, dict]:
    """
    Sample up to CELLS_PER_TYPE cells per cell type and compute:
    1. profiles — top-N marker genes (used for composition scoring)
    2. ct_gene_stats — per-CT stats for genes meaningfully enriched above global baseline
       (enables CT-aware Z-scoring to detect cell-type-restricted gene suppression)

    Both computed in the same disk-read loop. Returns (profiles, ct_gene_stats).
    """
    from scipy.sparse import issparse as _issparse

    rng = np.random.default_rng(seed=42)
    profiles      = {}
    ct_gene_stats = {}

    for cell_type in sorted(healthy_obs[CELL_TYPE_COLUMN].unique()):
        mask      = (adata.obs[DISEASE_COLUMN] == HEALTHY_VALUE) & (adata.obs[CELL_TYPE_COLUMN] == cell_type)
        positions = np.where(mask)[0]

        if len(positions) < MIN_CELLS_FOR_TYPE:
            continue

        n_sample   = min(CELLS_PER_TYPE, len(positions))
        sample_pos = np.sort(rng.choice(positions, size=n_sample, replace=False))

        X = adata.X[sample_pos, :]
        if _issparse(X):
            X = X.toarray()
        else:
            X = np.asarray(X)
        # adata.X is already log1p(CP10K); use as-is (no re-normalization).
        X_ct = X.astype(np.float32)
        del X

        means    = X_ct.mean(axis=0)
        stds     = X_ct.std(axis=0)
        pct_expr = (X_ct > 0).mean(axis=0)
        p5_ct, p95_ct = np.percentile(X_ct, [5, 95], axis=0)
        del X_ct

        # Artefact 3: top marker genes
        top_idx = np.argsort(means)[::-1][:TOP_MARKER_GENES]
        marker_stats = {
            gene_names[i]: {
                "mean":           float(means[i]),
                "std":            float(stds[i]),
                "pct_expressing": float(pct_expr[i]),
            }
            for i in top_idx if pct_expr[i] >= 0.10
        }
        profiles[cell_type] = {
            "n_cells":           int(len(positions)),
            "n_sampled":         int(n_sample),
            "compartment":       _infer_compartment(cell_type),
            "marker_gene_stats": marker_stats,
        }

        # Artefact 8: CT-specific gene stats for genes enriched above global baseline
        ct_stats = {}
        for i, gene in enumerate(gene_names):
            if gene not in gene_stats:
                continue
            if pct_expr[i] < CT_GENE_MIN_PCT:
                continue
            global_mean = gene_stats[gene]["mean"]
            ct_mean     = float(means[i])
            if ct_mean - global_mean < CT_GENE_MIN_SPAN:
                continue
            ct_stats[gene] = {
                "mean": round(ct_mean, 4),
                "std":  round(max(float(stds[i]), 0.05), 4),
                "p5":   round(float(p5_ct[i]), 4),
                "p95":  round(float(p95_ct[i]), 4),
                "pct_expressing": round(float(pct_expr[i]), 4),
            }
        if ct_stats:
            ct_gene_stats[cell_type] = ct_stats

    return profiles, ct_gene_stats


# Pathway gene sets — mirror the notebook PATHWAY_ATLAS
_PATHWAY_ATLAS: dict[str, dict] = {
    "Interferon response": {
        "category": "immune",
        "triggers": ["MX1", "MX2", "ISG15", "ISG20", "IFIT1", "IFIT2", "IFIT3",
                     "IFITM1", "IFITM3", "OAS1", "OAS2", "OAS3", "OASL",
                     "STAT1", "STAT2", "IRF7", "IRF9"],
        "suppressors": [],
    },
    "NF-kB / cytokine storm": {
        "category": "immune",
        "triggers": ["TNF", "IL6", "IL1B", "CXCL8", "CXCL10",
                     "CCL2", "CCL3", "CCL4", "NFKB1", "NFKBIA", "RELA", "IL18"],
        "suppressors": [],
    },
    "TGF-beta / fibrosis": {
        "category": "remodelling",
        "triggers": ["TGFB1", "TGFB2", "TGFB3", "SMAD2", "SMAD3",
                     "COL1A1", "COL1A2", "COL3A1", "FN1", "ACTA2",
                     "LOX", "LOXL2", "MMP2", "MMP9"],
        "suppressors": [],
    },
    "Epithelial-Mesenchymal Transition (EMT)": {
        "category": "remodelling",
        "triggers": ["VIM", "FN1", "SNAI1", "SNAI2", "ZEB1", "ZEB2", "TWIST1", "CDH2"],
        "suppressors": ["CDH1", "EPCAM", "OCLN", "TJP1"],
    },
    "Surfactant / AT2 function": {
        "category": "alveolar",
        "triggers": ["SFTPC", "SFTPB", "SFTPA1", "SFTPA2", "SFTPD",
                     "ABCA3", "LPCAT1", "FASN", "SLC34A2"],
        "suppressors": [],
    },
    "Hypoxia / HIF response": {
        "category": "metabolic",
        "triggers": ["HIF1A", "EPAS1", "VEGFA", "LDHA", "SLC2A1",
                     "BNIP3", "BNIP3L", "CA9", "PDK1", "PGK1"],
        "suppressors": [],
    },
    "Cell proliferation / oncogenic": {
        "category": "oncogenic",
        "triggers": ["MKI67", "TOP2A", "PCNA", "CDK1", "CCNB1", "CCND1", "CCNE1",
                     "E2F1", "MYBL2", "BUB1", "PLK1", "KRAS", "MYC"],
        "suppressors": ["RB1", "TP53", "CDKN1A", "CDKN2A"],
    },
    "Mucociliary clearance": {
        "category": "airway",
        "triggers": ["FOXJ1", "DNAI1", "DNAI2", "CCNO",
                     "MUC5AC", "MUC5B", "MUC1", "SCGB1A1"],
        "suppressors": [],
    },
    "Complement activation": {
        "category": "immune",
        "triggers": ["C1QA", "C1QB", "C1QC", "C3", "C4A", "CFB", "CFD", "SERPING1"],
        "suppressors": [],
    },
    "Vascular injury": {
        "category": "vascular",
        "triggers": ["ICAM1", "VCAM1", "SELE", "VWF", "ANGPT2", "EDN1", "F3", "PTGS2"],
        "suppressors": ["PECAM1", "CDH5", "KDR"],
    },
    "Myeloid activation": {
        "category": "immune",
        "triggers": ["CD14", "CD68", "MARCO", "MRC1", "S100A8", "S100A9",
                     "S100A12", "LYZ", "MPO", "CTSS", "CTSB"],
        "suppressors": [],
    },
    "T cell exhaustion": {
        "category": "immune",
        "triggers": ["PDCD1", "LAG3", "HAVCR2", "TIGIT", "CTLA4",
                     "TOX", "TOX2", "BATF", "NR4A1", "ENTPD1"],
        "suppressors": ["TCF7", "IL7R", "SELL", "CCR7"],
    },
}


def _compute_pathway_baselines(gene_stats: dict) -> dict:
    """Compute healthy baseline activity for each pathway from gene_stats."""
    baselines = {}
    for name, pw in _PATHWAY_ATLAS.items():
        tracked_t = [g for g in pw["triggers"]    if g in gene_stats]
        tracked_s = [g for g in pw["suppressors"] if g in gene_stats]

        if not tracked_t:
            continue

        genes_tracked = {
            **{g: {"mean": gene_stats[g]["mean"], "std": gene_stats[g]["std"], "role": "trigger"}
               for g in tracked_t},
            **{g: {"mean": gene_stats[g]["mean"], "std": gene_stats[g]["std"], "role": "suppressor"}
               for g in tracked_s},
        }

        baselines[name] = {
            "category":             pw["category"],
            "n_trigger_genes":      len(tracked_t),
            "n_suppressor_genes":   len(tracked_s),
            "trigger_mean_expr":    float(np.mean([gene_stats[g]["mean"] for g in tracked_t])),
            "trigger_std_expr":     float(np.mean([gene_stats[g]["std"]  for g in tracked_t])),
            "suppressor_mean_expr": float(np.mean([gene_stats[g]["mean"] for g in tracked_s])) if tracked_s else None,
            "genes_tracked":        genes_tracked,
        }
    return baselines


def _infer_compartment(cell_type: str) -> str:
    ct = cell_type.lower()
    if any(k in ct for k in ["at1", "at2", "type 1", "type 2", "alveolar type", "pneumocyte"]):
        return "alveolar"
    if any(k in ct for k in ["alveolar macrophage"]):
        return "alveolar"
    if any(k in ct for k in ["t cell", "b cell", "nk ", "dendritic", "mast", "plasma",
                               "monocyte", "macrophage", "neutrophil", "eosinophil"]):
        return "immune"
    if any(k in ct for k in ["basal", "ciliated", "multiciliated", "secretory", "goblet",
                               "airway", "tracheal", "bronchial", "club", "serous"]):
        return "airway"
    if any(k in ct for k in ["fibroblast", "smooth muscle", "pericyte", "mesothelial"]):
        return "stromal"
    if any(k in ct for k in ["endothelial", "capillary", "venous", "arterial", "lymphatic"]):
        return "vascular"
    if any(k in ct for k in ["tuft", "ionocyte", "neuroendocrine"]):
        return "rare_specialized"
    return "unknown"


def _save_json(data: dict, path: Path) -> None:
    path.write_text(json.dumps(data, indent=2, allow_nan=False))
    logger.debug("Saved %s (%.0f KB)", path.name, path.stat().st_size / 1024)


# ── Load / Status ──────────────────────────────────────────────────────────────

def model_is_built() -> bool:
    """True when the five core artefacts exist in RESPIRATORY_MODEL_DIR."""
    d = settings.RESPIRATORY_MODEL_DIR
    return all((d / f).exists() for f in _CORE_FILES)


def load_model() -> "RespiratoryModel | None":
    """
    Load all artefacts from RESPIRATORY_MODEL_DIR into a RespiratoryModel.

    The five core artefacts must be present. The fetal_reference and
    spatial_baselines artefacts are loaded if available (produced by the
    full Colab notebook run) and left as empty dicts otherwise.
    """
    if not model_is_built():
        return None
    try:
        d = settings.RESPIRATORY_MODEL_DIR

        def _load(name: str) -> dict:
            return json.loads((d / name).read_text())

        def _load_optional(name: str) -> dict:
            p = d / name
            return json.loads(p.read_text()) if p.exists() else {}

        return RespiratoryModel(
            meta               = _load("meta.json"),
            composition        = _load("cell_type_composition.json"),
            gene_stats         = _load("gene_stats.json"),
            cell_type_profiles = _load("cell_type_profiles.json"),
            pathway_baselines  = _load("pathway_baselines.json"),
            fetal_reference    = _load_optional("fetal_reference.json"),
            spatial_baselines  = _load_optional("spatial_baselines.json"),
            ct_gene_stats      = _load_optional("gene_stats_by_cell_type.json"),
        )
    except Exception:
        logger.exception("Failed to load Healthy Respiratory Model")
        return None
