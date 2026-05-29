# HEALTH — Lung Intelligence System

> AI-powered respiratory disease detection and management built on the world's largest human lung single-cell atlas.

---

## What it does

HEALTH analyses a patient's gene expression profile and either:

- **Identifies a known disease** — returns the disease name, ICD-10 code, affected cell types, pathophysiology, symptoms, treatments, and prognosis.
- **Flags a novel/unknown disease** — characterises the unusual gene pattern, hypothesises the biological mechanism, and — for certified research labs — suggests molecular drug design targets.

The system is built on the **Human Lung Cell Atlas (HLCA)**: 2,282,447 human lung cells across 16 disease states, 55,329 genes. It is the largest integrated single-cell lung dataset in existence.

---

## Safety

This system is a **research and clinical decision-support tool**. It does not replace medical diagnosis.

- Every disease result carries a mandatory `safety_disclaimer`.
- Drug design suggestions carry a `research_disclaimer` and are gated to certified research laboratory use only.
- No result should be acted on without review by a qualified medical professional.

---

## Quick start

```bash
# 1. Clone the repository
git clone <repo-url>
cd HEALTH

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Download datasets — see Data section below
python scripts/download_data.py --dataset hlca_core   # start small (5.5 GB)

# 4. Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Open the interactive API explorer
#    http://localhost:8000/docs
```

---

## API — all endpoints

### System

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Root — system name, version, links |
| `GET` | `/api/v1/health` | Health check — status, dataset counts |
| `GET` | `/docs` | Swagger UI — try every endpoint interactively |
| `GET` | `/redoc` | ReDoc — clean API reference |

### Data management

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/data/catalog` | Full catalog of all 17 datasets |
| `GET` | `/api/v1/data/catalog/{id}` | Info + status for one dataset |
| `GET` | `/api/v1/data/present` | Datasets already on disk |
| `GET` | `/api/v1/data/missing` | Datasets not yet downloaded |

### Atlas analysis (requires dataset files)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/analysis/loaded` | Datasets currently in memory |
| `GET` | `/api/v1/analysis/{id}/overview` | Cell counts, gene count, disease distribution |
| `GET` | `/api/v1/analysis/{id}/cell-types` | Full cell type distribution |
| `GET` | `/api/v1/analysis/{id}/diseases` | Full disease label distribution |
| `GET` | `/api/v1/analysis/{id}/metadata` | All metadata columns with types and top values |
| `POST` | `/api/v1/analysis/{id}/genes` | Expression stats for a list of gene names |
| `DELETE` | `/api/v1/analysis/{id}/unload` | Free dataset from memory |

### Disease detection (no dataset file required)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/disease/detect` | **Core endpoint** — detect disease from gene expression |
| `GET` | `/api/v1/disease/list` | All 16 detectable diseases |
| `GET` | `/api/v1/disease/{key}` | Full clinical profile for one disease |
| `GET` | `/api/v1/disease/{key}/markers` | Gene markers + weights used for detection |

### Research endpoints — certified laboratory use only

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/disease/research/drug-targets` | Drug design suggestions from gene expression |
| `POST` | `/api/v1/disease/research/repositioning` | Approved drugs that could be repositioned |

---

## Disease detection — how to use it

Submit a patient's gene expression profile as a JSON body:

```json
POST /api/v1/disease/detect
{
  "sample_id": "patient_001",
  "gene_expression": {
    "MX1": 9.2,
    "ISG15": 9.5,
    "IFI44L": 8.8,
    "IFIT1": 9.0,
    "CXCL10": 8.0,
    "ACE2": 5.5,
    "SFTPC": 1.5
  },
  "patient_metadata": {
    "age": 52,
    "sex": "male",
    "smoking_status": "never"
  }
}
```

**Gene expression values** must be log-normalised: `log1p(counts / total_counts × 10,000)`.
This is the standard output of tools like Seurat, Scanpy, and Cell Ranger.

**Minimum**: 50 genes. **Recommended**: 500–2,000 genes for accurate classification.

### Example response — known disease

```json
{
  "sample_id": "patient_001",
  "category": "known",
  "confidence": 0.71,
  "disease_name": "COVID-19 (SARS-CoV-2 infection)",
  "disease_details": {
    "icd_code": "U07.1",
    "category": "Viral respiratory infection",
    "affected_cell_types": [
      "Pulmonary alveolar type 2 cells (primary viral entry via ACE2)",
      "Alveolar macrophages (hyperactivated)",
      ...
    ],
    "pathophysiology": "SARS-CoV-2 binds ACE2 receptors on AT2 cells...",
    "symptoms": ["Fever", "Dry cough", "Dyspnoea", "Loss of smell", ...],
    "current_treatments": [
      "Antivirals: Nirmatrelvir/ritonavir (Paxlovid), Remdesivir",
      "Anti-inflammatory: Dexamethasone (severe/ICU)",
      ...
    ],
    "prognosis": "Highly variable. Mild: full recovery in 1–2 weeks..."
  },
  "top_expressed_genes": ["ISG15", "MX1", "IFIT1", "IFI44L", ...],
  "safety_disclaimer": "This analysis is intended to assist qualified medical professionals..."
}
```

### Example response — novel disease

```json
{
  "sample_id": "novel_patient",
  "category": "unknown",
  "confidence": 0.91,
  "anomaly_score": 0.91,
  "novel_characteristics": [
    "Strongly elevated genes vs. healthy baseline: ZEB1, SNAI1, AURKB...",
    "Significantly suppressed: SFTPC (-7.3), AGER (-5.9), FOXJ1 (-4.6)"
  ],
  "possible_mechanisms": [
    "Epithelial-Mesenchymal Transition (EMT) signature...",
    "High proliferative activity — cell-cycle markers elevated..."
  ],
  "drug_design_suggestions": {
    "target_genes": ["ZEB1", "ZEB2", "SNAI1", "CDK4", "AURKB"],
    "target_pathways": ["EMT (4 markers)", "Cell Cycle (3 markers)"],
    "drug_modality": [
      "ZEB1/ZEB2 PROTAC degrader",
      "CDK4/6 ATP-competitive inhibitor"
    ],
    "research_disclaimer": "RESEARCH USE ONLY — NOT FOR CLINICAL APPLICATION..."
  },
  "safety_disclaimer": "..."
}
```

---

## Data

All dataset files are stored in `data/` (gitignored — files are too large for git).

### Download datasets

```bash
# Download one dataset
python scripts/download_data.py --dataset hlca_core

# Download multiple
python scripts/download_data.py --dataset hlca_full hlca_embeddings

# Download all (warning: ~63 GB total)
python scripts/download_data.py --all

# List all available datasets without downloading
python scripts/download_data.py --list
```

### Dataset catalog

| ID | Name | Cells | Size | Priority |
|----|------|-------|------|----------|
| `hlca_full` | HLCA Full — 16 diseases | 2.28M | 20 GB | ★★★ Primary reference |
| `hlca_embeddings` | HLCA Pre-computed Embeddings | 2.28M | 2.2 GB | ★★★ Nearest-neighbour search |
| `hlca_core` | HLCA Core — quality subset | 585K | 5.5 GB | ★★ Training |
| `fetal_lung` | Fetal Lung Atlas | 72K | 1.6 GB | ★★ Developmental baseline |
| `myeloid_cells` | Macrophages, Monocytes | 41K | 455 MB | ★ Immune focus |
| `airway_epithelial` | Airway Epithelial Cells | 30K | 421 MB | ★ Airway focus |
| `lymphoid_cells` | T cells, NK cells | 38K | 134 MB | ★ Immune focus |
| `fibroblasts` | Fibroblasts | 21K | 229 MB | ★ Fibrosis focus |
| `vascular_endothelial` | Blood vessel cells | 21K | 183 MB | ★ Vascular focus |
| `smooth_muscle` | Smooth muscle cells | 5K | 48 MB | ★ LAM/asthma focus |
| `b_cells` | B cells | 4K | 34 MB | ★ Humoral immunity |
| `visium_bronchus` | Spatial — bronchus | 5K spots | 695 MB | ★ Spatial context |
| `visium_parenchyma` | Spatial — parenchyma | 5K spots | 831 MB | ★ Spatial context |
| `fetal_visium` | Fetal spatial | 23K spots | 1.5 GB | ★ Development |
| `fetal_atac` | Fetal ATAC-seq | 101K | 27 GB | ★ Regulatory |
| `all_cells_nuclei` | Combined cells+nuclei | 193K | 1.9 GB | ★★ Complete view |
| `hlca_gene_order` | Gene order CSV (2,000 genes) | — | 44 KB | ★★★ Model input format |

> The disease detection endpoints work **without any downloaded files** — they use a curated gene signature database built into the application.
> Dataset files are only needed for the `/api/v1/analysis/` endpoints.

---

## Architecture

```
HEALTH/
├── app/
│   ├── main.py                      ← FastAPI app, CORS, global error handlers
│   ├── core/
│   │   ├── config.py                ← All settings + 17-dataset catalog with URLs
│   │   └── exceptions.py            ← Custom exception hierarchy
│   ├── models/
│   │   └── schemas.py               ← All Pydantic request/response schemas
│   ├── services/
│   │   ├── downloader.py            ← Dataset catalog queries + on-disk status
│   │   ├── atlas_service.py         ← Loads .h5ad files (backed='r'); singleton cache
│   │   ├── disease_knowledge.py     ← Curated gene signatures + clinical DB (16 diseases)
│   │   ├── disease_service.py       ← Scoring engine, confidence, novelty detection
│   │   └── drug_design_service.py   ← Pathway detection + drug target recommendations
│   └── api/v1/
│       ├── router.py                ← Aggregates all route groups
│       ├── health.py                ← GET /health
│       ├── data.py                  ← GET /data/*
│       ├── analysis.py              ← GET+POST /analysis/*
│       └── disease.py               ← POST /disease/* (detection + research)
├── scripts/
│   └── download_data.py             ← CLI downloader for all datasets
├── notebooks/
│   └── 01_load_hlca_full.ipynb      ← Colab notebook — download + explore data
├── data/                            ← .h5ad files (gitignored, ~63 GB total)
├── models/                          ← ML model files (gitignored)
├── requirements.txt
├── .env.example                     ← Environment variable reference
└── CLAUDE.md                        ← Developer reference (full technical docs)
```

### Key design decisions

**Why `backed='r'` for .h5ad files?**
The HLCA Full is 20 GB. Loading it fully into RAM would crash most machines.
`backed='r'` keeps the expression matrix on disk and reads only the slices you request.
The metadata table (`obs`) — patient labels, disease names — loads into RAM (~500 MB).

**Why a curated gene signature database?**
The `/disease/detect` endpoint works immediately, without downloading any files.
Researchers can start testing against the system the moment they clone the repo.
The database is fully auditable — every marker gene has a published biological rationale.

**Why define all schemas upfront (Phase 1–5)?**
The schema file is the API contract. Defining it upfront means frontend teams can build against it today, and schema changes are deliberate, not accidental.

**Why custom exceptions?**
Services should not know they are running inside an HTTP server. A service raises `DatasetNotFoundError`; the HTTP layer converts it to a 404. This keeps services reusable in notebooks and CLI scripts.

---

## Diseases the system can detect

| Disease | ICD-10 | Key markers |
|---------|--------|-------------|
| Normal (healthy) | — | SFTPC, SFTPB, AGER, SCGB1A1 |
| COVID-19 | U07.1 | MX1, ISG15, IFI44L, IFIT1, ACE2, CXCL10 |
| Pulmonary Fibrosis (IPF) | J84.112 | COL1A1, SPP1, MMP7, POSTN, MUC5B |
| Lung Adenocarcinoma | C34.1 | NAPSA, NKX2-1, MKI67, EGFR |
| Squamous Cell Carcinoma | C34.9 | TP63, KRT5, SOX2, MKI67 |
| COPD | J44.1 | MMP12, MARCO, CXCL8, SERPINA1 |
| Pneumonia | J18.9 | S100A8, S100A9, MMP8, CXCL8 |
| Cystic Fibrosis | J84.0 | MUC5AC, MUC5B, SPDEF, CFTR |
| Pulmonary Sarcoidosis | D86.0 | ACE, CXCL10, CCL18, SPP1 |
| LAM | J84.81 | PMEL, VEGFD, ACTA2, TSC2 |
| Interstitial Lung Disease | J84.1 | COL1A1, CCL18, MMP7 |
| Hypersensitivity Pneumonitis | J67.9 | CD3D, IL17A, CXCL10, CCL18 |
| NSIP | J84.113 | COL1A1, CXCL10, FOXM1 |
| Chronic Rhinitis | J31.0 | IL4, IL13, MUC5AC, TSLP |
| Pleomorphic Carcinoma | C34.90 | VIM, CDH2, MKI67, MMP9 |
| Large Cell Carcinoma | C34.90 | MKI67, TOP2A, SMARCA4, CDK4 |

---

## Drug design pathways (research only)

When a novel disease is detected, the system identifies activated biological pathways
and suggests drug targets. Eight pathways are currently covered:

| Pathway | Trigger genes | Top drug approach |
|---------|--------------|-------------------|
| JAK-STAT / Type I IFN | MX1, ISG15, IFIT1, OAS1 | JAK1/2 inhibitor (Ruxolitinib-like) |
| TGF-β / Fibrotic | COL1A1, ACTA2, POSTN, SPP1 | TGFBR1 inhibitor / anti-TGF-β mAb |
| NF-κB / Cytokine storm | IL6, TNF, IL1B, CXCL8 | IKKβ inhibitor / anti-IL-6R mAb |
| Cell cycle / Proliferation | MKI67, TOP2A, CDK4, BIRC5 | CDK4/6 inhibitor (Palbociclib-like) |
| mTOR / TSC | VEGFD, PMEL, RPS6KB1 | mTORC1 rapalog (Sirolimus-like) |
| Type 2 / Allergic | IL4, IL13, IL33, TSLP | Anti-IL-4Rα mAb (Dupilumab-like) |
| Protease / MMP | MMP12, ELANE, MMP9 | Selective MMP12 / ELANE inhibitor |
| EMT | ZEB1, SNAI1, VIM, CDH2 | ZEB1/2 PROTAC degrader |

---

## Environment variables

Copy `.env.example` to `.env` and modify as needed:

```env
# Set to true to enable debug logging
DEBUG=false

# Override default data directory (default: ./data)
DATA_DIR=/path/to/large/disk/data

# Override default models directory (default: ./models)
MODELS_DIR=/path/to/models
```

---

## Build roadmap

| Phase | Status | What it adds |
|-------|--------|-------------|
| 1 — Foundation | ✅ Complete | Config, schemas, catalog, health + data endpoints |
| 2 — Data layer | ✅ Complete | Safe .h5ad loading, atlas exploration endpoints |
| 3 — Disease detection | ✅ Complete | 16-disease scoring engine, full clinical profiles |
| 4 — Novel characterisation | ✅ Complete | Anomaly scoring, pathway inference, differential expression |
| 5 — Drug design | ✅ Complete | 8-pathway drug target engine, repositioning candidates |
| 6 — scVI integration | Planned | Nearest-neighbour cell search using HLCA reference model |
| 7 — Spatial analysis | Planned | Visium spatial gene expression mapping |
| 8 — Population analytics | Planned | Cross-donor, multi-study disease comparison |

---

## Adding a new detectable disease

1. Add a `DiseaseSignature` entry to `app/services/disease_knowledge.py → DISEASE_DB`
2. Include: `markers` (gene → weight), `suppressors`, and all `clinical` fields
3. The detection endpoint picks it up automatically — no other changes needed

## Adding a new drug design pathway

1. Add a `PathwayEntry` to `app/services/drug_design_service.py → PATHWAY_LIBRARY`
2. Include: `trigger_genes`, `min_triggers`, `threshold`, targets, modalities, rationale
3. The pathway engine picks it up automatically

---

## Contributing

See [CLAUDE.md](CLAUDE.md) for the full technical developer reference — architecture decisions, file-by-file descriptions, and the adding-a-new-endpoint checklist.
