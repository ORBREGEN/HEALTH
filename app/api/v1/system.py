from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings
from app.models.schemas import SystemHealth
from app.services.respiratory_model import model_is_built

router = APIRouter(tags=["System"])


@router.get("/health", response_model=SystemHealth, summary="System health check")
def health():
    return SystemHealth(
        status      = "ok",
        version     = settings.VERSION,
        timestamp   = datetime.now(timezone.utc),
        model_ready = model_is_built(),
    )
