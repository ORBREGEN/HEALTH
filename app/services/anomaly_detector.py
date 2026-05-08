"""
Anomaly Detector — Layer 2 analysis engine

Given a gene expression sample, compares it against the Healthy Respiratory Model
and returns a structured DeviationReport across four biological dimensions:

  1. Cell type composition   — which populations are depleted or expanded (Z-scores)
  2. Gene-level deviations   — which genes are outside their healthy distribution
  3. Pathway deviations      — which biological processes deviate from healthy baseline
  4. Fetal reactivation      — whether developmental programmes are re-expressed in adult tissue

The detector does not name diseases. It characterises biology.
Clinical interpretation belongs to the expert in Layer 3.
"""

import logging
from datetime import datetime, timezone

from app.core.exceptions import InsufficientGenesError, ModelNotBuiltError
from app.models.schemas import (
    CellTypeDeviation,
    CellTypeImpairment,
    DeviationReport,
    FetalReactivation,
    GeneDeviation,
    PathwayDeviation,
)
from app.services.respiratory_model import RespiratoryModel, load_model

logger = logging.getLogger(__name__)

# ── Thresholds ─────────────────────────────────────────────────────────────────
MIN_GENES                = 10    # minimum genes required (lowered for dev testing)
Z_REPORT_THRESHOLD       = 2.0   # |Z| ≥ this → gene deviation flagged
PATHWAY_DELTA_THRESHOLD  = 0.8   # log1p CP10K units above/below baseline → pathway flagged
PATHWAY_MIN_GENE_FRAC    = 0.25  # fraction of pathway genes that must be present in sample
FETAL_SCORE_THRESHOLD    = 0.15  # fetal reactivation score above this is biologically notable
CT_Z_THRESHOLD           = 2.0   # |Z| against CT-specific baseline → gene suppressed in that CT context
CT_MIN_GENES_TESTED      = 3     # minimum CT-enriched genes needed to score a cell type
CT_MIN_GENES_SUPPRESSED  = 2     # minimum suppressed genes to flag CT impairment


def _magnitude(z: float) -> str:
    az = abs(z)
    if az >= 4.0: return "severe"
    if az >= 2.5: return "moderate"
    if az >= 1.5: return "mild"
    return "normal"


# ── Model cache ────────────────────────────────────────────────────────────────

_cached_model: RespiratoryModel | None = None


def model_ready() -> bool:
    from app.services.respiratory_model import model_is_built
    return model_is_built()


def reload_model() -> bool:
    global _cached_model
    _cached_model = load_model()
    return _cached_model is not None


def _get_model() -> RespiratoryModel:
    global _cached_model
    if _cached_model is None:
        _cached_model = load_model()
    if _cached_model is None:
        raise ModelNotBuiltError(
            "Healthy Respiratory Model not built. "
            "Call POST /api/v1/model/build to create it."
        )
    return _cached_model


# ── Main entry point ───────────────────────────────────────────────────────────

def analyse(sample_id: str, gene_expression: dict[str, float]) -> DeviationReport:
    if len(gene_expression) < MIN_GENES:
        raise InsufficientGenesError(len(gene_expression), MIN_GENES)

    model = _get_model()

    cell_devs    = _analyse_cell_types(gene_expression, model)
    gene_devs    = _analyse_genes(gene_expression, model)
    pathway_devs = _analyse_pathways(gene_expression, model)
    fetal_result = _analyse_fetal_reactivation(gene_expression, model)
    ct_impairs   = _analyse_ct_gene_impairments(gene_expression, model)
    score        = _overall_score(cell_devs, gene_devs, pathway_devs, fetal_result, ct_impairs)
    summary      = _build_summary(score, cell_devs, gene_devs, pathway_devs, fetal_result, ct_impairs)

    return DeviationReport(
        sample_id               = sample_id,
        analysed_at             = datetime.now(timezone.utc),
        overall_deviation_score = score,
        summary                 = summary,
        cell_type_deviations    = cell_devs,
        gene_deviations         = gene_devs,
        pathway_deviations      = pathway_devs,
        fetal_reactivation      = fetal_result,
        ct_impairments          = ct_impairs,
        healthy_reference_cells  = model.n_cells,
        healthy_reference_donors = model.n_donors,
        model_built_at           = model.built_at,
    )


# ── Dimension 1: Cell type composition ────────────────────────────────────────

def _score_cell_type(
    genes: dict[str, float],
    marker_stats: dict[str, dict],
    global_gene_stats: dict[str, dict],
) -> float:
    """
    Estimate cell type presence using specificity-weighted marker genes.

    A gene contributes only if it is enriched ≥1.0 log1p CP10K above the
    whole-lung global mean. This filters out housekeeping genes (expressed
    everywhere) and weak markers (span too small to be noise-resistant).
    The contribution measures how far the sample sits between the global
    baseline and the cell-type-specific level:

      0.0 → sample at global baseline (cell type absent)
      1.0 → sample fully at cell-type level (cell type dominant)

    This means a noisy healthy control scores near 0.0 for all cell types,
    and rare types with tiny healthy_std do not produce false Z-score explosions.
    """
    scores = []
    for gene, stats in marker_stats.items():
        if gene not in genes:
            continue
        ct_mean     = stats["mean"]
        global_mean = global_gene_stats.get(gene, {}).get("mean", 0.0)
        span        = ct_mean - global_mean
        if span < 1.0:
            continue  # require ≥1 log1p unit enrichment above whole-lung mean
        contribution = (genes[gene] - global_mean) / (span + 1e-6)
        scores.append(max(0.0, min(1.0, contribution)))
    return float(sum(scores) / len(scores)) if scores else 0.0


def _analyse_cell_types(genes: dict[str, float], model: RespiratoryModel) -> list[CellTypeDeviation]:
    deviations = []
    for ct, comp in model.composition.items():
        profile      = model.cell_type_profiles.get(ct, {})
        marker_stats = profile.get("marker_gene_stats", {})
        if not marker_stats:
            continue

        estimated    = _score_cell_type(genes, marker_stats, model.gene_stats)
        mu           = comp["mean_fraction"]
        std          = comp["std_fraction"]
        effective_std = max(std, 0.01)   # floor: prevents Z-explosion for rare types (std≈0.001)
        z            = (estimated - mu) / (effective_std + 1e-6)
        direction = "normal"
        if abs(z) >= 1.5:
            direction = "expanded" if z > 0 else "depleted"

        deviations.append(CellTypeDeviation(
            cell_type             = ct,
            compartment           = comp.get("compartment", "unknown"),
            estimated_fraction    = round(estimated, 4),
            healthy_mean_fraction = round(mu, 4),
            healthy_std_fraction  = round(std, 4),
            z_score               = round(z, 2),
            direction             = direction,
            magnitude             = _magnitude(z),
            interpretation        = _cell_type_interpretation(ct, direction, _magnitude(z)),
        ))

    deviations.sort(key=lambda d: abs(d.z_score), reverse=True)
    return deviations


def _cell_type_interpretation(cell_type: str, direction: str, magnitude: str) -> str:
    if direction == "normal":
        return ""
    ct = cell_type.lower()
    if "at2" in ct or "alveolar type 2" in ct:
        return "AT2 cells produce surfactant; depletion impairs gas exchange and alveolar repair."
    if "alveolar macrophage" in ct:
        return "Alveolar macrophages maintain sterility and clear debris; shifts indicate immune activation."
    if "basal" in ct:
        return "Basal cells are the progenitors of the airway epithelium; changes affect regenerative capacity."
    if "fibroblast" in ct:
        return "Fibroblast expansion is a hallmark of fibrotic remodelling."
    if "endothelial" in ct or "vascular" in ct:
        return "Endothelial shifts indicate vascular injury or angiogenesis."
    if "t cell" in ct or "lymphocyte" in ct:
        return "T cell changes reflect adaptive immune activity — infection, autoimmunity, or exhaustion."
    if "macrophage" in ct or "monocyte" in ct:
        return "Myeloid shifts indicate innate immune activation or resolution failure."
    return ""


# ── Dimension 2: Gene-level Z-scores ──────────────────────────────────────────

def _analyse_genes(genes: dict[str, float], model: RespiratoryModel) -> list[GeneDeviation]:
    deviations = []
    for gene, value in genes.items():
        stats = model.gene_stats.get(gene)
        if stats is None:
            continue
        mu  = stats["mean"]
        std = stats["std"]
        z   = (value - mu) / (std + 1e-6)
        if abs(z) < Z_REPORT_THRESHOLD:
            continue
        direction = "elevated" if z > 0 else "suppressed"
        deviations.append(GeneDeviation(
            gene         = gene,
            sample_value = round(value, 3),
            healthy_mean = round(mu, 3),
            healthy_std  = round(std, 3),
            healthy_p5   = round(stats.get("p5", 0.0), 3),
            healthy_p95  = round(stats.get("p95", 0.0), 3),
            z_score      = round(z, 2),
            direction    = direction,
            magnitude    = _magnitude(z),
        ))

    deviations.sort(key=lambda d: abs(d.z_score), reverse=True)
    return deviations[:100]


# ── Dimension 3: Pathway deviations vs. healthy baseline ──────────────────────

def _analyse_pathways(genes: dict[str, float], model: RespiratoryModel) -> list[PathwayDeviation]:
    """
    Compare sample pathway activity to the healthy baseline stored in the model.

    For each pathway:
      1. Compute sample's mean expression of the pathway's trigger genes
      2. Compute deviation = sample_mean - healthy_baseline_mean
      3. Flag if deviation exceeds PATHWAY_DELTA_THRESHOLD in either direction
      4. Also check suppressor genes for loss of expression

    This is more rigorous than the previous "is gene expressed above 0.5?" approach:
    it measures biological deviation in the same log1p CP10K units as the reference.
    """
    deviations = []

    for pathway_name, baseline in model.pathway_baselines.items():
        genes_tracked = baseline.get("genes_tracked", {})
        if not genes_tracked:
            continue

        triggers    = [g for g, meta in genes_tracked.items() if meta["role"] == "trigger"]
        suppressors = [g for g, meta in genes_tracked.items() if meta["role"] == "suppressor"]

        # Only analyse if enough pathway genes are in the sample
        present_triggers = [g for g in triggers if g in genes]
        if len(present_triggers) < max(1, len(triggers) * PATHWAY_MIN_GENE_FRAC):
            continue

        sample_trigger_mean = sum(genes[g] for g in present_triggers) / len(present_triggers)
        baseline_mean       = baseline.get("trigger_mean_expr", 0.0) or 0.0
        delta               = sample_trigger_mean - baseline_mean

        direction = None
        if delta >= PATHWAY_DELTA_THRESHOLD:
            direction = "over-active"
        elif delta <= -PATHWAY_DELTA_THRESHOLD:
            direction = "suppressed"

        # Check suppressor loss (a second signal for pathway activation)
        if suppressors and direction is None:
            present_supps = [g for g in suppressors if g in genes]
            if present_supps:
                supp_baseline_mean = baseline.get("suppressor_mean_expr") or 0.0
                supp_sample_mean   = sum(genes[g] for g in present_supps) / len(present_supps)
                supp_delta         = supp_sample_mean - supp_baseline_mean
                if supp_delta <= -PATHWAY_DELTA_THRESHOLD:
                    direction = "over-active"  # suppressor loss = pathway disinhibited

        if direction is None:
            continue

        # Identify the most-deviated genes for the report
        if direction == "over-active":
            active_genes = sorted(
                present_triggers,
                key=lambda g: genes[g] - (genes_tracked[g]["mean"] if g in genes_tracked else 0),
                reverse=True,
            )[:10]
        else:
            # suppressed: genes furthest below their healthy mean
            active_genes = sorted(
                present_triggers,
                key=lambda g: genes[g] - (genes_tracked[g]["mean"] if g in genes_tracked else 0),
            )[:10]

        deviations.append(PathwayDeviation(
            pathway                  = pathway_name,
            category                 = baseline.get("category", ""),
            direction                = direction,
            n_active_genes           = len(present_triggers),
            n_total_genes            = len(triggers),
            avg_expression           = round(sample_trigger_mean, 3),
            trigger_baseline_expr    = round(baseline_mean, 3),
            deviation_from_baseline  = round(delta, 3),
            active_genes             = active_genes,
            interpretation           = _pathway_interpretation(pathway_name, direction, delta),
        ))

    deviations.sort(key=lambda d: abs(d.deviation_from_baseline or 0), reverse=True)
    return deviations


def _pathway_interpretation(name: str, direction: str, delta: float) -> str:
    qualifier = "markedly" if abs(delta) >= 1.5 else "moderately"
    if direction == "over-active":
        return f"{name} pathway is {qualifier} over-active ({delta:+.2f} log1p CP10K above healthy baseline)."
    return f"{name} pathway is {qualifier} suppressed ({delta:+.2f} log1p CP10K below healthy baseline)."


# ── Dimension 4: Fetal reactivation ───────────────────────────────────────────

def _analyse_fetal_reactivation(
    genes: dict[str, float], model: RespiratoryModel
) -> FetalReactivation | None:
    """
    Measure how much the sample re-expresses developmental (fetal) gene programmes.

    Requires the fetal_reference artefact. Returns None if unavailable.

    Score definition:
      For each fetal-enriched gene present in the sample:
        gene_score = (sample_value - adult_mean) / (fetal_mean - adult_mean + ε)
      Clamped to [0, 1], then averaged across all tested genes.

    score ≈ 0: expression of fetal genes is at adult-healthy levels
    score ≈ 1: expression matches the fetal reference level
    """
    if not model.has_fetal_reference:
        return None

    fetal_enriched = model.fetal_reference.get("fetal_enriched", {})
    if not fetal_enriched:
        return None

    # Only test genes present in both the fetal reference and the sample
    testable = {
        gene: info
        for gene, info in fetal_enriched.items()
        if gene in genes
    }

    if len(testable) < 5:
        return None  # too few genes for a reliable score

    gene_scores: list[tuple[str, float]] = []
    for gene, ref in testable.items():
        adult_mean = ref.get("adult_mean", 0.0)
        fetal_mean = ref.get("fetal_mean", adult_mean)
        span       = fetal_mean - adult_mean
        if span < 0.1:
            continue  # small span — gene does not distinguish fetal from adult well

        raw_score = (genes[gene] - adult_mean) / (span + 1e-6)
        clamped   = max(0.0, min(1.0, raw_score))
        gene_scores.append((gene, clamped))

    if not gene_scores:
        return None

    overall_score  = sum(s for _, s in gene_scores) / len(gene_scores)
    n_reactivated  = sum(1 for _, s in gene_scores if s > 0.3)
    top_reactivated = [g for g, s in sorted(gene_scores, key=lambda x: x[1], reverse=True)[:10]]

    if overall_score >= FETAL_SCORE_THRESHOLD:
        interp = (
            f"Fetal gene programmes are partially re-active (score={overall_score:.2f}). "
            f"{n_reactivated}/{len(gene_scores)} developmental genes are elevated above adult baseline. "
            "This may indicate dedifferentiation, regenerative progenitor expansion, or oncogenic reprogramming."
        )
    else:
        interp = (
            f"Fetal gene expression is at adult-healthy levels (score={overall_score:.2f}). "
            "No significant developmental programme re-activation detected."
        )

    return FetalReactivation(
        score                     = round(overall_score, 3),
        n_fetal_genes_tested      = len(gene_scores),
        n_fetal_genes_reactivated = n_reactivated,
        top_reactivated_genes     = top_reactivated,
        interpretation            = interp,
    )


# ── Dimension 5: CT-specific gene impairments ─────────────────────────────────

def _analyse_ct_gene_impairments(
    genes: dict[str, float], model: RespiratoryModel
) -> list[CellTypeImpairment]:
    """
    Detect cell types whose signature genes are suppressed below their CT-specific baseline.

    Uses gene_stats_by_cell_type artefact: for each cell type, Z-scores its CT-enriched
    genes against CT-specific means/stds (not global). This catches suppression that
    global Z-scores miss — e.g. SFTPC at 0.2 in an AT2-rich sample:
      global Z = (0.2 − 0.78) / 1.27 ≈ −0.5  (below threshold)
      CT Z     = (0.2 − 6.0)  / 1.0  ≈ −5.8  (strongly flagged)

    Requires the gene_stats_by_cell_type artefact (optional; returns [] if absent).
    """
    if not model.ct_gene_stats:
        return []

    impairments = []

    for ct_name, ct_stats in model.ct_gene_stats.items():
        tested: list[tuple[str, float]] = []
        suppressed: list[tuple[str, float]] = []

        for gene, cts in ct_stats.items():
            if gene not in genes:
                continue
            z = (genes[gene] - cts["mean"]) / (cts["std"] + 1e-6)
            tested.append((gene, z))
            if z <= -CT_Z_THRESHOLD:
                suppressed.append((gene, z))

        if len(tested) < CT_MIN_GENES_TESTED:
            continue
        if len(suppressed) < CT_MIN_GENES_SUPPRESSED:
            continue

        mean_z = sum(z for _, z in tested) / len(tested)
        top_suppressed = [g for g, _ in sorted(suppressed, key=lambda x: x[1])[:10]]

        comp = model.composition.get(ct_name, {})
        impairments.append(CellTypeImpairment(
            cell_type          = ct_name,
            compartment        = comp.get("compartment", "unknown"),
            n_genes_tested     = len(tested),
            n_genes_suppressed = len(suppressed),
            mean_z_score       = round(mean_z, 2),
            most_suppressed_genes = top_suppressed,
            interpretation     = (
                f"{ct_name} molecular programme is suppressed "
                f"({len(suppressed)}/{len(tested)} signature genes below CT-specific baseline, "
                f"mean Z={mean_z:.1f}). "
                "The cell type may be present but functionally impaired."
            ),
        ))

    impairments.sort(key=lambda d: d.mean_z_score)
    return impairments


# ── Overall deviation score ────────────────────────────────────────────────────

def _overall_score(
    cell_devs:    list[CellTypeDeviation],
    gene_devs:    list[GeneDeviation],
    pathway_devs: list[PathwayDeviation],
    fetal:        FetalReactivation | None,
    ct_impairs:   list[CellTypeImpairment],
) -> float:
    """
    Weighted composite score across five dimensions.
    Each sub-score is normalised to [0, 1] before weighting.
    """
    def cell_score() -> float:
        if not cell_devs:
            return 0.0
        scoreable = [
            d for d in cell_devs
            if d.healthy_mean_fraction >= 0.005 and d.direction != "normal"
        ]
        if not scoreable:
            return 0.0
        return min(sum(abs(d.z_score) for d in scoreable) / (len(cell_devs) * 6.0), 1.0)

    def gene_score() -> float:
        if not gene_devs:
            return 0.0
        top = gene_devs[:20]
        return min(sum(abs(d.z_score) for d in top) / (len(top) * 8.0), 1.0)

    def pathway_score() -> float:
        if not pathway_devs:
            return 0.0
        raw = sum(min(abs(d.deviation_from_baseline or 0) / 2.0, 1.0) for d in pathway_devs)
        return min(raw / max(len(model.pathway_baselines if (model := _cached_model) else {}), 6), 1.0)

    def fetal_score() -> float:
        return fetal.score if fetal is not None else 0.0

    def ct_impairment_score() -> float:
        if not ct_impairs:
            return 0.0
        # Fraction of marker genes suppressed — more sensitive than mean Z / 8
        fracs = [d.n_genes_suppressed / max(d.n_genes_tested, 1) for d in ct_impairs]
        return min(max(fracs), 1.0)

    return round(
        0.25 * cell_score()          +
        0.25 * gene_score()          +
        0.20 * pathway_score()       +
        0.10 * fetal_score()         +
        0.20 * ct_impairment_score(),
        3,
    )


# ── Summary ────────────────────────────────────────────────────────────────────

def _build_summary(
    score:        float,
    cell_devs:    list[CellTypeDeviation],
    gene_devs:    list[GeneDeviation],
    pathway_devs: list[PathwayDeviation],
    fetal:        FetalReactivation | None,
    ct_impairs:   list[CellTypeImpairment],
) -> str:
    if score < 0.08:
        return "Sample is within the normal range across all analysis dimensions."

    parts = []

    non_normal = [d for d in cell_devs if d.direction != "normal"]
    if non_normal:
        top = non_normal[0]
        parts.append(f"{top.cell_type} is {top.direction} ({top.magnitude}, Z={top.z_score:+.1f})")

    if gene_devs:
        top_genes = [d.gene for d in gene_devs[:4]]
        parts.append(f"gene deviations in {', '.join(top_genes)}")

    if pathway_devs:
        top_pw = pathway_devs[0]
        parts.append(
            f"{top_pw.pathway} pathway {top_pw.direction} "
            f"({top_pw.deviation_from_baseline:+.2f} log1p from baseline)"
        )

    if fetal and fetal.score >= FETAL_SCORE_THRESHOLD:
        parts.append(
            f"fetal programme re-activation (score={fetal.score:.2f}, "
            f"top genes: {', '.join(fetal.top_reactivated_genes[:3])})"
        )

    if ct_impairs:
        worst = ct_impairs[0]
        parts.append(
            f"{worst.cell_type} molecular programme suppressed "
            f"({worst.n_genes_suppressed}/{worst.n_genes_tested} genes, mean Z={worst.mean_z_score:.1f})"
        )

    prefix = (
        "Mild deviation" if score < 0.3 else
        "Moderate deviation" if score < 0.6 else
        "Substantial deviation"
    )
    body = ". ".join(p[0].upper() + p[1:] for p in parts) + ("." if parts else "")
    return f"{prefix} from healthy respiratory reference. {body}".strip()
