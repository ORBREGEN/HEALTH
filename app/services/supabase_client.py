"""
Supabase client — singleton used across all API routes that need database access.

Falls back to None if SUPABASE_URL / SUPABASE_SERVICE_KEY are not set,
so the server still starts in development without a database configured.
Callers check `get_client()` and raise a clear 503 if it is None.
"""

import logging
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)

_client: Client | None = None


def get_client() -> Client | None:
    global _client
    if _client is not None:
        return _client
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        logger.warning("Supabase not configured — SUPABASE_URL or SUPABASE_SERVICE_KEY missing")
        return None
    _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return _client
