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

from fastapi import APIRouter, File, Form, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse

from app.api.deps import SCAServiceDep
from app.core.config import settings
from app.schemas.sca import (
    QuizData,
    SCAResponse,
    SeasonInfo,
    ColorMetrics,
    DominantColors,
    DebugInfo,
    ErrorResponse,
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
    file: UploadFile = File(
        ...,
        description="Face photo (JPEG or PNG, max 10 MB)",
    ),
    quiz_data: str = Form(
        ...,
        description="Stringified JSON object matching the QuizData schema",
    ),
):
    """
    **Seasonal Colour Analysis**

    Upload a selfie / portrait and receive the user's 12-season colour type.
    Also accepts a `quiz_data` form field containing the user's self-reported
    calibration answers as a stringified JSON object.

    ### Processing pipeline
    1. **Phase 0 – Validation**: lighting quality check  
    2. **Phase 1 – Vision**: MediaPipe face alignment → BiSeNet segmentation  
    3. **Phase 2 – Colour Engine**: K-Means extraction → CIELAB conversion  
    4. **Phase 3 – Classification**: 12-season decision tree  

    ### Flutter usage
    ```dart
    final quizJson = jsonEncode({
      'skin_type': 'dry',
      'sun_reaction': 'always_burn',
      'vein_color': 'blue_purple',
      'natural_hair_color': 'dark_brown',
      'jewelry_preference': 'silver',
    });
    final request = http.MultipartRequest(
      'POST', Uri.parse('$baseUrl/api/v1/sca/analyze'));
    request.files.add(await http.MultipartFile.fromPath('file', imagePath));
    request.fields['quiz_data'] = quizJson;
    final response = await request.send();
    ```
    """
    # ------------------------------------------------------------------ #
    # 1. Parse & validate quiz_data
    # ------------------------------------------------------------------ #
    try:
        parsed_quiz = QuizData.model_validate_json(quiz_data)
    except Exception as exc:
        logger.warning("Invalid quiz_data JSON: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"quiz_data contains invalid JSON or schema mismatch: {exc}",
        )

    logger.info(
        "Parsed quiz data: skin_type=%s, sun_reaction=%s, vein_color=%s, "
        "natural_hair_color=%s, jewelry_preference=%s",
        parsed_quiz.skin_type,
        parsed_quiz.sun_reaction,
        parsed_quiz.vein_color,
        parsed_quiz.natural_hair_color,
        parsed_quiz.jewelry_preference,
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
        "Received analyze request: filename=%s, size=%d bytes, content_type=%s",
        file.filename,
        len(image_bytes),
        file.content_type,
    )

    # ------------------------------------------------------------------ #
    # 3. Run SCA pipeline
    # ------------------------------------------------------------------ #
    try:
        result = await sca_service.analyze(image_bytes)

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
        analyzed_at=result.timestamp,
    )

    logger.info(
        "Analysis complete: season=%s, confidence=%.2f, time=%dms",
        result.season.value,
        result.confidence,
        result.processing_time_ms,
    )

    return response
