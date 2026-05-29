"""
Unified waitlist endpoint — handles patient, contributor, and researcher sign-ups.
Stores email, type, and optional location (lat/lng) in Supabase.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.services.supabase_client import get_client

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

    try:
        db.table("waitlist").upsert(
            {
                "email": signup.email.lower(),
                "type": signup.type,
                "lat": signup.lat,
                "lng": signup.lng,
                "location_text": signup.location_text,
            },
            on_conflict="email,type",
        ).execute()
    except Exception as exc:
        logger.error("Waitlist insert failed: %s", exc)
        raise HTTPException(status_code=500, detail="Could not save your sign-up. Please try again.")

    logger.info("Waitlist: %s joined as %s", signup.email, signup.type)
    return WaitlistResponse(ok=True, message="You are on the list.")
