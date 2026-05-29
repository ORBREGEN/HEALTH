"""
Expert Network API — onboard and manage respiratory specialists.

POST /expert/apply          — full application (stored in Supabase, emails fired)
POST /expert/{id}/review    — approve or reject an application (admin only)
"""

import logging
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr

from app.services.supabase_client import get_client
from app.services import email_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/expert", tags=["Expert Network"])


# ── Schemas ────────────────────────────────────────────────────────────────────

class ExpertApplication(BaseModel):
    name: str
    email: EmailStr
    note: str | None = None
    agreed_to_terms: bool = False
    lat: float | None = None
    lng: float | None = None


class ApplicationResponse(BaseModel):
    ok: bool
    message: str


class ReviewPayload(BaseModel):
    action: str   # "approve" | "reject"
    note: str | None = None


# ── Apply ──────────────────────────────────────────────────────────────────────

@router.post("/apply", response_model=ApplicationResponse, summary="Apply to join the specialist network")
def apply(application: ExpertApplication):
    if not application.agreed_to_terms:
        raise HTTPException(status_code=400, detail="You must agree to the terms before applying.")

    db = get_client()
    if db is None:
        logger.warning("Expert application ignored — Supabase not configured (email=%s)", application.email)
        raise HTTPException(
            status_code=503,
            detail="Applications are temporarily unavailable. Please try again shortly.",
        )

    try:
        existing = (
            db.table("expert_applications")
            .select("id")
            .eq("email", application.email.lower())
            .execute()
        )
        if existing.data:
            return ApplicationResponse(
                ok=True,
                message="We already have an application from this email. We will be in touch.",
            )

        db.table("expert_applications").insert(
            {
                "name": application.name,
                "email": application.email.lower(),
                "specialty": "",
                "institution": "",
                "country": "",
                "license_number": "",
                "years_experience": "",
                "note": application.note,
                "lat": application.lat,
                "lng": application.lng,
                "status": "pending",
            }
        ).execute()

    except Exception as exc:
        logger.error("Expert application insert failed: %s", exc)
        raise HTTPException(status_code=500, detail="Could not save your application. Please try again.")

    # Emails — fire after DB write succeeds
    email_service.send_expert_application_confirmation(
        name=application.name,
        email=application.email,
    )
    email_service.send_expert_application_admin_alert(
        name=application.name,
        email=application.email,
        note=application.note,
    )

    logger.info("Expert application received: %s (%s)", application.name, application.email)
    return ApplicationResponse(ok=True, message="Application received. We will be in touch.")


# ── Review (admin) ─────────────────────────────────────────────────────────────

@router.post("/{application_id}/review", response_model=ApplicationResponse, summary="Approve or reject an application")
def review(
    application_id: str,
    payload: ReviewPayload,
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
):
    if not settings.ADMIN_API_KEY or x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    if payload.action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="action must be 'approve' or 'reject'.")

    db = get_client()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    try:
        result = (
            db.table("expert_applications")
            .select("id, name, email, status")
            .eq("id", application_id)
            .execute()
        )
    except Exception as exc:
        logger.error("Expert review lookup failed: %s", exc)
        raise HTTPException(status_code=500, detail="Database error.")

    if not result.data:
        raise HTTPException(status_code=404, detail="Application not found.")

    row = result.data[0]
    new_status = "approved" if payload.action == "approve" else "rejected"

    try:
        db.table("expert_applications").update({"status": new_status}).eq("id", application_id).execute()
    except Exception as exc:
        logger.error("Expert review update failed: %s", exc)
        raise HTTPException(status_code=500, detail="Could not update application status.")

    if payload.action == "approve":
        email_service.send_expert_approved(
            name=row["name"],
            email=row["email"],
        )
    else:
        email_service.send_expert_rejected(
            name=row["name"],
            email=row["email"],
        )

    logger.info("Expert application %s: %s (%s)", new_status, row["name"], row["email"])
    return ApplicationResponse(ok=True, message=f"Application {new_status}.")
