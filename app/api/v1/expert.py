"""
Expert Network API — onboard and manage respiratory specialists.

POST /expert/apply   — full application (stored in Supabase)
POST /expert/waitlist — legacy lightweight waitlist (kept for compatibility)
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.services.supabase_client import get_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/expert", tags=["Expert Network"])


class ExpertApplication(BaseModel):
    name: str
    email: EmailStr
    specialty: str
    institution: str
    country: str
    license: str
    experience: str
    note: str | None = None
    lat: float | None = None
    lng: float | None = None


class ApplicationResponse(BaseModel):
    ok: bool
    message: str


@router.post("/apply", response_model=ApplicationResponse, summary="Apply to join the specialist network")
def apply(application: ExpertApplication):
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
                message="We already have an application from this email. We will be in touch shortly.",
            )

        db.table("expert_applications").insert(
            {
                "name": application.name,
                "email": application.email.lower(),
                "specialty": application.specialty,
                "institution": application.institution,
                "country": application.country,
                "license_number": application.license,
                "years_experience": application.experience,
                "note": application.note,
                "lat": application.lat,
                "lng": application.lng,
                "status": "pending",
            }
        ).execute()
    except Exception as exc:
        logger.error("Expert application insert failed: %s", exc)
        raise HTTPException(status_code=500, detail="Could not save your application. Please try again.")

    logger.info("Expert application received: %s (%s)", application.name, application.email)
    return ApplicationResponse(ok=True, message="Application received. We will be in touch within 5 business days.")


# ── Legacy waitlist (kept so old callers still work) ─────────────────────────

class _LegacyEntry(BaseModel):
    email: EmailStr
    specialty: str | None = None


@router.post("/waitlist", response_model=ApplicationResponse, summary="Join expert waitlist (legacy)")
def legacy_waitlist(entry: _LegacyEntry):
    db = get_client()
    if db is not None:
        try:
            db.table("waitlist").upsert(
                {"email": entry.email.lower(), "type": "expert"},
                on_conflict="email,type",
            ).execute()
        except Exception as exc:
            logger.error("Legacy waitlist insert failed: %s", exc)
    return ApplicationResponse(ok=True, message="You are on the list.")
