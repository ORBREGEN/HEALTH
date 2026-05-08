"""
Layer 2 — Biological Reasoning Engine API

POST /api/v1/interpret   — interpret a DeviationReport using chain-of-thought reasoning
"""

import logging

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.models.schemas import BiologicalInterpretation, DeviationReport
from app.services import reasoning_engine

router = APIRouter(tags=["Biological Reasoning Engine"])
logger = logging.getLogger(__name__)


@router.post(
    "/interpret",
    response_model=BiologicalInterpretation,
    summary="Interpret a DeviationReport using biological chain-of-thought reasoning",
    description="""
Accepts a `DeviationReport` (the output of `POST /api/v1/analyse`) and returns a
`BiologicalInterpretation` produced by the v6 chain-of-thought reasoning engine.

**Typical call sequence:**
1. `POST /api/v1/analyse` — analyse a gene expression sample → `DeviationReport`
2. `POST /api/v1/interpret` — interpret the report → `BiologicalInterpretation`

**The reasoning pipeline (v6):**

| Step | What it does |
|------|-------------|
| Triage | Rank and cap findings by severity (top 8 genes, 5 cell types, 6 pathways) |
| Cluster | Map findings to 8 biological processes using the HLCA process atlas |
| Enrich | Attach curated functional annotations to each finding |
| Prompt | Format evidence as a structured user message |
| Reason | Call `claude-opus-4-7` with the v6 system prompt |
| Parse | Extract stage, confidence, anomalous findings, and biological question |

**v6 system prompt steps:**
- **STEP 1** — Evidence Review (cite Z-scores and pathway deltas)
- **STEP 2** — Pattern Recognition (HIGH / MODERATE / LOW confidence grading)
- **STEP 2B** — Cross-Validation (PREDICTED / NEUTRAL / ANOMALOUS per finding)
- **STEP 3** — Mechanism with `[MEASURED]`/`[INFERRED]` causal node labels + Stage inference
- **STEP 4** — Functional Implications + Physiological Priority Ranking (Tier 1–5)
- **STEP 5** — Uncertainty and Gaps (single most valuable next measurement)
- **FINAL** — 3–5 sentences with cited Z-scores + single most important biological question

**Requires** `ANTHROPIC_API_KEY` in environment or `.env` file.

**The interpretation characterises biology, not disease. Clinical conclusions belong to a
qualified physician reviewing the full patient picture.**
""",
)
def interpret_report(report: DeviationReport) -> BiologicalInterpretation:
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "ANTHROPIC_API_KEY is not configured. "
                "Set it in your .env file or as an environment variable."
            ),
        )
    try:
        return reasoning_engine.interpret(report)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.exception("Interpretation failed for sample '%s'", report.sample_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
