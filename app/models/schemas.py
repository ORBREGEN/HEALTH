"""
Pydantic schemas — API contract for the HEALTH platform.

Layer 2 — Respiratory Intelligence Engine
  GeneExpressionSample       ← input
  DeviationReport            ← output: biological characterisation of the sample
    CellTypeDeviation[]      ← which cell types are depleted or expanded
    GeneDeviation[]          ← which genes are outside healthy range
    PathwayDeviation[]       ← which biological processes are dysregulated
    FetalReactivation        ← developmental programme re-activation score

Layer 1 — Patient Portal
  PatientIntake              ← symptoms and history from a citizen
  SpecialistMatch[]          ← matched specialists

Layer 3 — Expert Network (future)
  ExpertAnnotation           ← expert review of a deviation report
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── System ────────────────────────────────────────────────────────────────────

class SystemHealth(BaseModel):
    status: str
    version: str
    timestamp: datetime
    model_ready: bool = Field(False, description="True when the Healthy Respiratory Model is built")


# ── Layer 2: Respiratory Intelligence Engine ──────────────────────────────────

class ModelStatus(BaseModel):
    is_ready: bool
    built_at: str | None = None
    n_healthy_cells: int | None = None
    n_donors: int | None = None
    n_genes_tracked: int | None = None
    n_cell_types: int | None = None
    n_pathways: int | None = Field(None, description="Number of biological pathways with healthy baselines")
    has_fetal_reference: bool = Field(False, description="True when fetal developmental reference is loaded")
    has_spatial_baselines: bool = Field(False, description="True when Visium spatial baselines are loaded")
    message: str = ""


class GeneExpressionSample(BaseModel):
    """
    A gene expression profile to analyse against the Healthy Respiratory Model.

    Values must be log1p-normalised counts per 10,000 (log1p CP10K) —
    the same scale used in the HLCA and CellxGene Census.

    Minimum 10 genes for dev/testing. 500–2000 genes gives reliable cell-type resolution.
    """
    sample_id: str
    gene_expression: dict[str, float] = Field(
        ...,
        description="gene symbol → log1p(CP10K) expression value",
        min_length=10,
    )
    metadata: dict[str, Any] | None = Field(
        None,
        description="Optional: age, sex, smoking history, tissue region, assay type, etc.",
    )

    model_config = {"json_schema_extra": {"example": {
        "sample_id": "lab_sample_001",
        "gene_expression": {
            "SFTPC": 8.3, "SFTPB": 7.1, "AGER": 6.8,
            "FOXJ1": 5.2, "ACTA2": 3.2, "COL1A1": 1.1,
        },
        "metadata": {"age": 58, "sex": "male", "smoking_status": "never"},
    }}}


class CellTypeDeviation(BaseModel):
    """How much a cell type deviates from its expected proportion in healthy lung."""
    cell_type: str
    compartment: str = Field(..., description="alveolar | airway | immune | stromal | vascular")
    estimated_fraction: float
    healthy_mean_fraction: float
    healthy_std_fraction: float
    z_score: float
    direction: str = Field(..., description="'depleted' | 'expanded' | 'normal'")
    magnitude: str = Field(..., description="'severe' | 'moderate' | 'mild' | 'normal'")
    interpretation: str = ""


class GeneDeviation(BaseModel):
    """A gene whose expression is significantly outside the healthy range."""
    gene: str
    sample_value: float
    healthy_mean: float
    healthy_std: float
    healthy_p5: float
    healthy_p95: float
    z_score: float
    direction: str = Field(..., description="'elevated' | 'suppressed'")
    magnitude: str = Field(..., description="'severe' | 'moderate' | 'mild'")


class PathwayDeviation(BaseModel):
    """
    A biological pathway that deviates from its healthy baseline activity.

    The comparison is against the healthy baseline (trigger_baseline_expr),
    not just a fixed expression threshold. This makes the deviation meaningful:
    a pathway at +1.5 log1p units above its healthy tone is far more informative
    than knowing that some genes are expressed above zero.
    """
    pathway: str
    category: str
    direction: str = Field(..., description="'over-active' | 'suppressed'")
    n_active_genes: int
    n_total_genes: int
    avg_expression: float = Field(..., description="Mean expression of pathway genes in the sample")
    trigger_baseline_expr: float | None = Field(
        None, description="Healthy baseline mean expression of trigger genes (for reference)"
    )
    deviation_from_baseline: float | None = Field(
        None, description="sample_avg_expr minus healthy_baseline_expr (log1p CP10K units)"
    )
    active_genes: list[str] = Field(default_factory=list)
    interpretation: str = ""


class FetalReactivation(BaseModel):
    """
    Score indicating how much the sample re-expresses developmental (fetal) gene programmes.

    In a healthy adult lung, fetal developmental genes are largely silenced.
    Their re-activation can indicate dedifferentiation, oncogenic transformation,
    or regenerative progenitor expansion.

    score = 0.0 means the sample's fetal-gene expression is at adult-healthy levels.
    score = 1.0 means it matches fetal-tissue levels.
    """
    score: float = Field(..., ge=0.0, le=1.0,
        description="0.0 = adult-like, 1.0 = fetal-like expression of developmental genes"
    )
    n_fetal_genes_tested: int
    n_fetal_genes_reactivated: int = Field(
        ..., description="Genes above the adult healthy mean for fetal-enriched genes"
    )
    top_reactivated_genes: list[str] = Field(
        default_factory=list,
        description="Up to 10 fetal-enriched genes with highest expression in this sample"
    )
    interpretation: str = ""


class CellTypeImpairment(BaseModel):
    """
    A cell type whose signature genes are suppressed below their cell-type-specific baseline.

    Detected by the fifth analysis dimension (CT-aware gene Z-scoring).
    This catches functional impairment that global Z-scores miss — e.g. SFTPC suppressed
    in an AT2-rich sample reads Z ≈ −0.5 globally but Z ≈ −5.8 against the AT2 baseline.

    Requires the gene_stats_by_cell_type artefact (built by Notebook 02 Section 7).
    """
    cell_type: str
    compartment: str = Field(..., description="alveolar | airway | immune | stromal | vascular")
    n_genes_tested: int
    n_genes_suppressed: int = Field(
        ..., description="Genes with Z < -2.0 against CT-specific baseline"
    )
    mean_z_score: float = Field(
        ..., description="Mean Z-score of all tested signature genes (negative = functionally suppressed)"
    )
    most_suppressed_genes: list[str] = Field(
        default_factory=list,
        description="Up to 10 most suppressed signature genes (ranked by CT-specific Z-score)"
    )
    interpretation: str = ""


class DeviationReport(BaseModel):
    """
    The output of the Respiratory Intelligence Engine for one sample.

    Describes how the sample deviates from the Healthy Respiratory Model
    across five biological dimensions.

    Does not name a disease. Describes biology. A clinician interprets this report.
    """
    sample_id: str
    analysed_at: datetime

    overall_deviation_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="0.0 = indistinguishable from healthy, 1.0 = maximally abnormal",
    )
    summary: str = Field(..., description="Short biological summary of the most salient findings")

    # ── Five analysis dimensions ───────────────────────────────────────────────
    cell_type_deviations: list[CellTypeDeviation]
    gene_deviations:      list[GeneDeviation]
    pathway_deviations:   list[PathwayDeviation]
    fetal_reactivation:   FetalReactivation | None = Field(
        None,
        description="Developmental programme re-activation (populated when fetal reference is available)"
    )
    ct_impairments: list[CellTypeImpairment] = Field(
        default_factory=list,
        description=(
            "Cell types whose signature genes are suppressed below CT-specific baselines. "
            "Populated when gene_stats_by_cell_type artefact is available."
        )
    )

    # ── Reference information ──────────────────────────────────────────────────
    healthy_reference_cells:  int
    healthy_reference_donors: int
    model_built_at:           str

    safety_disclaimer: str = Field(
        default=(
            "This report characterises gene expression deviation from a healthy respiratory "
            "reference. It is intended to assist qualified researchers and clinicians — "
            "it does not constitute a clinical diagnosis. All findings require validation "
            "by certified medical personnel using approved diagnostic procedures."
        )
    )


# ── Layer 1: Patient Portal ───────────────────────────────────────────────────

class Symptom(str, Enum):
    SHORTNESS_OF_BREATH    = "shortness_of_breath"
    CHRONIC_COUGH          = "chronic_cough"
    WHEEZING               = "wheezing"
    CHEST_TIGHTNESS        = "chest_tightness"
    COUGHING_BLOOD         = "coughing_blood"
    FATIGUE                = "fatigue"
    FEVER                  = "fever"
    NIGHT_SWEATS           = "night_sweats"
    UNINTENDED_WEIGHT_LOSS = "unintended_weight_loss"
    RECURRENT_INFECTIONS   = "recurrent_infections"


class PatientIntake(BaseModel):
    """
    What a citizen provides when seeking help.
    No genomics required. Plain language symptoms and history.
    """
    patient_id: str
    symptoms: list[Symptom] = Field(..., min_length=1)
    symptom_duration_weeks: int | None = None
    age:             int | None = None
    sex:             str | None = None
    smoking_history: str | None = Field(None, description="never | former | current")
    location:        str | None = Field(None, description="City or region — helps with specialist availability")
    additional_notes: str | None = None


class SpecialistType(str, Enum):
    PULMONOLOGIST                = "pulmonologist"
    THORACIC_ONCOLOGIST          = "thoracic_oncologist"
    RESPIRATORY_IMMUNOLOGIST     = "respiratory_immunologist"
    INTERVENTIONAL_PULMONOLOGIST = "interventional_pulmonologist"
    SLEEP_MEDICINE               = "sleep_medicine"


class SpecialistMatch(BaseModel):
    """A recommended specialist type for a patient, with reasoning."""
    specialist_type: SpecialistType
    reason: str = Field(..., description="Why this specialist type fits the symptom pattern")
    urgency: str = Field(..., description="'routine' | 'soon' | 'urgent'")
    biological_context: str = Field(
        "",
        description="What the model knows about this symptom pattern at the cellular level (when model is available)"
    )


# ── Layer 2: Biological Reasoning Engine ─────────────────────────────────────

class BiologicalInterpretation(BaseModel):
    """
    The output of the Reasoning Engine for one DeviationReport.

    Produced by POST /api/v1/interpret using the v6 chain-of-thought prompt
    and claude-opus-4-7. Contains the full step-by-step reasoning text and
    key structured fields extracted from it.

    Does not name diseases. Characterises biology. Clinicians draw conclusions.
    """
    sample_id: str
    interpreted_at: datetime
    model_id: str = Field(..., description="Claude model used for reasoning")
    prompt_version: str = Field(..., description="System prompt version (e.g. 'v6')")
    overall_deviation_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="Overall deviation score from the source DeviationReport"
    )

    # ── Structured fields extracted from the reasoning ─────────────────────
    stage: str | None = Field(
        None,
        description="Inferred biological process stage: INITIATING | ACTIVE | ESTABLISHED | RESOLVING"
    )
    overall_confidence: str | None = Field(
        None,
        description="Overall confidence in the interpretation: HIGH | MODERATE | LOW"
    )
    anomalous_findings: list[str] = Field(
        default_factory=list,
        description="Findings classified ANOMALOUS in Step 2B cross-validation"
    )

    # ── Text output ────────────────────────────────────────────────────────
    final_interpretation: str = Field(
        "",
        description="Extracted FINAL INTERPRETATION section (3–5 sentences with cited Z-scores)"
    )
    biological_question: str = Field(
        "",
        description="The single most important biological question raised by this profile"
    )
    full_reasoning: str = Field(
        ...,
        description=(
            "Complete chain-of-thought reasoning: Evidence Review → Pattern Recognition → "
            "Cross-Validation → Mechanism → Functional Implications → Uncertainty → "
            "Final Interpretation"
        )
    )

    safety_disclaimer: str = Field(
        default=(
            "RESEARCH USE ONLY — This interpretation is produced by an AI model trained on "
            "healthy lung reference data. It characterises gene expression deviation from a "
            "healthy respiratory reference. It does not constitute a clinical diagnosis and "
            "has not been reviewed by a qualified clinician. All findings require validation "
            "by certified medical personnel using approved diagnostic procedures."
        )
    )
