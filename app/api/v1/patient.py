"""
Layer 1 — Patient Portal API

POST /api/v1/patient/intake  — citizen submits symptoms, receives specialist match

This layer is intentionally simple at first. It maps symptom patterns to
specialist types using rule-based logic. When the Respiratory Intelligence Engine
(Layer 2) matures, the matching will be grounded in biological deviation profiles
— what a patient's symptom pattern looks like at the cellular level — rather than
fixed rules.
"""

from fastapi import APIRouter

from app.models.schemas import PatientIntake, Symptom, SpecialistMatch, SpecialistType

router = APIRouter(prefix="/patient", tags=["Patient Portal"])


@router.post(
    "/intake",
    response_model=list[SpecialistMatch],
    summary="Submit symptoms — receive specialist match recommendations",
    description="""
Any citizen can submit their respiratory symptoms. The system returns one or more
specialist types suited to their presentation, with urgency guidance.

No genomics or medical background required. Plain language symptom selection.

**Note**: This is early-stage matching logic based on symptom patterns.
As the Respiratory Intelligence Engine matures, these recommendations will be
grounded in biological characterisation rather than symptom rules alone.
""",
)
def patient_intake(intake: PatientIntake) -> list[SpecialistMatch]:
    return _match_specialists(intake)


def _match_specialists(intake: PatientIntake) -> list[SpecialistMatch]:
    symptoms = set(intake.symptoms)
    matches: list[SpecialistMatch] = []

    # Haemoptysis → urgent, interventional
    if Symptom.COUGHING_BLOOD in symptoms:
        matches.append(SpecialistMatch(
            specialist_type   = SpecialistType.INTERVENTIONAL_PULMONOLOGIST,
            reason            = "Coughing blood requires urgent evaluation to rule out serious pathology.",
            urgency           = "urgent",
            biological_context= "",
        ))

    # Classic malignancy pattern: weight loss + chronic cough + haemoptysis
    malignancy_signals = {Symptom.UNINTENDED_WEIGHT_LOSS, Symptom.CHRONIC_COUGH, Symptom.COUGHING_BLOOD}
    if len(symptoms & malignancy_signals) >= 2:
        matches.append(SpecialistMatch(
            specialist_type   = SpecialistType.THORACIC_ONCOLOGIST,
            reason            = "Combination of constitutional symptoms and respiratory changes warrants oncological assessment.",
            urgency           = "urgent",
            biological_context= "",
        ))

    # Immune / systemic pattern: fever + night sweats + fatigue
    immune_signals = {Symptom.FEVER, Symptom.NIGHT_SWEATS, Symptom.FATIGUE, Symptom.RECURRENT_INFECTIONS}
    if len(symptoms & immune_signals) >= 2:
        matches.append(SpecialistMatch(
            specialist_type   = SpecialistType.RESPIRATORY_IMMUNOLOGIST,
            reason            = "Systemic and immune symptoms alongside respiratory complaints suggest an immunological or autoimmune process.",
            urgency           = "soon",
            biological_context= "",
        ))

    # Chronic obstructive / fibrotic: progressive breathlessness + cough
    chronic_signals = {Symptom.SHORTNESS_OF_BREATH, Symptom.CHRONIC_COUGH, Symptom.CHEST_TIGHTNESS}
    if len(symptoms & chronic_signals) >= 2:
        matches.append(SpecialistMatch(
            specialist_type   = SpecialistType.PULMONOLOGIST,
            reason            = "Progressive breathlessness and cough pattern warrants pulmonary function evaluation and imaging.",
            urgency           = "soon",
            biological_context= "",
        ))

    # Default: general pulmonologist for any respiratory symptom
    if not matches:
        matches.append(SpecialistMatch(
            specialist_type   = SpecialistType.PULMONOLOGIST,
            reason            = "Respiratory symptoms warrant evaluation by a pulmonologist.",
            urgency           = "routine",
            biological_context= "",
        ))

    # Deduplicate by specialist type
    seen = set()
    unique = []
    for m in matches:
        if m.specialist_type not in seen:
            seen.add(m.specialist_type)
            unique.append(m)

    return unique
