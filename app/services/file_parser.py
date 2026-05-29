"""
File parser — converts researcher-uploaded expression files into
the gene symbol → log1p CP10K dict the analysis engine expects.

Supported formats:
  .h5ad   — AnnData (Scanpy / Seurat export). Multi-cell files are
             per-cell normalised then pseudo-bulk averaged.
             Parsed from disk with backed='r' (memory-mapped, chunk-processed).
  .zip    — CellRanger MEX output (matrix.mtx.gz + barcodes.tsv.gz +
             features.tsv.gz or genes.tsv.gz). Zip the output folder and upload.
  .csv / .tsv / .txt — two-column (gene, value) or matrix with gene
             names in the first column.
"""

import gzip
import io
import logging
import re
import zipfile
from typing import Union

import numpy as np

logger = logging.getLogger(__name__)

_ENSEMBL_RE = re.compile(r'^ENSG\d{11}$', re.IGNORECASE)
MAX_GENES = 60_000
_H5AD_CHUNK = 5_000  # cells per chunk; sparse ops keep peak RAM ~50-300 MB regardless of chunk size

# ── Auto QC thresholds ─────────────────────────────────────────────────────────
_QC_MIN_GENES = 200       # below: empty droplet or severely damaged cell
_QC_MAX_GENES = 8_000     # above: likely doublet (two cells captured together)
_QC_MAX_MT_PCT = 25.0     # above: damaged/dying cell (cytoplasmic RNA leaked, MT remains)


def parse_file(
    content: bytes,
    filename: str,
) -> tuple[dict[str, float], list[str]]:
    """Parse CSV/TSV/TXT expression files. Use parse_file_from_path for .h5ad and .zip."""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    if ext in ('h5ad', 'zip'):
        raise ValueError(
            f".{ext} files must be parsed via parse_file_from_path (path-based). "
            "Call parse_file only for CSV/TSV uploads."
        )
    elif ext in ('csv', 'tsv', 'txt'):
        sep = '\t' if ext == 'tsv' else None
        return _parse_delimited(content.decode('utf-8', errors='replace'), sep)
    else:
        raise ValueError(
            f"Unsupported file format '.{ext}'. "
            "Upload a .h5ad, .zip (CellRanger MEX), .csv, or .tsv file."
        )


def parse_file_from_path(
    path: str,
    filename: str,
) -> tuple[dict[str, float], list[str]]:
    """Parse an uploaded expression file from a temp-file path into (gene_expression, notes)."""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    if ext == 'h5ad':
        return _parse_h5ad_from_path(path)
    elif ext == 'zip':
        return _parse_10x_zip(path)
    elif ext in ('csv', 'tsv', 'txt'):
        with open(path, 'rb') as f:
            content = f.read()
        sep = '\t' if ext == 'tsv' else None
        return _parse_delimited(content.decode('utf-8', errors='replace'), sep)
    else:
        raise ValueError(
            f"Unsupported file format '.{ext}'. "
            "Upload a .h5ad, .zip (CellRanger MEX), .csv, or .tsv file."
        )


# ── h5ad ───────────────────────────────────────────────────────────────────────

def _parse_h5ad_from_path(path: str) -> tuple[dict[str, float], list[str]]:
    """
    Parse an h5ad file with backed='r', automatic QC, and sparse-aware chunked pseudo-bulk.

    Single pass over the file: each chunk is read once, QC-filtered, normalised,
    and accumulated. Dense (cells × genes) matrix is never materialised.

    QC removes:
      - Empty droplets   : cells with < _QC_MIN_GENES genes detected
      - Damaged cells    : cells with > _QC_MAX_MT_PCT% mitochondrial reads (MT- genes)
      - Doublets         : cells with > _QC_MAX_GENES genes detected
    """
    try:
        import anndata as ad
        from scipy.sparse import issparse, diags as sp_diags
    except ImportError:
        raise RuntimeError("anndata and scipy are required. Run: pip install anndata scipy")

    notes: list[str] = []
    adata = None

    try:
        try:
            adata = ad.read_h5ad(path, backed='r')
        except Exception as exc:
            raise ValueError(f"Could not read .h5ad file: {exc}") from exc

        n_cells, n_genes = adata.shape
        logger.info("h5ad opened (backed): %d cells × %d genes", n_cells, n_genes)

        gene_names = [str(g).strip() for g in adata.var_names]

        # ── Prefer raw counts layer for QC + normalisation ────────────────
        use_layer = None
        for candidate in ('counts', 'raw_counts', 'spliced'):
            if candidate in adata.layers:
                use_layer = candidate
                break

        # ── Mitochondrial gene indices (for damage detection) ─────────────
        mt_idx = np.array([i for i, g in enumerate(gene_names) if g.upper().startswith('MT-')])
        has_mt = mt_idx.size > 0

        # ── Scale detection from first chunk (non-zero values only) ───────
        sample = adata.layers[use_layer][:min(200, n_cells)] if use_layer else adata.X[:min(200, n_cells)]
        positive_vals = sample.data[sample.data > 0] if issparse(sample) else np.asarray(sample)[np.asarray(sample) > 0]
        p99 = float(np.percentile(positive_vals, 99)) if positive_vals.size else 0.0
        can_qc_mt = p99 > 10  # MT% is only meaningful for raw/CP10K data, not log1p

        if p99 > 1000:
            scale = 'raw'
            notes.append(
                (f"Raw counts detected in '{use_layer}' layer — " if use_layer else "Raw counts detected — ")
                + "normalised per cell (÷ total × 10,000 → log1p CP10K) before analysis."
            )
        elif p99 > 10:
            scale = 'cp10k'
            notes.append("CP10K values detected — log1p transform applied.")
        else:
            scale = 'lognorm'

        # ── Single-pass: QC + filter + normalise + accumulate ─────────────
        mean_expr = np.zeros(n_genes, dtype=np.float64)
        n_kept = 0
        n_low_genes = 0
        n_high_genes = 0
        n_high_mt = 0

        for start in range(0, n_cells, _H5AD_CHUNK):
            end = min(start + _H5AD_CHUNK, n_cells)
            chunk = adata.layers[use_layer][start:end] if use_layer else adata.X[start:end]

            if issparse(chunk):
                chunk = chunk.tocsr().astype(np.float64)

                # Per-cell QC stats (sparse-aware, no dense matrix)
                n_genes_cell = np.diff(chunk.indptr)
                totals = np.asarray(chunk.sum(axis=1)).flatten()

                low  = n_genes_cell < _QC_MIN_GENES
                high = n_genes_cell > _QC_MAX_GENES
                if has_mt and can_qc_mt:
                    mt_sum = np.asarray(chunk[:, mt_idx].sum(axis=1)).flatten()
                    mt_pct = np.where(totals > 0, mt_sum / totals * 100, 0.0)
                    bad_mt = mt_pct > _QC_MAX_MT_PCT
                else:
                    bad_mt = np.zeros(end - start, dtype=bool)

                keep = ~(low | high | bad_mt)
                n_low_genes  += int(low.sum())
                n_high_genes += int(high.sum())
                n_high_mt    += int(bad_mt.sum())

                if not keep.any():
                    continue
                chunk = chunk[keep]
                n_kept += chunk.shape[0]

                # Normalise (sparse-aware)
                if scale == 'raw':
                    row_totals = np.asarray(chunk.sum(axis=1)).flatten()
                    row_totals[row_totals == 0] = 1.0
                    chunk = sp_diags(1e4 / row_totals).dot(chunk)
                    chunk.data = np.log1p(chunk.data)
                elif scale == 'cp10k':
                    chunk.data = np.log1p(chunk.data)

                mean_expr += np.asarray(chunk.sum(axis=0)).flatten()

            else:
                # Dense fallback
                chunk = np.asarray(chunk, dtype=np.float64)
                n_genes_cell = (chunk > 0).sum(axis=1)
                totals = chunk.sum(axis=1)

                low  = n_genes_cell < _QC_MIN_GENES
                high = n_genes_cell > _QC_MAX_GENES
                if has_mt and can_qc_mt:
                    mt_pct = np.where(totals > 0, chunk[:, mt_idx].sum(axis=1) / totals * 100, 0.0)
                    bad_mt = mt_pct > _QC_MAX_MT_PCT
                else:
                    bad_mt = np.zeros(end - start, dtype=bool)

                keep = ~(low | high | bad_mt)
                n_low_genes  += int(low.sum())
                n_high_genes += int(high.sum())
                n_high_mt    += int(bad_mt.sum())

                if not keep.any():
                    continue
                chunk = chunk[keep]
                n_kept += chunk.shape[0]

                if scale == 'raw':
                    row_totals = chunk.sum(axis=1, keepdims=True)
                    row_totals[row_totals == 0] = 1.0
                    chunk = np.log1p(chunk / row_totals * 1e4)
                elif scale == 'cp10k':
                    chunk = np.log1p(chunk)

                mean_expr += chunk.sum(axis=0)

        gene_names_out = gene_names  # captured before finally block closes file

    finally:
        if adata is not None and adata.isbacked:
            adata.file.close()

    # ── QC report ─────────────────────────────────────────────────────────
    if n_kept == 0:
        raise ValueError(
            f"All {n_cells:,} cells failed QC "
            f"({n_low_genes} empty/low-quality, {n_high_mt} damaged, {n_high_genes} doublets). "
            "The sample may be severely degraded."
        )
    if n_kept < 10:
        raise ValueError(
            f"Only {n_kept} cells survived QC from {n_cells:,} total. "
            "Too few cells for reliable pseudo-bulk analysis."
        )

    n_removed = n_cells - n_kept
    if n_removed > 0:
        mt_clause = (
            f", {n_high_mt:,} damaged [>{_QC_MAX_MT_PCT:.0f}% mitochondrial]"
            if has_mt and can_qc_mt else ""
        )
        notes.insert(0,
            f"Auto QC: {n_kept:,} of {n_cells:,} cells retained — "
            f"{n_low_genes:,} empty/low-quality [<{_QC_MIN_GENES} genes]"
            f"{mt_clause}, "
            f"{n_high_genes:,} doublets [>{_QC_MAX_GENES:,} genes] removed."
        )

    mean_expr /= n_kept

    if n_kept > 1:
        notes.append(
            f"{n_kept:,} cells retained after QC — expression averaged (pseudo-bulk) before analysis."
        )

    # ── Ensembl ID check ──────────────────────────────────────────────────
    n_ensembl = sum(1 for g in gene_names_out[:500] if _ENSEMBL_RE.match(g))
    if n_ensembl > 100:
        raise ValueError(
            f"{n_ensembl} gene identifiers appear to be Ensembl IDs "
            "(e.g. ENSG00000…). This model uses HGNC gene symbols (e.g. COL1A1, SFTPC). "
            "Convert using sc.queries.biomart_annotations() in Scanpy or biomaRt in R, "
            "update adata.var_names, then re-export your .h5ad."
        )

    gene_expr: dict[str, float] = {}
    for gene, val in zip(gene_names_out, mean_expr.tolist()):
        if val > 0 and gene:
            gene_expr[gene.upper()] = round(float(val), 6)

    if len(gene_expr) < 10:
        raise ValueError(
            f"Only {len(gene_expr)} genes with non-zero expression found after parsing. "
            "Minimum 10 required. Ensure adata.X contains expression values, not zeros."
        )

    logger.info("h5ad parsed: %d cells kept, %d genes expressed", n_kept, len(gene_expr))
    return gene_expr, notes


# ── 10x MEX zip (CellRanger output) ───────────────────────────────────────────

def _parse_10x_zip(path: str) -> tuple[dict[str, float], list[str]]:
    """
    Parse a zip of CellRanger MEX output.

    Expects inside the zip (any directory depth):
      matrix.mtx[.gz]           — sparse count matrix (features × barcodes)
      barcodes.tsv[.gz]         — cell barcodes
      features.tsv[.gz]         — gene_id, gene_name[, feature_type]  (v3)
        or genes.tsv[.gz]       — gene_id, gene_name                   (v2)

    Applies the same scale detection + sparse chunked pseudo-bulk as h5ad.
    """
    try:
        from scipy.io import mmread
        from scipy.sparse import issparse, diags as sp_diags
    except ImportError:
        raise RuntimeError("scipy is required. Run: pip install scipy")

    notes: list[str] = []

    # ── Extract required files from the zip ───────────────────────────────────
    def _read_entry(zf: zipfile.ZipFile, *names: str) -> bytes | None:
        """Return the first matching entry (plain or .gz) regardless of path depth."""
        entries = zf.namelist()
        for name in names:
            for entry in entries:
                base = entry.split('/')[-1]
                if base == name or base == name + '.gz':
                    raw = zf.read(entry)
                    return gzip.decompress(raw) if base.endswith('.gz') else raw
        return None

    try:
        with zipfile.ZipFile(path, 'r') as zf:
            matrix_bytes   = _read_entry(zf, 'matrix.mtx')
            barcode_bytes  = _read_entry(zf, 'barcodes.tsv')
            feature_bytes  = _read_entry(zf, 'features.tsv', 'genes.tsv')
    except zipfile.BadZipFile as exc:
        raise ValueError(f"Could not open zip file: {exc}") from exc

    if matrix_bytes is None:
        raise ValueError(
            "matrix.mtx or matrix.mtx.gz not found in the zip. "
            "Zip the CellRanger output folder (filtered_feature_bc_matrix/) directly."
        )
    if barcode_bytes is None:
        raise ValueError("barcodes.tsv not found in the zip.")
    if feature_bytes is None:
        raise ValueError("features.tsv (or genes.tsv) not found in the zip.")

    # ── Parse features ─────────────────────────────────────────────────────────
    # v3: gene_id\tgene_name\tfeature_type  — use gene_name (col 1)
    # v2: gene_id\tgene_name               — use gene_name (col 1)
    gene_names: list[str] = []
    feature_mask: list[bool] = []   # True = Gene Expression, False = skip (ADT, CRISPR…)
    for line in feature_bytes.decode('utf-8').splitlines():
        parts = line.strip().split('\t')
        if not parts or not parts[0]:
            continue
        name = parts[1].strip() if len(parts) >= 2 else parts[0].strip()
        ftype = parts[2].strip() if len(parts) >= 3 else 'Gene Expression'
        gene_names.append(name)
        feature_mask.append(ftype == 'Gene Expression')

    # ── Load sparse matrix (features × barcodes) ──────────────────────────────
    try:
        mat = mmread(io.BytesIO(matrix_bytes)).tocsr()
    except Exception as exc:
        raise ValueError(f"Could not read matrix.mtx: {exc}") from exc

    if mat.shape[0] != len(gene_names):
        raise ValueError(
            f"Matrix has {mat.shape[0]} features but features file has {len(gene_names)} rows."
        )

    # Filter to Gene Expression features only (removes ADT/CRISPR rows for CITE-seq)
    n_total = len(gene_names)
    n_gex = sum(feature_mask)
    if n_gex < n_total:
        idx = np.array([i for i, keep in enumerate(feature_mask) if keep])
        mat = mat[idx, :]
        gene_names = [g for g, keep in zip(gene_names, feature_mask) if keep]
        notes.append(
            f"Multi-modal data detected: kept {n_gex:,} Gene Expression features "
            f"(removed {n_total - n_gex:,} non-GEX rows such as antibody/CRISPR)."
        )

    # Transpose: (features × barcodes) → (cells × genes)
    mat = mat.T.tocsr().astype(np.float64)
    n_cells, n_genes = mat.shape
    logger.info("10x MEX loaded: %d cells × %d genes", n_cells, n_genes)

    # ── Auto QC (matrix is in memory — compute stats in one shot) ─────────────
    mt_idx = np.array([i for i, g in enumerate(gene_names) if g.upper().startswith('MT-')])
    has_mt = mt_idx.size > 0

    n_genes_per_cell = np.diff(mat.indptr)
    totals_all       = np.asarray(mat.sum(axis=1)).flatten()

    low_mask  = n_genes_per_cell < _QC_MIN_GENES
    high_mask = n_genes_per_cell > _QC_MAX_GENES

    if has_mt:
        mt_sum  = np.asarray(mat[:, mt_idx].sum(axis=1)).flatten()
        mt_pct  = np.where(totals_all > 0, mt_sum / totals_all * 100, 0.0)
        bad_mt  = mt_pct > _QC_MAX_MT_PCT
    else:
        bad_mt = np.zeros(n_cells, dtype=bool)

    keep      = ~(low_mask | high_mask | bad_mt)
    n_kept    = int(keep.sum())
    n_low     = int(low_mask.sum())
    n_high    = int(high_mask.sum())
    n_high_mt = int(bad_mt.sum())
    n_removed = n_cells - n_kept

    if n_kept == 0:
        raise ValueError(
            f"All {n_cells:,} cells failed QC "
            f"({n_low} empty/low-quality, {n_high_mt} damaged, {n_high} doublets). "
            "The sample may be severely degraded."
        )
    if n_kept < 10:
        raise ValueError(
            f"Only {n_kept} cells survived QC from {n_cells:,} total. "
            "Too few cells for reliable pseudo-bulk analysis."
        )

    if n_removed > 0:
        mt_clause = f", {n_high_mt:,} damaged [>{_QC_MAX_MT_PCT:.0f}% mitochondrial]" if has_mt else ""
        notes.insert(0,
            f"Auto QC: {n_kept:,} of {n_cells:,} cells retained — "
            f"{n_low:,} empty/low-quality [<{_QC_MIN_GENES} genes]"
            f"{mt_clause}, "
            f"{n_high:,} doublets [>{_QC_MAX_GENES:,} genes] removed."
        )

    mat = mat[keep]

    # ── Scale detection (from surviving cells) ─────────────────────────────────
    sample = mat[:min(200, n_kept)]
    p99 = float(np.percentile(sample.data[sample.data > 0], 99)) if sample.data.size else 0.0

    if p99 > 1000:
        scale = 'raw'
        notes.append("Raw counts detected — normalised per cell (÷ total × 10,000 → log1p CP10K) before analysis.")
    elif p99 > 10:
        scale = 'cp10k'
        notes.append("CP10K values detected — log1p transform applied.")
    else:
        scale = 'lognorm'

    # ── Chunked sparse pseudo-bulk mean ───────────────────────────────────────
    mean_expr = np.zeros(n_genes, dtype=np.float64)

    for start in range(0, n_kept, _H5AD_CHUNK):
        end = min(start + _H5AD_CHUNK, n_kept)
        chunk = mat[start:end].tocsr().astype(np.float64)

        if scale == 'raw':
            totals = np.asarray(chunk.sum(axis=1)).flatten()
            totals[totals == 0] = 1.0
            chunk = sp_diags(1e4 / totals).dot(chunk)
            chunk.data = np.log1p(chunk.data)
        elif scale == 'cp10k':
            chunk.data = np.log1p(chunk.data)

        mean_expr += np.asarray(chunk.sum(axis=0)).flatten()

    mean_expr /= n_kept

    if n_kept > 1:
        notes.append(
            f"{n_kept:,} cells retained after QC — expression averaged (pseudo-bulk) before analysis."
        )

    # ── Ensembl ID check ──────────────────────────────────────────────────────
    n_ensembl = sum(1 for g in gene_names[:500] if _ENSEMBL_RE.match(g))
    if n_ensembl > 100:
        raise ValueError(
            f"{n_ensembl} gene names are Ensembl IDs (e.g. ENSG00000…). "
            "This model uses HGNC gene symbols. "
            "Ensure features.tsv column 2 contains gene symbols, not Ensembl IDs."
        )

    gene_expr: dict[str, float] = {}
    for gene, val in zip(gene_names, mean_expr.tolist()):
        if val > 0 and gene:
            gene_expr[gene.upper()] = round(float(val), 6)

    if len(gene_expr) < 10:
        raise ValueError(
            f"Only {len(gene_expr)} genes with non-zero expression found. Minimum 10 required."
        )

    logger.info("10x MEX parsed: %d genes with non-zero expression", len(gene_expr))
    return gene_expr, notes


# ── Delimited text (CSV / TSV) ─────────────────────────────────────────────────

def _parse_delimited(
    text: str,
    sep: Union[str, None] = None,
) -> tuple[dict[str, float], list[str]]:
    notes: list[str] = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        raise ValueError("File is empty.")

    if sep is None:
        first = lines[0]
        sep = '\t' if '\t' in first else ',' if ',' in first else ';' if ';' in first else ' '

    rows = [[c.strip().strip('"\'') for c in l.split(sep)] for l in lines]

    # Detect header: first row non-numeric in position [1]
    has_header = len(rows) >= 2 and not _is_float(rows[0][1] if len(rows[0]) > 1 else '')
    data_rows = rows[1:] if has_header else rows

    if not data_rows:
        raise ValueError("No data rows found.")

    # Detect Ensembl IDs in first column
    n_ensembl = sum(1 for r in data_rows[:200] if r and _ENSEMBL_RE.match(r[0]))
    if n_ensembl > 50:
        notes.append(
            f"Ensembl IDs detected ({n_ensembl} found, e.g. {data_rows[0][0]}). "
            "The model uses HGNC gene symbols (COL1A1, SFTPC). "
            "Convert with biomaRt (R) or mygene.info (Python) for best coverage."
        )

    gene_expr: dict[str, float] = {}
    for row in data_rows:
        if len(row) < 2:
            continue
        gene = row[0].upper().strip()
        if not gene:
            continue
        try:
            val = float(row[1])
        except ValueError:
            continue
        if val > 0:
            gene_expr[gene] = val

    if len(gene_expr) < 10:
        raise ValueError(
            f"Only {len(gene_expr)} valid gene rows found. "
            "Expected: gene symbol in column 1, expression value in column 2. "
            "Minimum 10 genes required."
        )

    return gene_expr, notes


def _is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False
