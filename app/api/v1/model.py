"""
Layer 2 — Respiratory Intelligence Engine API

POST /api/v1/model/build     — build the Healthy Respiratory Model from HLCA data
GET  /api/v1/model/status    — model readiness and summary stats
POST /api/v1/analyse         — analyse a gene expression sample
"""

import logging
import os
import tempfile

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile, status

from app.core.exceptions import ModelNotBuiltError, DataNotAvailableError, InsufficientGenesError
from app.models.schemas import DeviationReport, GeneExpressionSample, ModelStatus
from app.services import anomaly_detector
from app.services.file_parser import parse_file_from_path
from app.services.respiratory_model import (
    build_respiratory_model,
    load_model,
    model_is_built,
)

router = APIRouter(tags=["Respiratory Intelligence Engine"])
logger = logging.getLogger(__name__)


def _build_and_reload() -> None:
    try:
        build_respiratory_model()
        reloaded = anomaly_detector.reload_model()
        if reloaded:
            logger.info("Healthy Respiratory Model built and loaded.")
        else:
            logger.error("Model built but failed to reload.")
    except DataNotAvailableError as e:
        logger.error("Build failed — data not available: %s", e.path)
    except Exception:
        logger.exception("Healthy Respiratory Model build failed.")


@router.post(
    "/model/build",
    summary="Build the Healthy Respiratory Model",
    description="""
Builds the Healthy Respiratory Model from HLCA Full (`disease == 'normal'` cells).

Computes three artefacts saved to `models/respiratory_model/`:
- Cell type composition: expected fractions per donor ± std
- Global gene statistics: mean, std, percentiles for every expressed gene
- Per-cell-type gene profiles: expression statistics per cell type

Runs in the background (~10 minutes). Requires `data/hlca_full.h5ad` on disk.
Poll `GET /api/v1/model/status` to check when ready.
""",
)
def build_model(background_tasks: BackgroundTasks) -> dict:
    background_tasks.add_task(_build_and_reload)
    return {
        "status":  "building",
        "message": "Model build started in background. Poll GET /api/v1/model/status to track progress.",
    }


@router.get("/model/status", response_model=ModelStatus, summary="Healthy Respiratory Model status")
def model_status() -> ModelStatus:
    if not model_is_built():
        return ModelStatus(
            is_ready = False,
            message  = "Model not built. Call POST /api/v1/model/build.",
        )
    model = load_model()
    if model is None:
        return ModelStatus(is_ready=False, message="Model files exist but could not be loaded — try rebuilding.")
    return ModelStatus(
        is_ready              = True,
        built_at              = model.built_at,
        n_healthy_cells       = model.n_cells,
        n_donors              = model.n_donors,
        n_genes_tracked       = model.n_genes,
        n_cell_types          = len(model.cell_type_profiles),
        n_pathways            = model.n_pathways,
        has_fetal_reference   = model.has_fetal_reference,
        has_spatial_baselines = model.has_spatial_baselines,
        message               = (
            f"Ready. Built from {model.n_cells:,} healthy cells across {model.n_donors} donors. "
            f"{model.n_genes:,} genes, {model.n_pathways} pathway baselines."
            + (" Fetal reference loaded." if model.has_fetal_reference else "")
            + (" Spatial baselines loaded." if model.has_spatial_baselines else "")
        ),
    )


@router.post(
    "/analyse",
    response_model=DeviationReport,
    summary="Analyse a gene expression sample against the Healthy Respiratory Model",
    description="""
Compares a gene expression profile to the Healthy Respiratory Model and returns
a structured biological deviation report.

**Input**: gene symbol → log1p(CP10K) expression value. Minimum 50 genes.

**Output**: three biological dimensions:
- Cell type deviations (Z-scores vs. healthy donor distribution)
- Gene deviations (genes outside ±2σ of healthy range)
- Pathway deviations (active or suppressed biological processes)

The report does not name a disease. It describes the biology of the sample
and how it deviates from healthy. Clinical interpretation belongs to the expert.
""",
)
def analyse_sample(sample: GeneExpressionSample) -> DeviationReport:
    if not anomaly_detector.model_ready():
        raise HTTPException(
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail      = "Healthy Respiratory Model not ready. Call POST /api/v1/model/build first.",
        )
    try:
        return anomaly_detector.analyse(sample.sample_id, sample.gene_expression)
    except InsufficientGenesError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except ModelNotBuiltError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.exception("Analysis failed for sample %s", sample.sample_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


_MAX_UPLOAD_BYTES = 100 * 1024 * 1024 * 1024  # 100 GB
_STREAM_CHUNK = 8 * 1024 * 1024  # 8 MB read chunks during upload


@router.post(
    "/analyse/upload",
    response_model=DeviationReport,
    summary="Analyse a gene expression file (.h5ad, .csv, .tsv)",
    description="""
Upload a gene expression file for analysis against the Healthy Respiratory Model.

**Accepted formats:**
- `.h5ad` — AnnData (Scanpy / Seurat). Multi-cell files are pseudo-bulk averaged.
  Parsed with memory-mapped access and chunked cell processing — RAM usage is
  bounded regardless of cell count.
- `.zip` — CellRanger MEX output folder (matrix.mtx.gz + barcodes.tsv.gz +
  features.tsv.gz). Zip the `filtered_feature_bc_matrix/` folder and upload.
- `.csv` / `.tsv` / `.txt` — two columns: gene symbol, expression value.

**Normalisation:**
Values should be log1p CP10K (Scanpy: `sc.pp.normalize_total` + `sc.pp.log1p`).
Raw counts and plain CP10K are auto-detected and normalised with a warning in the report.

**File size limit:** 100 GB.
""",
)
async def analyse_upload(
    file: UploadFile = File(..., description="Gene expression file (.h5ad, .csv, .tsv)"),
    sample_id: str = Form(default="", description="Optional sample identifier"),
) -> DeviationReport:
    if not anomaly_detector.model_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Healthy Respiratory Model not ready. Call POST /api/v1/model/build first.",
        )

    filename = file.filename or "upload"
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    # ── Stream upload to temp file (bounded RAM regardless of file size) ────
    suffix = f'.{ext}' if ext else ''
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp_path = tmp.name
            total = 0
            while True:
                chunk = await file.read(_STREAM_CHUNK)
                if not chunk:
                    break
                total += len(chunk)
                if total > _MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File exceeds the 100 GB limit.",
                    )
                tmp.write(chunk)

        logger.info("Upload streamed to disk: %s (%.1f MB)", filename, total / 1e6)

        # ── Parse ───────────────────────────────────────────────────────────
        try:
            gene_expression, parse_notes = parse_file_from_path(tmp_path, filename)
        except (ValueError, RuntimeError) as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
        except Exception as e:
            logger.exception("File parsing failed for %s", filename)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not parse file: {e}",
            )

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    # ── Analyse ─────────────────────────────────────────────────────────────
    sid = sample_id.strip() or filename.rsplit('.', 1)[0] or "uploaded_sample"
    try:
        report = anomaly_detector.analyse(sid, gene_expression)
    except InsufficientGenesError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except ModelNotBuiltError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.exception("Analysis failed for uploaded file %s", filename)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    if parse_notes:
        report.data_quality_warnings = parse_notes + report.data_quality_warnings

    logger.info("Upload analysis complete: %s (%d genes)", sid, len(gene_expression))
    return report
