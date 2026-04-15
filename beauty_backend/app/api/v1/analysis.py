#!/usr/bin/env python3
"""
SCA (Seasonal Color Analysis) API Endpoints

Flutter client contract
-----------------------
POST /api/v1/sca/analyze
  - Body    : multipart/form-data  { file: <image/jpeg|png>, quiz_data: <stringified JSON> }
  - Returns : SCAResponse (200) | ErrorResponse (400 / 500)

GET  /api/v1/sca/health
  - Returns : JSON { "status": "ok" }
"""

import logging
from datetime import datetime

from fastapi import APIRouter, File, Form, UploadFile, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import SCAServiceDep, CurrentUserDep
from app.core.database import get_db
from app.core.config import settings
from app.domain.entities import (
    Season as SeasonModel, 
    Color as ColorModel, 
    CosmeticProduct as CosmeticProductModel,
    SeasonColor as SeasonColorModel
)
from app.schemas.sca import (
    QuizData,
    SCAResponse,
    SeasonInfo,
    ColorMetrics,
    DominantColors,
    DebugInfo,
    ErrorResponse,
    ColorSwatch,
    ColorPalette,
    CosmeticProduct,
    Recommendations,
)
from app.services.sca_workflow_service import ValidationError

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@router.get(
    "/health",
    summary="SCA service health",
    response_description="Service status",
    tags=["meta"],
)
async def health_check(sca_service: SCAServiceDep):
    """
    Lightweight liveness probe.

    Returns ``{"status": "ok"}`` when the SCA service (including ML models)
    is loaded and ready.
    """
    return {"status": "ok", "service": "sca", "timestamp": datetime.now().isoformat()}


# ---------------------------------------------------------------------------
# Main analyse endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/analyze",
    response_model=SCAResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation / image quality error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Analyse face image for seasonal colour type",
    response_description="Seasonal colour analysis result",
    tags=["sca"],
)
async def analyze_image(
    sca_service: SCAServiceDep,
    current_user: CurrentUserDep,
    db: Session = Depends(get_db),
    file: UploadFile = File(
        ...,
        description="Face photo (JPEG or PNG, max 10 MB)",
    ),
    quiz_data: str = Form(
        default="{}",
        description="Stringified JSON object matching the QuizData schema (optional; send {} to omit)",
    ),
):
    logger.info("Entering analyze_image endpoint")
    # ------------------------------------------------------------------ #
    # 1. Parse & validate quiz_data
    # ------------------------------------------------------------------ #
    try:
        logger.info("Parsing quiz_data: %s", quiz_data)
        parsed_quiz = QuizData.model_validate_json(quiz_data)
    except Exception as exc:
        logger.warning("Invalid quiz_data JSON: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"quiz_data contains invalid JSON or schema mismatch: {exc}",
        )

    logger.info(
        "User %d (%s) parsed quiz data: skin_type=%s",
        current_user.id,
        current_user.email or "Guest",
        parsed_quiz.skin_type,
    )

    # ------------------------------------------------------------------ #
    # 2. Validate uploaded file type
    # ------------------------------------------------------------------ #
    allowed_types = settings.get_allowed_image_types
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{file.content_type}'. "
                   f"Allowed: {', '.join(allowed_types)}",
        )

    # ------------------------------------------------------------------ #
    # 2. Validate file size
    # ------------------------------------------------------------------ #
    image_bytes = await file.read()
    if len(image_bytes) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large ({len(image_bytes) // 1024} KB). "
                   f"Maximum allowed is {settings.max_file_size_mb} MB.",
        )

    logger.info(
        "Received analyze request: user_id=%d, filename=%s, size=%d bytes",
        current_user.id,
        file.filename,
        len(image_bytes),
    )

    # ------------------------------------------------------------------ #
    # 3. Run SCA pipeline
    # ------------------------------------------------------------------ #
    try:
        # Pass DB and user_id to service to persist history
        result = await sca_service.analyze(
            image_bytes=image_bytes, 
            db=db, 
            user_id=current_user.id, 
            quiz_data=parsed_quiz
        )

    except ValidationError as exc:
        logger.warning("Validation failed for uploaded image: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Unexpected error during SCA analysis")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during analysis. Please try again.",
        )

    # ------------------------------------------------------------------ #
    # 4. Map domain entity → API schema
    # ------------------------------------------------------------------ #
    # Fetch recommendations from Database if available, else fallback to JSON
    # result.season.value is the machine name like 'soft_autumn'
    recs_raw = result.recommendations or {}
    best_colors    = [ColorSwatch(**c) for c in recs_raw.get("best_colors", [])]
    neutral_colors = [ColorSwatch(**c) for c in recs_raw.get("neutral_colors", [])]
    avoid_colors   = [ColorSwatch(**c) for c in recs_raw.get("avoid_colors", [])]
    cosmetics      = [CosmeticProduct(**p) for p in recs_raw.get("cosmetics", [])]


    recommendations = Recommendations(
        color_palette=ColorPalette(
            best=best_colors,
            neutral=neutral_colors,
            avoid=avoid_colors,
        ),
        cosmetics=cosmetics,
    )

    response = SCAResponse(
        result=SeasonInfo(
            season=result.season.value,
            display_name=result.display_name,
            confidence=round(result.confidence, 2),
        ),
        metrics=ColorMetrics(
            contrast_score=round(result.contrast_score, 1),
            skin_temperature=result.skin_temperature,
            dominant_colors=DominantColors(
                skin=result.skin_color,
                hair=result.hair_color,
                eye=result.eye_color,
            ),
        ),
        debug_info=DebugInfo(
            lighting_quality=result.lighting_quality,
            processing_time_ms=result.processing_time_ms,
            rotation_angle=round(result.rotation_angle, 1),
        ),
        recommendations=recommendations,
        quiz_influence=result.quiz_influence,
        session_id=result.session_id,
        analyzed_at=result.timestamp,
    )

    logger.info(
        "Analysis complete: season=%s, confidence=%.2f, time=%dms",
        result.season.value,
        result.confidence,
        result.processing_time_ms,
    )

    return response
