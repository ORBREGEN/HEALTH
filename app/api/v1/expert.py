import csv
import logging
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/expert", tags=["Expert Network"])

WAITLIST_FILE = settings.DATA_DIR / "expert_waitlist.csv"
WAITLIST_COLUMNS = ["email", "joined_at"]


def _ensure_file():
    WAITLIST_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not WAITLIST_FILE.exists():
        with WAITLIST_FILE.open("w", newline="") as f:
            csv.writer(f).writerow(WAITLIST_COLUMNS)


class WaitlistEntry(BaseModel):
    email: EmailStr


class WaitlistResponse(BaseModel):
    success: bool
    message: str


@router.post("/waitlist", response_model=WaitlistResponse, summary="Join expert waitlist")
def join_waitlist(entry: WaitlistEntry):
    _ensure_file()

    # Deduplicate — don't add the same email twice
    existing = set()
    with WAITLIST_FILE.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing.add(row["email"].lower())

    email = entry.email.lower()
    if email in existing:
        return WaitlistResponse(success=True, message="Already on the waitlist.")

    with WAITLIST_FILE.open("a", newline="") as f:
        csv.writer(f).writerow([email, datetime.now(timezone.utc).isoformat()])

    logger.info("Expert waitlist: added %s", email)
    return WaitlistResponse(success=True, message="You're on the list. We'll reach out when expert onboarding opens.")
