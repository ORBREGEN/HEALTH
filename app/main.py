"""
HEALTH — Respiratory Intelligence Platform
FastAPI entry point.

Start with:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Docs:
    http://localhost:8000/docs
    http://localhost:8000/redoc
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    DataNotAvailableError,
    InsufficientGenesError,
    ModelNotBuiltError,
)

app = FastAPI(
    title       = "HEALTH — Respiratory Intelligence Platform",
    description = (
        "A four-layer platform for respiratory health.\n\n"
        "**Layer 1** — Patient Portal: connect citizens with appropriate specialists.\n\n"
        "**Layer 2** — Respiratory Intelligence Engine: understand the healthy respiratory "
        "system at the cellular level; characterise deviations in new samples.\n\n"
        "**Layer 3** — Expert Network: clinicians review and improve model outputs.\n\n"
        "**Layer 4** — Treatment Intelligence: generate guidelines from the healthy "
        "reference and the characterised breakdown (future)."
    ),
    version     = settings.VERSION,
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(ModelNotBuiltError)
async def model_not_built(request: Request, exc: ModelNotBuiltError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(DataNotAvailableError)
async def data_not_available(request: Request, exc: DataNotAvailableError):
    return JSONResponse(status_code=503, content={"detail": str(exc), "path": exc.path})


@app.exception_handler(InsufficientGenesError)
async def insufficient_genes(request: Request, exc: InsufficientGenesError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/", include_in_schema=False)
def root():
    return {
        "system":  "HEALTH — Respiratory Intelligence Platform",
        "version": settings.VERSION,
        "docs":    "/docs",
        "layers":  {
            "1": "Patient Portal      — POST /api/v1/patient/intake",
            "2": "Intelligence Engine — POST /api/v1/model/build · POST /api/v1/analyse · POST /api/v1/interpret",
            "3": "Expert Network      — coming soon",
            "4": "Treatment Intel     — coming soon",
        },
    }
