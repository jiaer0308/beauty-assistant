#!/usr/bin/env python3
"""
SCA API Schemas (Pydantic V2)

These models define the exact JSON contract between the FastAPI backend
and the Flutter mobile client.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Quiz / calibration input
# ---------------------------------------------------------------------------

class QuizData(BaseModel):
    """
    User self-reported calibration & preference answers.

    All fields are optional so the client can send a partial quiz
    without causing a validation failure.
    """
    skin_type: str | None = Field(
        default=None,
        examples=["oily", "dry", "combination", "normal"],
        description="Self-reported skin type",
    )
    sun_reaction: str | None = Field(
        default=None,
        examples=["always_burn", "tan_easily", "rarely_burn"],
        description="How the user's skin reacts to sun exposure",
    )
    vein_color: str | None = Field(
        default=None,
        examples=["blue_purple", "green", "both"],
        description="Wrist vein colour (blue/purple → cool, green → warm)",
    )
    natural_hair_color: str | None = Field(
        default=None,
        examples=["black", "dark_brown", "light_brown", "blonde", "red", "grey"],
        description="User's natural (undyed) hair colour",
    )
    jewelry_preference: str | None = Field(
        default=None,
        examples=["gold", "silver", "both"],
        description="Which metal tone flatters the user most",
    )


# ---------------------------------------------------------------------------
# Recommendation models
# ---------------------------------------------------------------------------

class ColorSwatch(BaseModel):
    """A single colour in a seasonal palette."""
    name: str = Field(..., examples=["Terracotta"], description="Human-readable colour name")
    hex: str = Field(..., examples=["#C87941"], description="Hex colour code with leading #")


class ColorPalette(BaseModel):
    """Three-tier colour palette for a season."""
    best: List[ColorSwatch] = Field(..., description="5 signature / highly flattering colours")
    neutral: List[ColorSwatch] = Field(..., description="5 versatile, everyday colours")
    avoid: List[ColorSwatch] = Field(..., description="5 colours that clash with this season")


class CosmeticProduct(BaseModel):
    """A specific cosmetic product recommendation."""
    category: str = Field(..., examples=["Lipstick"], description="Product category")
    brand: str = Field(..., examples=["MAC"], description="Brand name")
    name: str = Field(..., examples=["Cherish"], description="Product name")
    shade: str = Field(..., examples=["Cherish"], description="Shade name")
    hex: str = Field(..., examples=["#B05A5A"], description="Approximate hex colour of the shade")
    image_url: str = Field(default="", description="URL of the product image")

class Recommendations(BaseModel):
    """Complete colour + cosmetic recommendations for the detected season."""
    color_palette: ColorPalette
    cosmetics: List[CosmeticProduct] = Field(
        ..., description="5 curated cosmetic product recommendations"
    )


# ---------------------------------------------------------------------------
# Nested display models
# ---------------------------------------------------------------------------

class SeasonInfo(BaseModel):
    """Classified season details."""
    season: str = Field(..., examples=["soft_autumn"], description="Machine-readable season key")
    display_name: str = Field(..., examples=["Soft Autumn"], description="Human-friendly season name")
    confidence: float = Field(..., ge=0.0, le=1.0, examples=[0.82], description="Confidence score 0–1")


class DominantColors(BaseModel):
    """Dominant RGB colours extracted from the image."""
    skin: List[int] = Field(..., min_length=3, max_length=3, examples=[[210, 168, 130]])
    hair: List[int] = Field(..., min_length=3, max_length=3, examples=[[80, 55, 40]])
    eye: List[int] = Field(..., min_length=3, max_length=3, examples=[[100, 80, 60]])


class ColorMetrics(BaseModel):
    """Computed colour-science metrics."""
    contrast_score: float = Field(..., ge=0.0, le=100.0, description="Skin-to-hair CIELAB ΔL")
    skin_temperature: str = Field(..., examples=["warm"], description="'warm', 'cool', or 'neutral'")
    dominant_colors: DominantColors


class DebugInfo(BaseModel):
    """Optional diagnostics — useful during Flutter development."""
    lighting_quality: str = Field(..., examples=["good"])
    processing_time_ms: int = Field(..., ge=0)
    rotation_angle: float = Field(default=0.0, description="Detected face rotation in degrees")


# ---------------------------------------------------------------------------
# Top-level response
# ---------------------------------------------------------------------------

class SCAResponse(BaseModel):
    """
    Complete Seasonal Colour Analysis API response.

    Returned by ``POST /api/v1/sca/analyze``.
    """
    success: bool = True
    result: SeasonInfo
    metrics: ColorMetrics
    debug_info: DebugInfo
    recommendations: Recommendations = Field(
        ..., description="Colour palette and cosmetic product recommendations for the detected season"
    )
    quiz_influence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="0–1 float indicating how much the quiz shifted the final season result",
    )
    analyzed_at: datetime = Field(default_factory=datetime.now)

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "result": {
                    "season": "soft_autumn",
                    "display_name": "Soft Autumn",
                    "confidence": 0.82,
                },
                "metrics": {
                    "contrast_score": 24.5,
                    "skin_temperature": "warm",
                    "dominant_colors": {
                        "skin": [210, 168, 130],
                        "hair": [80, 55, 40],
                        "eye": [100, 80, 60],
                    },
                },
                "debug_info": {
                    "lighting_quality": "good",
                    "processing_time_ms": 850,
                    "rotation_angle": 2.3,
                },
                "recommendations": {
                    "color_palette": {
                        "best": [{"name": "Warm Taupe", "hex": "#937166"}],
                        "neutral": [{"name": "Warm Sand", "hex": "#C2A882"}],
                        "avoid": [{"name": "Electric Blue", "hex": "#007FFF"}],
                    },
                    "cosmetics": [
                        {"category": "Lipstick", "brand": "MAC", "shade": "Cherish", "hex": "#B05A5A"}
                    ],
                },
                "quiz_influence": 0.18,
            }
        }
    }


# ---------------------------------------------------------------------------
# Error response
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    """Standard error envelope returned with 4xx/5xx responses."""
    success: bool = False
    error: str
    detail: str | None = None
