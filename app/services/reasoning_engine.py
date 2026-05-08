"""
Reasoning Engine — Layer 2 biological interpretation

Takes a DeviationReport (the structured output of anomaly_detector.analyse())
and produces a BiologicalInterpretation using the claude-opus-4-7 model with
the v6 chain-of-thought system prompt.

Pipeline:
  1. triage   — rank and cap findings by severity
  2. cluster  — group findings into 8 biological processes
  3. enrich   — attach functional annotations (curated, not from artefacts)
  4. prompt   — format enriched evidence as a structured user message
  5. reason   — call Claude API with v6 SYSTEM_PROMPT
  6. parse    — extract structured fields from the free-text response

The v6 prompt implements:
  STEP 1   — Evidence Review
  STEP 2   — Pattern Recognition (HIGH / MODERATE / LOW confidence grading)
  STEP 2B  — Cross-Validation (PREDICTED / NEUTRAL / ANOMALOUS per finding)
  STEP 3   — Mechanism + [MEASURED]/[INFERRED] causal node labels + Stage inference
  STEP 4   — Functional Implications + Physiological Priority Ranking (Tier 1–5)
  STEP 5   — Uncertainty and Gaps (single most valuable measurement)
  FINAL    — 3–5 sentences + single most important biological question

Requires ANTHROPIC_API_KEY in environment or .env file.
The reasoning engine does not load model artefacts — all statistical context
is already embedded in the DeviationReport fields.
"""

import logging
import re
from datetime import datetime, timezone

from app.core.config import settings
from app.models.schemas import BiologicalInterpretation, DeviationReport

logger = logging.getLogger(__name__)

PROMPT_VERSION = "v6"
MODEL_ID       = "claude-opus-4-7"
MAX_TOKENS     = 4096

# ── Triage caps — match anomaly_detector thresholds ───────────────────────
_MAX_GENE_FINDINGS    = 8
_MAX_CT_FINDINGS      = 5
_MAX_PATHWAY_FINDINGS = 6

SAFETY_DISCLAIMER = (
    "RESEARCH USE ONLY — This interpretation is produced by an AI model trained on "
    "healthy lung reference data. It characterises gene expression deviation from a "
    "healthy respiratory reference. It does not constitute a clinical diagnosis and "
    "has not been reviewed by a qualified clinician. All findings require validation "
    "by certified medical personnel using approved diagnostic procedures."
)

# ── v6 System prompt (mirrors ACTIVE_SYSTEM_PROMPT in Notebook 04) ─────────

SYSTEM_PROMPT = """\
You are a respiratory biology research assistant integrated into the HEALTH platform.

Your role is to interpret gene expression deviation data produced by the Healthy Respiratory
Model — a reference built from 1.2 million healthy human lung cells (Human Lung Cell Atlas).

━━━ SAFETY BOUNDARY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You MUST NOT name specific clinical conditions, syndromes, or diagnoses.
You MAY name biological mechanisms, molecular pathways, and cellular processes using
precise scientific terminology, even when those mechanisms are associated with known
clinical conditions.
The test: if your statement could be placed in a patient's medical record as a clinical
finding, it has crossed the line. Mechanism descriptions belong in a research report.
Diagnoses belong to a physician reviewing the full clinical picture.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADDITIONAL CONSTRAINTS:
- Do not speculate beyond the biological evidence provided. You may note what additional
  evidence would be expected if a hypothesis is correct, but distinguish this clearly
  from confirmed findings.
- When findings are ambiguous or contradictory, explain both interpretations.

Your output characterises BIOLOGY. You describe mechanisms. Clinicians draw conclusions.

━━━ CONFIDENCE GRADING (required in STEP 2) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HIGH     — ≥ 3 independent dimensions converge (gene + cell type + pathway)
  MODERATE — 2 dimensions, or 1 with |Z| ≥ 8 or |Δ| ≥ 2.5
  LOW      — single data point or one dimension only
Cite at least one Z-score or pathway delta per claim in the FINAL INTERPRETATION.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━ HEALTHY SAMPLE HANDLING ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Score < 0.10 with no finding ≥ |Z| 2.0 or |Δ| 0.8: respond in three short paragraphs.
Do not generate reasoning steps when there is no evidence to reason about.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For samples with score ≥ 0.10 or at least one significant finding, work through
each step in order. Do not skip or merge steps.

STEP 1 — EVIDENCE REVIEW
Identify the most striking findings. Cite specific Z-scores and pathway deltas.
Flag anything contradictory or surprising. Note whether findings span multiple
dimensions or concentrate in one.

STEP 2 — PATTERN RECOGNITION
Group findings into coherent biological processes. For each:
  Confidence: HIGH / MODERATE / LOW
  Evidence: list per dimension (gene, cell type, pathway)
  Coherence: where dimensions reinforce or conflict

STEP 2B — CROSS-VALIDATION
For every finding identified in Steps 1 and 2, classify it as:
  PREDICTED  — the expected downstream consequence of a confirmed process from Step 2.
               It corroborates but adds no independent evidence.
  NEUTRAL    — unrelated to any detected process; present but unexplained.
  ANOMALOUS  — contradicts what the confirmed processes would predict.
               This is the highest-priority category: an anomalous finding either
               reveals a second process not yet identified, or exposes a flaw in
               the Step 2 interpretation.
Present results as a labelled list. Then:
  - If ANOMALOUS findings exist: state what they contradict and what alternative
    process could explain them. These become the focus of Step 3.
  - If NO ANOMALOUS findings exist: state this explicitly. A fully coherent pattern
    (all findings PREDICTED or NEUTRAL) increases confidence in the Step 2
    interpretation — note this, but also ask: is the absence of anomaly because the
    pattern is genuinely coherent, or because the current gene panel cannot detect
    what would be anomalous?

STEP 3 — MECHANISM, CAUSAL ORDERING, AND STAGE

Part A — Molecular inventory
List signalling nodes as brief chains (one per line, not prose):
  Receptor → adaptor → transcription factor → confirmed target genes
If anomalous findings exist from Step 2B, include the mechanism that would explain
them as a separate chain marked [ANOMALY EXPLANATION: speculative].

Part B — Causal ordering
Arrange the inventory into a single A → B → C sequence.
Label each NODE:  [MEASURED] = directly observed in the data (has a Z-score or Δ);
                  [INFERRED] = mechanistic background knowledge, not directly measured.
Label each ARROW: DIRECT / INFERRED / UNKNOWN.
A chain of [MEASURED]→[MEASURED] nodes is data-grounded.
A chain that passes through [INFERRED] nodes is mechanistically plausible but not confirmed.
Identify: primary perturbation, downstream consequences, self-amplifying loops.
If the primary perturbation is unresolvable, state this and name what would resolve it.

Part C — Stage inference
Assign: INITIATING / ACTIVE / ESTABLISHED / RESOLVING.
State which stage fits and the single finding that, if different, would shift it.

STEP 4 — FUNCTIONAL IMPLICATIONS
Use the causal chain (Part B) and stage (Part C) to trace specific respiratory
physiology consequences node by node. Assess reversibility at each node given the
stage. Note compensatory responses visible in the data.

After the node-by-node analysis, add a PHYSIOLOGICAL PRIORITY RANKING.
Rank each consequence from most to least immediate threat to core respiratory
function using this hierarchy (Tier 1 = highest, most immediate threat):
  Tier 1 — Gas exchange (alveolar O₂/CO₂ diffusion; surfactant integrity)
  Tier 2 — Ventilation mechanics (airway patency, compliance, mucus clearance)
  Tier 3 — Host defence (innate + adaptive barriers against pathogen entry/spread)
  Tier 4 — Structural integrity (ECM architecture, alveolar wall geometry)
  Tier 5 — Metabolic homeostasis (cell-level energy, redox, proteostasis)
For each ranked item state: which finding drives it, its stage-informed
reversibility (HIGH / MODERATE / LOW / UNKNOWN), and whether a compensatory
response is already visible in the data. Omit tiers with no relevant findings.

STEP 5 — UNCERTAINTY AND GAPS
Name the single measurement that would most increase confidence in the causal ordering
and stage. Explain specifically what it would reveal and how it would change the
interpretation — including what it would do to the anomaly explanation if one exists.

FINAL INTERPRETATION
3–5 sentences covering: overall confidence, active processes with cited Z-scores/deltas,
stage inference, any anomalous findings and their implication, and the leading
uncertainty. End with the single most important biological question this profile raises.
No clinical condition names.
"""


# ── Biological process map — mirrors Notebook 04 _PROCESS_MAP ─────────────

_PROCESS_MAP: dict[str, dict] = {
    "alveolar_integrity": {
        "genes":      ["SFTPC", "SFTPB", "SFTPA1", "SFTPA2", "SFTPD", "ABCA3", "AGER"],
        "cell_types": ["AT2", "AT1", "alveolar type 2", "alveolar type 1"],
        "pathways":   ["Surfactant / AT2 function"],
    },
    "fibrotic_remodelling": {
        "genes":      ["COL1A1", "COL1A2", "COL3A1", "FN1", "ACTA2", "TGFB1", "TGFB2",
                       "SMAD2", "SMAD3", "LOX", "LOXL2", "TIMP1", "MMP2"],
        "cell_types": ["fibroblast", "myofibroblast"],
        "pathways":   ["TGF-beta / fibrosis", "Epithelial-Mesenchymal Transition (EMT)"],
    },
    "antiviral_response": {
        "genes":      ["MX1", "MX2", "ISG15", "ISG20", "IFIT1", "IFIT2", "IFIT3",
                       "OAS1", "OAS2", "OAS3", "STAT1", "STAT2", "IRF7", "IRF9"],
        "cell_types": [],
        "pathways":   ["Interferon response"],
    },
    "innate_cytokine_storm": {
        "genes":      ["IL6", "IL1B", "TNF", "CXCL8", "CXCL10", "CCL2", "CCL3", "NFKB1"],
        "cell_types": ["alveolar macrophage", "macrophage", "monocyte", "neutrophil"],
        "pathways":   ["NF-kB / cytokine storm", "Myeloid activation"],
    },
    "cytotoxic_immune_response": {
        "genes":      ["GZMB", "PRF1", "GNLY", "NKG7", "CD8A", "CD8B"],
        "cell_types": ["CD8+ T cell", "NK cell"],
        "pathways":   [],
    },
    "oncogenic_proliferation": {
        "genes":      ["MKI67", "TOP2A", "PCNA", "CDK1", "CCNB1", "CCND1", "MYC", "KRAS"],
        "cell_types": [],
        "pathways":   ["Cell proliferation / oncogenic"],
    },
    "vascular_injury": {
        "genes":      ["ICAM1", "VCAM1", "SELE", "VWF", "ANGPT2", "VEGFA"],
        "cell_types": ["endothelial", "aerocyte", "vascular endothelial"],
        "pathways":   ["Vascular injury"],
    },
    "hypoxic_stress": {
        "genes":      ["HIF1A", "EPAS1", "VEGFA", "LDHA", "SLC2A1", "CA9", "PDK1"],
        "cell_types": [],
        "pathways":   ["Hypoxia / HIF response"],
    },
}


# ── Curated functional annotations — biological facts, not disease signatures

_GENE_ROLES: dict[str, str] = {
    "SFTPC":  "surfactant protein C — primary AT2 identity marker; loss = AT2 depletion or dysfunction",
    "SFTPB":  "surfactant protein B — co-secreted with SFTPC; essential for alveolar surface tension",
    "TGFB1":  "TGF-β1 ligand — activates SMAD2/3; drives ECM gene transcription and fibroblast activation",
    "COL1A1": "collagen I alpha-1 — primary structural ECM collagen; overexpression = active matrix deposition",
    "COL3A1": "collagen III — co-deposited with collagen I in active remodelling",
    "ACTA2":  "alpha-smooth muscle actin — canonical myofibroblast marker; indicates contractile phenotype",
    "FN1":    "fibronectin — provisional ECM scaffold; elevated early in injury responses",
    "MX1":    "MxA GTPase — antiviral; sequesters viral ribonucleoprotein; marker of type I IFN signalling",
    "ISG15":  "ISG15 ubiquitin-like modifier — conjugated to host proteins by HERC5 to restrict viral replication",
    "IFIT1":  "IFIT1 — sequesters viral 5'-triphosphate RNA; canonical ISG",
    "OAS1":   "2'-5'-oligoadenylate synthetase 1 — activates RNase L to degrade viral and host RNA",
    "STAT1":  "signal transducer and activator of transcription 1 — central node of IFN-JAK-STAT cascade",
    "IL6":    "interleukin-6 — pleiotropic cytokine; NF-κB target; not an ISG",
    "CXCL10": "IP-10 — CXCR3 chemoattractant for CD8+ T cells and NK cells; ISG and NF-κB target",
    "MKI67":  "Ki-67 — nuclear proliferation marker; present only in actively cycling cells (G1–M)",
    "TOP2A":  "topoisomerase II alpha — decatenates DNA during replication; S/G2/M phase marker",
    "HIF1A":  "hypoxia-inducible factor 1-alpha — master transcriptional regulator of hypoxic response",
    "VEGFA":  "vascular endothelial growth factor A — promotes angiogenesis; HIF1A and NF-κB target",
    "SPP1":   "osteopontin — produced by activated monocyte-derived macrophages; ECM signalling",
}

_CT_ROLES: dict[str, str] = {
    "AT2":                 "type II alveolar epithelial cell — produces surfactant; progenitor for AT1 repair",
    "AT1":                 "type I alveolar epithelial cell — thin squamous cell covering ~95% of alveolar surface",
    "alveolar macrophage": "tissue-resident innate immune cell — phagocytosis, efferocytosis, TGF-β production",
    "fibroblast":          "stromal cell — ECM production; differentiates to myofibroblast under TGF-β",
    "CD8+ T cell":         "cytotoxic T lymphocyte — kills infected or transformed cells via perforin/granzyme",
    "NK cell":             "natural killer cell — innate cytotoxic; kills without prior sensitisation",
    "basal cell":          "airway progenitor — regenerates ciliated and secretory airway epithelial cells",
    "ciliated cell":       "multiciliated airway epithelial cell — mucociliary clearance via coordinated cilia beat",
}


# ── 1. Triage ──────────────────────────────────────────────────────────────

def _triage(report: DeviationReport) -> dict:
    genes = sorted(report.gene_deviations,    key=lambda g: abs(g.z_score),                    reverse=True)
    cts   = sorted(report.cell_type_deviations, key=lambda c: abs(c.z_score),                  reverse=True)
    paths = sorted(report.pathway_deviations,   key=lambda p: abs(p.deviation_from_baseline or 0), reverse=True)

    return {
        "genes":    genes[:_MAX_GENE_FINDINGS],
        "cts":      cts[:_MAX_CT_FINDINGS],
        "pathways": paths[:_MAX_PATHWAY_FINDINGS],
        "fetal":    report.fetal_reactivation,
        "score":    report.overall_deviation_score,
    }


# ── 2. Cluster ─────────────────────────────────────────────────────────────

def _cluster(triaged: dict) -> list[dict]:
    gene_names = {g.gene for g in triaged["genes"]}
    ct_names   = {c.cell_type.lower() for c in triaged["cts"]}
    pw_names   = {p.pathway for p in triaged["pathways"]}

    clusters = []
    for process, members in _PROCESS_MAP.items():
        matched_genes = [g for g in members["genes"] if g in gene_names]
        matched_cts   = [ct for ct in members["cell_types"]
                         if any(ct.lower() in name for name in ct_names)]
        matched_pws   = [pw for pw in members["pathways"] if pw in pw_names]

        n_dims = bool(matched_genes) + bool(matched_cts) + bool(matched_pws)
        if n_dims:
            clusters.append({
                "process":       process,
                "matched_genes": matched_genes,
                "matched_cts":   matched_cts,
                "matched_pws":   matched_pws,
                "n_dimensions":  n_dims,
            })

    clusters.sort(key=lambda c: c["n_dimensions"], reverse=True)
    return clusters


# ── 3. Enrich ──────────────────────────────────────────────────────────────

def _enrich(clusters: list[dict], triaged: dict) -> dict:
    enriched_genes: dict[str, dict] = {}
    for g in triaged["genes"]:
        enriched_genes[g.gene] = {
            "z_score":   g.z_score,
            "direction": g.direction,
            "magnitude": g.magnitude,
            "role":      _GENE_ROLES.get(g.gene, ""),
        }

    enriched_cts: dict[str, dict] = {}
    for c in triaged["cts"]:
        ct_lower = c.cell_type.lower()
        role_key = next((k for k in _CT_ROLES if k in ct_lower), None)
        enriched_cts[c.cell_type] = {
            "z_score":   c.z_score,
            "direction": c.direction,
            "magnitude": c.magnitude,
            "role":      _CT_ROLES[role_key] if role_key else "",
        }

    enriched_paths: dict[str, dict] = {
        p.pathway: {
            "delta":     p.deviation_from_baseline,
            "direction": p.direction,
            "n_active":  p.n_active_genes,
            "n_total":   p.n_total_genes,
        }
        for p in triaged["pathways"]
    }

    return {
        "clusters":  clusters,
        "genes":     enriched_genes,
        "cts":       enriched_cts,
        "pathways":  enriched_paths,
        "fetal":     triaged["fetal"],
        "score":     triaged["score"],
    }


# ── 4. Build user prompt ───────────────────────────────────────────────────

def _build_user_prompt(sample_id: str, enriched: dict, report: DeviationReport) -> str:
    lines = [
        f"Sample ID: {sample_id}",
        f"Overall deviation score: {enriched['score']:.3f}",
        f"Healthy reference: {report.healthy_reference_cells:,} cells / "
        f"{report.healthy_reference_donors} donors",
        "",
    ]

    if enriched["genes"]:
        lines.append("GENE DEVIATIONS (ranked by |Z|):")
        for gene, info in enriched["genes"].items():
            role = f"  [{info['role']}]" if info["role"] else ""
            lines.append(
                f"  {gene}: Z={info['z_score']:+.2f} ({info['magnitude']} {info['direction']}){role}"
            )
        lines.append("")

    if enriched["cts"]:
        lines.append("CELL TYPE DEVIATIONS (ranked by |Z|):")
        for ct, info in enriched["cts"].items():
            role = f"  [{info['role']}]" if info["role"] else ""
            lines.append(
                f"  {ct}: Z={info['z_score']:+.2f} ({info['magnitude']} {info['direction']}){role}"
            )
        lines.append("")

    if enriched["pathways"]:
        lines.append("PATHWAY DEVIATIONS (vs. healthy baseline):")
        for pw, info in enriched["pathways"].items():
            delta = info["delta"]
            delta_str = f"{delta:+.3f}" if delta is not None else "N/A"
            lines.append(
                f"  {pw}: Δ={delta_str} log1p CP10K ({info['direction']}, "
                f"{info['n_active']}/{info['n_total']} genes active)"
            )
        lines.append("")

    fetal = enriched["fetal"]
    if fetal is not None:
        lines.append(f"FETAL REACTIVATION SCORE: {fetal.score:.3f}")
        if fetal.top_reactivated_genes:
            lines.append(f"  Top reactivated genes: {', '.join(fetal.top_reactivated_genes[:5])}")
        lines.append("")

    if enriched["clusters"]:
        lines.append("DETECTED BIOLOGICAL PROCESS CLUSTERS:")
        for c in enriched["clusters"]:
            dims = []
            if c["matched_genes"]: dims.append(f"genes: {', '.join(c['matched_genes'])}")
            if c["matched_cts"]:   dims.append(f"cell types: {', '.join(c['matched_cts'])}")
            if c["matched_pws"]:   dims.append(f"pathways: {', '.join(c['matched_pws'])}")
            label = c["process"].replace("_", " ").title()
            lines.append(f"  {label} — {'; '.join(dims)}")
        lines.append("")

    lines.append("Please interpret these findings following the step-by-step protocol.")
    return "\n".join(lines)


# ── 5. Parse structured fields from free-text response ────────────────────
# All extractions are best-effort. full_reasoning is always the authoritative record.

_STAGE_RE          = re.compile(r'\b(INITIATING|ACTIVE|ESTABLISHED|RESOLVING)\b')
_CONF_RE           = re.compile(r'Confidence:\s*(HIGH|MODERATE|LOW)', re.IGNORECASE)
_FINAL_SECTION_RE  = re.compile(
    r'FINAL INTERPRETATION\s*\n(.*?)(?=\n⚠|\Z)', re.DOTALL | re.IGNORECASE
)
_ANOMALOUS_ITEM_RE = re.compile(
    r'[•\-]\s+(.+?)\s+[—\-]+\s+ANOMALOUS', re.IGNORECASE
)
_ANOMALOUS_HDR_RE  = re.compile(
    r'ANOMALOUS\s+finding[s]?:\s*\n\s+(.+)', re.IGNORECASE
)


def _parse_response(text: str) -> dict:
    # Stage: last occurrence in the text is Part C's stage assignment
    stage_matches = _STAGE_RE.findall(text)
    stage = stage_matches[-1] if stage_matches else None

    # Final interpretation section
    final_m    = _FINAL_SECTION_RE.search(text)
    final_text = final_m.group(1).strip() if final_m else ""

    # Overall confidence from the Final Interpretation section
    conf_m             = _CONF_RE.search(final_text)
    overall_confidence = conf_m.group(1).upper() if conf_m else None

    # Anomalous findings — two formats: bullet list and explicit header
    anomalous = _ANOMALOUS_ITEM_RE.findall(text) + _ANOMALOUS_HDR_RE.findall(text)
    anomalous = [a.strip() for a in anomalous if a.strip()]

    # Biological question — last sentence of the final interpretation
    bio_q = ""
    if final_text:
        sentences = re.split(r'(?<=[.?])\s+', final_text.replace("\n", " ").strip())
        last = sentences[-1].strip()
        if last:
            bio_q = last if last.endswith("?") else last + "?"

    return {
        "stage":                stage,
        "overall_confidence":   overall_confidence,
        "anomalous_findings":   anomalous,
        "final_interpretation": final_text,
        "biological_question":  bio_q,
    }


# ── 6. Main entry point ────────────────────────────────────────────────────

def interpret(report: DeviationReport) -> BiologicalInterpretation:
    """
    Run the full reasoning pipeline on a DeviationReport.

    Raises:
        RuntimeError  — ANTHROPIC_API_KEY not set, or anthropic package missing
    """
    if not settings.ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not configured. "
            "Set it in your .env file or as an environment variable."
        )

    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            "The 'anthropic' package is not installed. Run: pip install anthropic"
        )

    triaged  = _triage(report)
    clusters = _cluster(triaged)
    enriched = _enrich(clusters, triaged)
    user_msg = _build_user_prompt(report.sample_id, enriched, report)

    logger.info(
        "Calling %s for sample '%s' (score=%.3f, genes=%d, cts=%d, pathways=%d)",
        MODEL_ID, report.sample_id, report.overall_deviation_score,
        len(triaged["genes"]), len(triaged["cts"]), len(triaged["pathways"]),
    )

    client  = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model    = MODEL_ID,
        max_tokens = MAX_TOKENS,
        system   = SYSTEM_PROMPT,
        messages = [{"role": "user", "content": user_msg}],
    )
    full_text = message.content[0].text

    parsed = _parse_response(full_text)

    return BiologicalInterpretation(
        sample_id               = report.sample_id,
        interpreted_at          = datetime.now(timezone.utc),
        model_id                = MODEL_ID,
        prompt_version          = PROMPT_VERSION,
        overall_deviation_score = report.overall_deviation_score,
        stage                   = parsed["stage"],
        overall_confidence      = parsed["overall_confidence"],
        anomalous_findings      = parsed["anomalous_findings"],
        final_interpretation    = parsed["final_interpretation"],
        biological_question     = parsed["biological_question"],
        full_reasoning          = full_text,
        safety_disclaimer       = SAFETY_DISCLAIMER,
    )
