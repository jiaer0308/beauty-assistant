#!/usr/bin/env python3
"""
Beauty Assistant API - FastAPI Entry Point

Exposes the ML-powered Seasonal Color Analysis (SCA) pipeline
via a REST API designed for the Flutter mobile client.
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logger import setup_logger
from app.api.v1.router import api_router


# Bootstrap logging
setup_logger(level=settings.log_level)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan: startup / shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    The SCA service + ML models are heavy – we initialise them once here so
    they are shared across all requests via app.state.
    """
    logger.info("Starting Beauty Assistant API...")

    # Lazy-import here to avoid paying startup cost during tests that mock it
    from app.services.sca_workflow_service import SCAWorkflowService
    app.state.sca_service = SCAWorkflowService()
    logger.info("SCAWorkflowService loaded and ready.")

    yield  # ← application runs here

    logger.info("Shutting down Beauty Assistant API.")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Beauty Assistant REST API powering the Flutter mobile app.\n\n"
        "| Endpoint | Purpose |\n"
        "|---|---|\n"
        "| `POST /api/v1/sca/analyze` | Seasonal Color Analysis |\n"
        "| `GET  /api/v1/health`      | Health check            |"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow the Flutter dev emulator and any production origin
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(api_router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Root redirect
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def root():
    return JSONResponse({"message": "Beauty Assistant API is running.", "docs": "/docs"})
