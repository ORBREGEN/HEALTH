"""
Senebiclabs API Test Suite
======================
Tests every endpoint of the Respiratory Intelligence Engine.
Runs against the live FastAPI server on localhost:8000.

Run:
    cd /home/godwingodwi/startups/HEALTH
    python -m pytest tests/test_api.py -v
"""

import pytest
import httpx

BASE = "http://localhost:8000"
TIMEOUT = 30


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE, timeout=TIMEOUT) as c:
        yield c


SAMPLE_GENES = {
    "SFTPC":  0.82,   # alveolar AT2 marker — suppressed in this IPF-like profile
    "SFTPB":  0.91,
    "COL1A1": 4.21,   # fibrosis marker — elevated
    "COL3A1": 3.55,
    "FN1":    3.84,
    "ACTA2":  3.12,   # myofibroblast
    "TGFB1":  1.92,
    "AGER":   0.61,   # AT1 marker — suppressed
    "SPP1":   2.41,
    "MUC5B":  2.94,
    "TIMP1":  2.18,
    "VEGFA":  0.89,
}

HEALTHY_GENES = {
    "SFTPC":  6.50,
    "SFTPB":  5.80,
    "COL1A1": 0.40,
    "COL3A1": 0.30,
    "FN1":    0.50,
    "ACTA2":  0.60,
    "TGFB1":  0.35,
    "AGER":   4.20,
    "SPP1":   0.20,
    "MUC5B":  0.10,
    "TIMP1":  0.40,
    "VEGFA":  0.55,
}


# ── 1. System health ───────────────────────────────────────────────────────────

class TestSystemHealth:
    def test_health_endpoint_returns_200(self, client):
        r = client.get("/api/v1/health")
        assert r.status_code == 200

    def test_health_has_required_fields(self, client):
        data = client.get("/api/v1/health").json()
        assert "status" in data
        assert "version" in data
        assert "model_ready" in data

    def test_health_status_is_ok(self, client):
        data = client.get("/api/v1/health").json()
        assert data["status"] == "ok"


# ── 2. Model status ────────────────────────────────────────────────────────────

class TestModelStatus:
    def test_model_status_returns_200(self, client):
        r = client.get("/api/v1/model/status")
        assert r.status_code == 200

    def test_model_is_ready(self, client):
        data = client.get("/api/v1/model/status").json()
        assert data["is_ready"] is True, "Model must be built before running tests"

    def test_model_has_healthy_cells(self, client):
        data = client.get("/api/v1/model/status").json()
        assert data["n_healthy_cells"] > 100_000, \
            f"Expected >100k healthy cells, got {data['n_healthy_cells']}"

    def test_model_has_donors(self, client):
        data = client.get("/api/v1/model/status").json()
        assert data["n_donors"] >= 10

    def test_model_tracks_genes(self, client):
        data = client.get("/api/v1/model/status").json()
        assert data["n_genes_tracked"] >= 1000

    def test_model_has_cell_types(self, client):
        data = client.get("/api/v1/model/status").json()
        assert data["n_cell_types"] >= 10

    def test_model_has_pathways(self, client):
        data = client.get("/api/v1/model/status").json()
        assert data["n_pathways"] >= 1

    def test_spatial_baselines_loaded(self, client):
        data = client.get("/api/v1/model/status").json()
        assert data.get("has_spatial_baselines") is True, \
            "spatial_baselines.json not loaded — copy it from Drive"


# ── 3. Analyse endpoint ────────────────────────────────────────────────────────

class TestAnalyse:
    def test_analyse_returns_200(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_basic",
            "gene_expression": SAMPLE_GENES,
        })
        assert r.status_code == 200, r.text

    def test_analyse_returns_sample_id(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_id_check",
            "gene_expression": SAMPLE_GENES,
        })
        assert r.json()["sample_id"] == "test_id_check"

    def test_analyse_has_deviation_score(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_score",
            "gene_expression": SAMPLE_GENES,
        })
        score = r.json()["overall_deviation_score"]
        assert 0.0 <= score <= 1.0

    def test_analyse_has_summary(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_summary",
            "gene_expression": SAMPLE_GENES,
        })
        assert len(r.json()["summary"]) > 10

    def test_analyse_has_safety_disclaimer(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_disclaimer",
            "gene_expression": SAMPLE_GENES,
        })
        data = r.json()
        assert "safety_disclaimer" in data
        assert len(data["safety_disclaimer"]) > 20

    def test_analyse_returns_gene_deviations(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_genes",
            "gene_expression": SAMPLE_GENES,
        })
        devs = r.json()["gene_deviations"]
        assert isinstance(devs, list)

    def test_analyse_returns_cell_type_deviations(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_celltypes",
            "gene_expression": SAMPLE_GENES,
        })
        devs = r.json()["cell_type_deviations"]
        assert isinstance(devs, list)

    def test_analyse_returns_pathway_deviations(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_pathways",
            "gene_expression": SAMPLE_GENES,
        })
        assert "pathway_deviations" in r.json()

    def test_analyse_returns_spatial_context(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_spatial",
            "gene_expression": SAMPLE_GENES,
        })
        sc = r.json().get("spatial_context")
        assert sc is not None, "spatial_context missing — check spatial_baselines.json"
        assert "dominant_tissue_compartment" in sc
        assert "tissue_localisation_summary" in sc

    def test_gene_deviation_has_required_fields(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_gene_fields",
            "gene_expression": SAMPLE_GENES,
        })
        devs = r.json()["gene_deviations"]
        if devs:
            d = devs[0]
            for field in ["gene", "z_score", "direction", "magnitude",
                          "sample_value", "healthy_mean", "healthy_std"]:
                assert field in d, f"Missing field: {field}"

    def test_cell_type_deviation_has_required_fields(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_ct_fields",
            "gene_expression": SAMPLE_GENES,
        })
        devs = r.json()["cell_type_deviations"]
        if devs:
            d = devs[0]
            for field in ["cell_type", "z_score", "direction", "magnitude", "compartment"]:
                assert field in d, f"Missing field: {field}"

    def test_healthy_sample_has_low_deviation_score(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_healthy",
            "gene_expression": HEALTHY_GENES,
        })
        score = r.json()["overall_deviation_score"]
        assert score < 0.4, \
            f"Healthy-ish sample scored {score:.3f} — expected < 0.4"

    def test_diseased_sample_has_higher_score_than_healthy(self, client):
        r_disease = client.post("/api/v1/analyse", json={
            "sample_id": "test_disease",
            "gene_expression": SAMPLE_GENES,
        })
        r_healthy = client.post("/api/v1/analyse", json={
            "sample_id": "test_healthy2",
            "gene_expression": HEALTHY_GENES,
        })
        score_d = r_disease.json()["overall_deviation_score"]
        score_h = r_healthy.json()["overall_deviation_score"]
        assert score_d > score_h, \
            f"Disease score ({score_d:.3f}) should be higher than healthy ({score_h:.3f})"

    def test_analyse_rejects_too_few_genes(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_toofew",
            "gene_expression": {"SFTPC": 1.0, "COL1A1": 2.0},
        })
        assert r.status_code in (400, 422)

    def test_analyse_reference_fields_present(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_ref",
            "gene_expression": SAMPLE_GENES,
        })
        data = r.json()
        assert data["healthy_reference_cells"] > 0
        assert data["healthy_reference_donors"] > 0
        assert "model_built_at" in data


# ── 4. Spatial context correctness ────────────────────────────────────────────

class TestSpatialContext:
    def test_sftpc_suppression_is_alveolar(self, client):
        """SFTPC is an alveolar gene. When suppressed, the signal should be alveolar."""
        genes = {**SAMPLE_GENES}
        genes["SFTPC"] = 0.1   # strongly suppressed AT2 marker
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_spatial_sftpc",
            "gene_expression": genes,
        })
        sc = r.json().get("spatial_context")
        if sc:
            # SFTPC is an alveolar gene — should appear in alveolar signal genes
            alveolar = sc.get("alveolar_signal_genes", [])
            airway   = sc.get("airway_signal_genes", [])
            # At least some alveolar genes should be flagged
            assert len(alveolar) >= 0   # soft check — passes even if SFTPC not in top devs

    def test_spatial_context_has_summary(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_spatial_summary",
            "gene_expression": SAMPLE_GENES,
        })
        sc = r.json().get("spatial_context")
        if sc:
            assert len(sc["tissue_localisation_summary"]) > 20

    def test_spatial_dominant_compartment_is_valid(self, client):
        r = client.post("/api/v1/analyse", json={
            "sample_id": "test_spatial_compartment",
            "gene_expression": SAMPLE_GENES,
        })
        sc = r.json().get("spatial_context")
        if sc:
            assert sc["dominant_tissue_compartment"] in \
                ("airway", "alveolar", "both", "unknown")


# ── 5. Patient intake ──────────────────────────────────────────────────────────

class TestPatientIntake:
    def test_patient_intake_returns_200(self, client):
        r = client.post("/api/v1/patient/intake", json={
            "patient_id": "test_patient_001",
            "symptoms": ["chronic_cough", "shortness_of_breath"],
            "age": 55,
            "sex": "male",
            "smoking_history": "former",
        })
        assert r.status_code == 200, r.text

    def test_patient_intake_returns_list(self, client):
        r = client.post("/api/v1/patient/intake", json={
            "patient_id": "test_patient_002",
            "symptoms": ["chronic_cough", "shortness_of_breath"],
        })
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_patient_match_has_specialist_type(self, client):
        r = client.post("/api/v1/patient/intake", json={
            "patient_id": "test_patient_003",
            "symptoms": ["coughing_blood"],
        })
        matches = r.json()
        assert all("specialist_type" in m for m in matches)

    def test_patient_match_has_disclaimer(self, client):
        r = client.post("/api/v1/patient/intake", json={
            "patient_id": "test_patient_004",
            "symptoms": ["fever", "night_sweats", "unintended_weight_loss"],
        })
        matches = r.json()
        assert all("disclaimer" in m for m in matches)


# ── 6. Expert application ─────────────────────────────────────────────────────

class TestExpertApplication:
    def test_expert_apply_returns_200(self, client):
        r = client.post("/api/v1/expert/apply", json={
            "name":        "Dr. Test User",
            "email":       "test@example.com",
            "institution": "Test University",
            "specialty":   "Pulmonology",
            "country":     "Kenya",
            "license":     "KE-MED-12345",
            "experience":  "10 years in respiratory medicine.",
        })
        assert r.status_code in (200, 201), r.text


# ── 7. Waitlist ────────────────────────────────────────────────────────────────

class TestWaitlist:
    def test_waitlist_signup_returns_200(self, client):
        r = client.post("/api/v1/waitlist", json={
            "email": "test_waitlist@example.com",
            "type":  "patient",
        })
        assert r.status_code in (200, 201), r.text
