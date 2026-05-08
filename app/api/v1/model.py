"""
Layer 2 — Respiratory Intelligence Engine API

POST /api/v1/model/build     — build the Healthy Respiratory Model from HLCA data
GET  /api/v1/model/status    — model readiness and summary stats
POST /api/v1/analyse         — analyse a gene expression sample
"""

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.core.exceptions import ModelNotBuiltError, DataNotAvailableError, InsufficientGenesError
from app.models.schemas import DeviationReport, GeneExpressionSample, ModelStatus
from app.services import anomaly_detector
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
