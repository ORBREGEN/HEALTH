# Senebiclabs — Respiratory Intelligence

**A model of health, built from the cell up. Starting with the lung.**

> Connecting Patients, Intelligence, and Experts for Better Health Care.

Senebiclabs builds a model of what a *healthy* human respiratory system looks like at
the cellular level, precise enough that anything departing from it can be detected,
characterised, and eventually corrected. Instead of training a separate detector for
each disease, we model **health** and let disease reveal itself as a **deviation** from
it. The model is built only from healthy cells, so it carries no disease bias and can,
in principle, flag deviations it has never seen before.

**Live:** [senebiclabs.com](https://senebiclabs.com)

---

## Mission

Senebiclabs rests on one foundational insight: **if a system deeply understands what a
healthy human body looks like at the cellular level, it can detect anything that deviates
from it, known or novel, and eventually guide the correction of it.**

We are building toward a future where illness is recognised the moment the body departs
from health, and ultimately guided back to it. We start with the respiratory system, and
build toward the whole body.

---

## The idea

Medicine characterises the body mostly through disease, one trained detector at a time.
We invert it: build a precise, cellular-resolution model of health, and treat disease as
a measurable departure from it.

- The model **describes** the deviation (which cell populations and genes are off, which
  pathways are dysregulated).
- It does **not** name the disease. Naming and clinical judgment belong to a clinician.

---

## The platform (four layers)

1. **Patient portal** — a person describes symptoms and is matched to the specialist
   whose expertise fits their presentation.
2. **Intelligence engine** — a healthy-cell reference of the lung that scores how a sample
   deviates from healthy, across cell-type composition, gene expression, and pathways.
3. **Expert network** — clinicians and researchers confirm, correct, and annotate the
   model's findings, sharpening it over time.
4. **Treatment intelligence** — reasoning about how to reverse a characterised deviation.
   The destination, not yet built.

---

## What's built

- A **healthy-lung reference** constructed from the Human Lung Cell Atlas, restricted to
  `disease == normal` cells. Per-donor, per-cell-type statistics give a sample-level
  baseline for what "normal" looks like.
- A **deviation engine** that returns ranked deviations (cell-type composition, gene-level
  Z-scores, pathway activity) for a submitted expression profile.
- A deployed **FastAPI** backend and **Next.js** front end.

**Status:** research stage. The reference detects deviation well *in-distribution*
(same-source data). Making detection robust across **different labs** (batch effects) is
the active research problem. The model characterises deviations; it does not diagnose.

---

## Principles (hard rules)

1. **The model learns from data. Nothing biological is hardcoded.** Every reference
   statistic is computed from real healthy cells. No curated disease signatures.
2. **The model describes biology. Experts name diseases.** Outputs are deviations and
   scores, not disease labels.
3. **Every output carries a safety disclaimer.** It is part of the schema.
4. **Memory-safe by default.** Large `.h5ad` files are read with `backed='r'`; never loaded
   fully into RAM.

---

## Tech stack

| Component | Technology |
|---|---|
| API | FastAPI + uvicorn, Pydantic v2 |
| Single-cell data | scanpy + anndata |
| Representation learning | scVI / scArches (research) |
| Frontend | Next.js 14 |
| Deploy | Cloud Run + Vercel |

---

## Repository layout

```
app/            FastAPI backend (services, schemas, API routes)
ui/             Next.js frontend
scripts/        Model build + validation scripts
notebooks/      Exploratory work
models/         Trained model artefacts (gitignored, large)
data/           .h5ad datasets (gitignored, large)
CLAUDE.md       Full developer reference
```

---

## Running locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# API docs: http://localhost:8000/docs
```

Frontend:

```bash
cd ui && npm install && npm run dev
# http://localhost:3000
```

---

## Disclaimer

This is a **research and decision-support system**, not a diagnostic. It characterises
how a sample deviates from a healthy reference; it does not provide clinical diagnoses,
and no output should be acted on without review by a qualified medical professional.

---

*Senebiclabs — a model of health, starting with the lung, building toward the whole body.*
