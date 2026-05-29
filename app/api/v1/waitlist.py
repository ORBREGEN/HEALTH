"""
Unified waitlist endpoint — handles patient, contributor, and researcher sign-ups.
Stores email + type + optional location in Supabase, then sends a confirmation email.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.services.supabase_client import get_client
from app.services import email_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/waitlist", tags=["Waitlist"])


class WaitlistSignup(BaseModel):
    email: EmailStr
    type: str  # 'patient' | 'contributor' | 'researcher'
    lat: float | None = None
    lng: float | None = None
    location_text: str | None = None


class WaitlistResponse(BaseModel):
    ok: bool
    message: str


@router.post("", response_model=WaitlistResponse, summary="Join a waitlist")
def join_waitlist(signup: WaitlistSignup):
    allowed_types = {"patient", "contributor", "researcher"}
    if signup.type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"type must be one of {allowed_types}")

    db = get_client()
    if db is None:
        logger.warning("Waitlist signup ignored — Supabase not configured (email=%s type=%s)", signup.email, signup.type)
        return WaitlistResponse(ok=True, message="You are on the list.")

    already_exists = False
    try:
        existing = (
            db.table("waitlist")
            .select("id")
            .eq("email", signup.email.lower())
            .eq("type", signup.type)
            .execute()
        )
        if existing.data:
            already_exists = True
        else:
            db.table("waitlist").insert(
                {
                    "email": signup.email.lower(),
                    "type": signup.type,
                    "lat": signup.lat,
                    "lng": signup.lng,
                    "location_text": signup.location_text,
                }
            ).execute()
    except Exception as exc:
        logger.error("Waitlist insert failed: %s", exc)
        raise HTTPException(status_code=500, detail="Could not save your sign-up. Please try again.")

    if not already_exists:
        email_service.send_waitlist_confirmation(email=signup.email, type=signup.type)

    logger.info("Waitlist: %s joined as %s (already_existed=%s)", signup.email, signup.type, already_exists)
    return WaitlistResponse(ok=True, message="You are on the list.")
