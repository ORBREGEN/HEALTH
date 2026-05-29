Senebiclabs
Biological Intelligence Platform: Platform Overview

---

The Idea

Most clinical tools learn from disease. They study what went wrong.
Senebiclabs learns from health first.

We built a precise computational reference of what a healthy human lung looks like
at the cellular level. When a new patient sample is analysed, the system compares
it against that reference and describes exactly what has changed: which cells are
out of proportion, which biological processes are disrupted, and where in the lung
tissue the deviation is concentrated.

The system does not name diseases. It describes biology.
A clinician reads the output and draws conclusions.

---

The Data Behind It

The reference model is built from the Human Lung Cell Atlas, a dataset compiled
by research institutions across the UK, United States, and Europe.

  Healthy human lung cells       1,305,099
  Donors represented             268
  Cell types modelled            60
  Genes tracked                  9,838
  Tissue regions (spatial)       Airway (bronchus) + Alveolar (parenchyma)

Every reference statistic is computed from real human cells.
Nothing is hardcoded. Nothing is assumed.

---

What a Report Shows

When a gene expression sample is submitted, the system produces a structured
biological report across six dimensions:

1. Cell type composition
Which cell populations are expanded or depleted, and by how much.
Expressed as Z-scores against the healthy donor distribution.

2. Gene-level deviations
Which genes are outside their healthy range. How far outside.
Direction: elevated or suppressed.

3. Pathway activity
Which biological processes are over-active or suppressed
compared to the healthy baseline.

4. Fetal programme reactivation
Whether genes normally active only in fetal development
have been switched back on. A signal seen in fibrosis and cancer.

5. Cell type functional impairment
Cell types present in normal numbers but functioning abnormally.
This catches impairment that standard analysis misses.

6. Spatial tissue localisation
Whether the deviation is concentrated in the airway or the alveolar tissue.

The same elevated gene reads differently with spatial context:
"COL1A1 elevated" reads as a general fibrotic signal.
"COL1A1 elevated in alveolar tissue, normal in airway" points to subpleural fibrosis, not airway remodelling.

This distinction matters for TB (bronchocentric), IPF (subpleural), and COPD (both compartments).

---

Why This Matters for Respiratory Research

Tuberculosis
TB produces characteristic cellular signatures: macrophage activation, interferon response,
lymphocyte infiltration, granuloma formation. The system can detect these as deviations
from the healthy reference. Spatial context distinguishes bronchocentric TB from
disseminated disease.

COPD
COPD involves airway inflammation and alveolar destruction simultaneously.
The spatial dimension separates these signals. Spirometry cannot.

Post-TB lung disease
Persistent cellular changes after treatment are currently very difficult to quantify.
This system can characterise what remains biologically abnormal at the cellular level
after TB is cleared.

---

Current Status

  Healthy reference model                  Complete
  Six-dimension analysis engine            Live
  Spatial tissue localisation              Live
  API and web analysis interface           Running
  Clinical validation against real cases   Requires partnership
  Patient matching application             In development

---

What We Are Asking For

A research collaboration with KEMRI-CRDR.

Specifically: a clinician or researcher willing to look at what this system produces
against cases your team already knows (TB, COPD, post-TB) and tell us honestly
whether the biological findings are pointing at the right things.

We are not asking for funding.
We are not presenting a finished product.
We are asking for clinical eyes on a working tool.

---

Godwin Yampoi, Founder, Senebiclabs
godwinyampoi449@gmail.com

All outputs are for research use only and do not constitute clinical diagnoses.
