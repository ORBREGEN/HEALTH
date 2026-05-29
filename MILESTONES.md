# Senebiclabs — Milestones & Progress Log

Last updated: 2026-05-26

---

## What Senebiclabs Is

A biological intelligence platform built on one foundational insight:
**if a system deeply understands what a healthy human lung looks like at the cellular level,
it can detect anything that deviates from that — and eventually guide the correction of it.**

The platform has four layers. Layers 2 is complete. Layers 1, 3, and 4 are in progress.

---

## ✅ Milestone 1 — Data Foundation

**Completed:** May 2026

The model is built entirely from real human cells. No hardcoded rules. No curated gene lists.
Every reference statistic is computed from data.

**What was collected:**

| Dataset | Cells / Spots | Type | Role |
|---|---|---|---|
| HLCA Full | 2,282,447 | scRNA-seq | Master reference — 16 disease conditions |
| HLCA Core | 584,944 | scRNA-seq | High-quality annotated training subset |
| HLCA Embeddings | 2,282,447 | scVI vectors | Pre-computed similarity vectors |
| Single nuclei (lung) | 193,108 | snRNA-seq | Nucleus-resolved cell data |
| Fetal ATAC | 100,940 | ATAC-seq | Chromatin accessibility — fetal lung |
| Fetal assembled | 71,752 | scRNA-seq | Fetal development baseline |
| Myeloid immune cells | 40,634 | scRNA-seq | Innate immune compartment |
| Lymphoid immune cells | 37,502 | scRNA-seq | Adaptive immune compartment |
| Airway epithelial cells | 29,505 | scRNA-seq | Airway epithelial layer |
| Vascular endothelial | 20,855 | scRNA-seq | Vasculature |
| Fibroblasts | 20,515 | scRNA-seq | Stromal / fibrotic compartment |
| Fetal Visium (spatial) | 22,883 | Spatial | Fetal lung — 10 annotated domains |
| Smooth muscle cells | 5,156 | scRNA-seq | Airway smooth muscle |
| Visium bronchus | 4,992 | Spatial | Adult airway tissue |
| Visium parenchyma | 4,992 | Spatial | Adult alveolar tissue |
| B cells | 3,699 | scRNA-seq | B cell compartment |

**Model trained on:** `disease == 'normal'` cells only — 1,305,099 healthy cells across 268 donors.
Disease cells are reserved for validation.

---

## ✅ Milestone 2 — Healthy Respiratory Model (Layer 2 Core)

**Completed:** May 2026

Built the reference model — what a healthy lung looks like at the cellular level.

**What the model knows:**
- **9,838 genes** tracked with per-gene healthy baselines (mean, std, p5, p95)
- **60 cell types** with expected proportions (mean fraction ± std per donor)
- **12 biological pathways** with healthy baseline expression levels
- **268 donors** — the reference reflects real human variation, not a single idealised sample

**How it was built:**
- Filtered HLCA Full to `disease == 'normal'`
- Computed per-gene statistics across all healthy cells
- Computed per-cell-type composition fractions per donor (mean ± std)
- Built cell-type-specific gene profiles (marker genes + their CT-level baselines)
- Defined 12 pathway baselines from real gene expression (not curated gene sets)

---

## ✅ Milestone 3 — Deviation Detection Engine (Layer 2 Analysis)

**Completed:** May 2026

Given any gene expression sample, the engine compares it against the healthy reference
and produces a structured report across **six biological dimensions**.

### Dimension 1 — Cell Type Composition
- Estimates the fraction of each cell type present in the sample
- Computes Z-scores against healthy donor distribution
- Flags cell types as **expanded**, **depleted**, or **normal**
- 60 cell types scored; surface only those present at meaningful levels in healthy tissue

### Dimension 2 — Gene-Level Deviations
- For every gene in the sample, computes Z-score against healthy mean ± std
- Reports genes with |Z| ≥ 2.0 (configurable threshold)
- Returns top 100 deviated genes sorted by Z-score magnitude
- Classifies each as **elevated** or **suppressed**, with severity (mild / moderate / severe)

### Dimension 3 — Pathway Deviations
- 12 pathways with healthy baseline expression levels
- Compares sample's pathway gene expression to healthy baseline (not a fixed threshold)
- Flags pathways as **over-active** or **suppressed**
- Also detects suppressor gene loss (pathway disinhibition)

### Dimension 4 — Fetal Reactivation
- Measures whether the sample re-expresses developmental (fetal) gene programmes
- Score: 0.0 = adult-like, 1.0 = fetal-like
- Relevant for: dedifferentiation, oncogenic reprogramming, regenerative progenitor expansion
- Requires fetal reference artefact

### Dimension 5 — Cell Type Functional Impairment
- Uses cell-type-specific gene baselines (not global baselines)
- Detects cell types that are present but functionally impaired
- Example: AT2 cells present in normal proportion, but their signature genes suppressed
  - Global Z: −0.5 (missed)
  - AT2-specific Z: −5.8 (flagged correctly)

### Dimension 6 — Spatial Tissue Localisation ← NEW
- Compares deviated genes against Visium spatial baselines (bronchus + parenchyma)
- Answers: **WHERE in the lung is this deviation concentrated?**
- Classifies deviated genes as airway-dominant or alveolar-dominant
- Determines dominant tissue compartment: AIRWAY / ALVEOLAR / BOTH / UNKNOWN
- Returns plain-language clinical summary

**Example output for the same gene, before and after spatial context:**

| Without spatial | With spatial |
|---|---|
| "COL1A1 elevated (severe, Z=+6.2)" | "COL1A1 elevated — normally airway-dominant. Elevation consistent with airway fibrosis, not subpleural/alveolar." |
| "SFTPC suppressed (moderate, Z=−3.1)" | "SFTPC suppressed — alveolar gene. Suppression indicates AT2 cell dysfunction in the gas-exchange zone." |

**Spatial baselines built from:**
- Visium bronchus: 4,992 spots, 9,793 genes
- Visium parenchyma: 4,992 spots, 9,793 genes
- Visium fetal: 22,883 spots, 10 anatomical domains
- 200 tissue contrast genes (strongest bronchus/parenchyma differences)
- 17 clinical landmark genes mapped to their spatial location

---

## ✅ Milestone 4 — API (Layer 2 Endpoints)

**Completed:** May 2026

FastAPI server exposing the engine to the outside world.

**Endpoints:**

| Method | Path | What it does |
|---|---|---|
| GET | `/api/v1/model/status` | Model readiness, cell count, gene count, spatial flag |
| POST | `/api/v1/model/build` | Build or rebuild the healthy reference model |
| POST | `/api/v1/analyse` | Run a gene expression sample through the engine |
| POST | `/api/v1/interpret` | Chain-of-thought biological reasoning via Claude |
| POST | `/api/v1/patient/intake` | Patient symptom intake + specialist matching |
| POST | `/api/v1/expert/apply` | Expert application to join the network |
| POST | `/api/v1/waitlist` | Public waitlist signup |

**Every response carries a safety disclaimer.**
The engine does not name diseases. It characterises biology.

---

## ✅ Milestone 5 — Frontend (Senebiclabs.com)

**Completed:** May 2026

Next.js frontend with five public pages and one research tool.

**Public pages:**
- `/` — Landing page: mission, platform overview, waitlist signup
- `/about` — Full story: why we started, what we're building, principles
- `/patients` — Patient waitlist (Layer 1 coming soon)
- `/experts` — Specialist application form (Layer 3 coming soon)
- `/vision` — Long-term vision: what the platform becomes

**Research tool:**
- `/analyse` — Full analysis interface for lab use
  - Upload: CSV, TSV, TXT, XLSX — auto-detects format and separator
  - Multi-sample support: pick which column to analyse
  - Normalisation modes: log1p CP10K (default), raw counts, CP10K
  - Manual gene entry: add individual genes by name + value
  - Real-time model status indicator
  - Full deviation report: all 6 dimensions rendered
  - Download report as CSV
  - Chain-of-thought biological interpretation (when API key configured)

---

## ✅ Milestone 6 — Biological Reasoning Engine

**Completed:** May 2026

`POST /api/v1/interpret` — takes a deviation report and produces a structured
chain-of-thought biological interpretation using Claude.

**Output includes:**
- Step-by-step reasoning: Evidence → Patterns → Cross-validation → Mechanism → Implications
- Inferred biological process stage: INITIATING / ACTIVE / ESTABLISHED / RESOLVING
- Overall confidence: HIGH / MODERATE / LOW
- Most anomalous findings flagged
- Final interpretation (3–5 sentences with cited Z-scores)
- The single most important biological question raised by the profile

**Requires:** `ANTHROPIC_API_KEY` in `.env`

---

## ✅ Milestone 7 — Spatial Context in UI

**Completed:** May 2026

The sixth analysis dimension is now fully visible in the `/analyse` page.

**What was built:**
- Dominant tissue compartment badge (AIRWAY / ALVEOLAR / BOTH / UNKNOWN) with colour coding
- Tissue localisation summary sentence in plain language
- Two-column gene grid: airway signal genes (blue) vs alveolar signal genes (green)
- Per-gene spatial baseline table: bronchus baseline vs parenchyma baseline, clinical note per gene
- Text readability pass: all dim grey colours replaced with bright white, font sizes increased throughout report

---

## 🔲 Milestone 8 — Clinical Research Partnership (KEMRI)

**Status: Call pending**

Kenya Medical Research Institute — Centre for Respiratory Diseases Research (KEMRI-CRDR).
Focus: TB, COPD, asthma, bronchiectasis, post-TB lung disease.
Key contacts: Dr. Hellen Meme, Dr. Evans Amukoye.

**What we need from them:**
- Clinical validation of deviation reports against known disease cases
- Expert interpretation of what the model flags
- Eventually: access to patient samples for real-world testing

**What we offer:**
- A working analysis engine they can use for their research today
- A platform that can characterise biological deviations from healthy lung baseline
- Spatial context: where in the lung tissue the deviation is concentrated

**Call script:** ready. Call not yet made.

---

## 🔲 Milestone 9 — Patient Matching App (Layer 1)

**Status: Design phase**

A patient describes their symptoms. The platform matches them to the right specialist
for their specific biological situation — not a generic referral.

**Depends on:**
- Layer 2 being solid ✅
- Clinical partnership providing feedback on what deviations map to what specialist types
- Expert network (Layer 3) being partially populated

---

## 🔲 Milestone 10 — Expert Network (Layer 3)

**Status: Not started**

Certified respiratory physicians and researchers interact with the model's findings.
They confirm deviations, add clinical context, correct errors.
Their feedback makes the model more accurate over time.

**This is the flywheel:**
Better model → better patient matching → more expert engagement → better model.

---

## 🔲 Milestone 11 — Treatment Intelligence (Layer 4)

**Status: Not started — long-term**

Because the model knows what healthy looks like and can precisely describe what broke down,
it can reason about how to reverse the breakdown.

**Will produce:**
- Evidence-based treatment directions grounded in specific biological deviations
- Drug design directions when the mechanism is novel or untreatable by known drugs
- Pathway-targeted intervention suggestions, ranked by target quality and evidence

**Depends on:** Layers 2 and 3 being mature.

---

## Hard Rules (never change)

1. **The model learns from data. Nothing biological is hardcoded.**
2. **The model describes biology. Experts name diseases.**
3. **Layer 1 is built on top of Layer 2. Do not rush the patient interface.**
4. **Every output carries a safety disclaimer.**
5. **backed='r' for all .h5ad files. Never load the full HLCA into RAM.**
