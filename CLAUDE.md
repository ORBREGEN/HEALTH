# HEALTH — Respiratory Intelligence Platform
## Developer Reference · Single Source of Truth

Read this entirely before touching any code. Every decision made in this codebase traces back to the mission described here.

---

## Mission

HEALTH is a platform built on one foundational insight: **if a system deeply understands what a healthy human respiratory system looks like at the cellular level, it can detect anything that deviates from that — and eventually guide the correction of it.**

The platform serves four interconnected groups at four layers:

---

## The Four Layers

### Layer 1 — Patient Portal (public)
**Who uses it:** Any citizen. No medical background required.

A patient describes their symptoms, history, and concerns. The platform matches them with the most suitable respiratory specialist for their specific situation — not a generic referral, but a match based on the type of deviation their presentation suggests.

This is what the public sees. This is the face of HEALTH.

The intelligence that powers the matching comes from Layers 2 and 3.

### Layer 2 — Respiratory Intelligence Engine (the model)
**Who uses it first:** Research laboratories. Then powers Layer 1.

A biological model built from the Human Lung Cell Atlas — 2.28 million human lung cells across donors, tissues, and conditions. The model learns what a healthy respiratory system looks like at every level:
- Which cell types are present, in what proportions
- What genes are expressed in each cell type and at what levels
- How these distributions vary across age, sex, and donors
- What spatial organisation looks like across tissue regions

When given a new sample, the model compares it against this healthy reference and describes every deviation: which cell populations are expanded or depleted, which genes are outside their normal range, which biological processes are dysregulated.

**The model does not name diseases. It characterises biology.**

Diseases emerge from the pattern. The model provides the foundation for that reasoning — but the naming and clinical judgment belong to the expert in Layer 3.

### Layer 3 — Expert Network (feedback loop)
**Who uses it:** Certified respiratory physicians and researchers.

Experts interact with the model's findings. They confirm deviations, add clinical context, correct errors, and contribute annotated cases back to the training data. Each expert interaction makes the model more accurate and more specific.

This is the flywheel: better model → better patient matching → more expert engagement → better model.

### Layer 4 — Treatment Intelligence (the end goal)
**Who uses it:** Clinicians, researchers, drug developers.

Because the model knows what healthy looks like and can precisely describe what broke down, it can reason about how to reverse the breakdown. This layer generates:
- Evidence-based treatment guidelines grounded in the biological deviation, not generic protocols
- Drug design directions when the mechanism is novel or untreatable by known drugs
- Pathway-targeted intervention suggestions, ranked by target quality and evidence

This layer is powered by Layers 2 and 3 being sufficiently mature. It does not exist yet. It is the destination.

---

## Data Foundation

Everything the model knows comes from real human cells. No hardcoded knowledge. No curated signatures. The statistics are computed from the data.

### Datasets collected (stored in `data/`, gitignored — large files)

| File | Cells/Spots | Genes | Type | Role |
|---|---|---|---|---|
| `hlca_full.h5ad` | 2,282,447 | 55,329 | scRNA | Master reference — all cell types, 16 conditions |
| `hlca_core.h5ad` | 584,944 | 27,402 | scRNA | High-quality annotated training subset |
| `lung_hlca_full_v1.1_emb.h5ad` | 2,282,447 | 30 | Embeddings | Pre-computed HLCA vectors for fast similarity |
| `lung_cells_all_nuclei.h5ad` | 193,108 | 32,383 | snRNA | Nucleus-resolved single-cell |
| `lung_fetal_atac.h5ad` | 100,940 | 45,107 | ATAC | Chromatin accessibility, fetal lung |
| `lung_fetal_assembled_10domains.h5ad` | 71,752 | 26,568 | scRNA | Fetal development baseline |
| `lung_tissues_myeloid_cells.h5ad` | 40,634 | 32,383 | scRNA | Myeloid immune compartment |
| `lung_tissues_lymphoid_cells.h5ad` | 37,502 | 32,383 | scRNA | Lymphoid immune compartment |
| `lung_tissues_airway_epithelial_cells.h5ad` | 29,505 | 32,383 | scRNA | Airway epithelial layer |
| `lung_tissues_vascular_endothelial_cells.h5ad` | 20,855 | 32,383 | scRNA | Vasculature |
| `lung_tissues_fibroblasts.h5ad` | 20,515 | 32,383 | scRNA | Stromal fibroblasts |
| `lung_fetal_visium_annotated.h5ad` | 22,883 | 33,538 | Spatial | Fetal spatial expression |
| `lung_tissues_smooth_muscle_cells.h5ad` | 5,156 | 32,383 | scRNA | Smooth muscle |
| `lung_tissues_visium_bronchus.h5ad` | 4,992 | 32,397 | Spatial | Bronchus spatial expression |
| `lung_tissues_visium_parenchyma.h5ad` | 4,992 | 32,397 | Spatial | Parenchyma spatial expression |
| `lung_tissues_b_cells.h5ad` | 3,699 | 32,383 | scRNA | B cell compartment |
| `HLCA_reference_model_extracted/` | — | — | scVI | Pre-trained HLCA scVI model |
| `HLCA_surgery_models_extracted/` | — | — | scVI | Surgery-specific HLCA models |
| `hlca_gene_order_ids_and_symbols.csv` | — | 2,000 | CSV | Gene ID ↔ symbol mapping |
| `lung_core_atlas_extracted/` | — | — | Atlas | uniLUNG Core Atlas |

### Key fields in HLCA Full metadata
```
cell_type, disease, donor_id, tissue, sex, development_stage
BMI, age_or_mean_of_age_range, smoking_status, cause_of_death
ann_level_1..5, ann_finest_level        ← 5 levels of cell type granularity
tissue_level_2, tissue_level_3          ← anatomical region
assay, sequencing_platform
```

### Disease states present in HLCA Full (16 total)
`normal` · `pulmonary fibrosis` · `squamous cell lung carcinoma` · `COVID-19` ·
`lung adenocarcinoma` · `COPD` · `pulmonary sarcoidosis` · `pneumonia` ·
`lymphangioleiomyomatosis` · `interstitial lung disease` · `cystic fibrosis` ·
`chronic rhinitis` · `pleomorphic carcinoma` · `lung large cell carcinoma` ·
`hypersensitivity pneumonitis` · `non-specific interstitial pneumonia`

The model is built **only from `disease == 'normal'`** cells. Disease cells are reserved for validation and expert training data.

---

## Technology Stack

| Component | Technology |
|---|---|
| API server | FastAPI + uvicorn |
| Data validation | Pydantic v2 |
| Single-cell data | scanpy + anndata |
| Pre-trained model | scVI (HLCA reference model) |
| Runtime | Python 3.10 |
| Frontend | Next.js 14 (App Router) |
| Database (future) | PostgreSQL — expert annotations, patient records |

---

## Project Layout

```
HEALTH/
├── app/                           ← FastAPI backend
│   ├── main.py                    ← Entry point
│   ├── core/
│   │   ├── config.py              ← All paths and settings
│   │   └── exceptions.py         ← Custom exception types
│   ├── models/
│   │   └── schemas.py             ← All Pydantic schemas
│   ├── services/
│   │   ├── respiratory_model.py   ← Build + serve the Healthy Respiratory Model
│   │   ├── anomaly_detector.py    ← Compare samples against healthy reference
│   │   └── expert_service.py      ← Expert annotation ingestion
│   └── api/
│       └── v1/
│           ├── router.py
│           ├── system.py          ← Health check
│           ├── model.py           ← Layer 2 — model status + analysis
│           ├── patient.py         ← Layer 1 — patient intake + matching
│           └── expert.py          ← Layer 3 — expert feedback endpoints
├── ui/                            ← Next.js frontend
│   ├── app/
│   │   ├── (public)/              ← Layer 1: patient-facing pages
│   │   └── (platform)/            ← Layer 2/3: research + expert platform
├── data/                          ← .h5ad files (gitignored, large)
├── models/                        ← Trained model artefacts (gitignored)
├── notebooks/                     ← Exploratory work
│   └── 01_load_hlca_full.ipynb    ← Data collection + initial exploration
├── scripts/                       ← One-off data processing scripts
├── requirements.txt
└── CLAUDE.md                      ← This file
```

---

## Build Sequence

### Phase 1 — Respiratory Intelligence Engine (Layer 2, research use) ← CURRENT
Build the model. Validate it. Expose it via API for lab use.

- [ ] `app/` structure + FastAPI skeleton
- [ ] `services/respiratory_model.py` — build healthy reference model from HLCA normal cells
  - Per-cell-type: mean expression, std, percentiles for every gene
  - Cell type composition: expected fractions per donor ± std
  - Spatial context from Visium data
  - Uses `hlca_full.h5ad` filtered to `disease == 'normal'`
- [ ] `services/anomaly_detector.py` — compare a sample against the healthy model
  - Cell type deviation Z-scores
  - Gene-level deviation Z-scores
  - Biological pathway activation
- [ ] API: `POST /api/v1/model/build`, `GET /api/v1/model/status`, `POST /api/v1/analyse`
- [ ] `ui/` minimal: landing page + analysis interface for lab use

### Phase 2 — Patient Portal (Layer 1, public)
- [ ] Patient intake form: symptoms, duration, history, location
- [ ] Specialist matching logic: map symptom + deviation pattern → specialist type
- [ ] Expert directory: respiratory specialists with their specialty focus
- [ ] `ui/(public)` patient-facing interface

### Phase 3 — Expert Network (Layer 3)
- [ ] Expert login + case review interface
- [ ] Annotation workflow: expert reviews model output, confirms/corrects
- [ ] Data contribution: expert-annotated cases fed back to model
- [ ] `ui/(platform)/expert` interface

### Phase 4 — Treatment Intelligence (Layer 4)
- [ ] Given healthy reference + deviation profile → reason about reversal
- [ ] Treatment guideline generation grounded in specific deviations
- [ ] Novel mechanism characterisation for unknown patterns
- [ ] Drug design directions (research only)

---

## Hard Rules

1. **The model learns from data. Nothing biological is hardcoded.** No curated gene lists, no manually written disease signatures. Every reference statistic comes from the HLCA cells.

2. **The model describes biology. Experts name diseases.** The API returns deviations, Z-scores, and pathway states. It does not return disease names. That judgment belongs to a clinician.

3. **Layer 1 is built on top of Layer 2.** Patient matching is only as good as the underlying model. Do not rush the patient interface at the expense of model quality.

4. **Every output carries a safety disclaimer.** It is part of the schema, not an optional string.

5. **backed='r' for all .h5ad files.** The HLCA Full is 20 GB. Never load it fully into RAM.

---

## Running the Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API docs
# http://localhost:8000/docs
# http://localhost:8000/api/v1/system/health
```

## Running the Frontend

```bash
cd ui
npm install
npm run dev
# http://localhost:3000
```

---

## Environment Variables

```env
DEBUG=true
DATA_DIR=./data
MODELS_DIR=./models
```
