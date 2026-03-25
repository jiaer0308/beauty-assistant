#!/usr/bin/env python3
"""
Recommendation History Schemas (Pydantic V2)

Defines the structure for viewing analysis history and
grouped product recommendations.
"""

from __future__ import annotations

from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class RecommendationItemOut(BaseModel):
    """Individual product recommendation details from a session."""
    id: int = Field(..., examples=[1])
    session_id: int = Field(..., examples=[1])
    cosmetic_id: int = Field(..., examples=[1])
    is_saved: bool = Field(default=False, description="Whether the user 'favorited' this product")

    model_config = ConfigDict(from_attributes=True)


class RecommendationSessionOut(BaseModel):
    """
    Summary metadata for an analysis event.
    
    Returned in list views for user recommendation history.
    """
    id: int = Field(..., examples=[1])
    user_id: int = Field(..., examples=[1])
    analysis_type: str = Field(
        ..., 
        examples=["sca_scan", "manual"], 
        description="Origin of the recommendation (automated scan or manual override)"
    )
    season_id: int = Field(
        ..., 
        description="The season ID assigned during this session (FK to seasons.id)"
    )
    image_path: str | None = Field(
        default=None, 
        description="Relative path to the selfie image used for this analysis"
    )
    created_at: datetime = Field(..., description="Timestamp when the session occurred")

    model_config = ConfigDict(from_attributes=True)


class RecommendationSessionDetailOut(RecommendationSessionOut):
    """
    Full recommendation session details including all recommended products.
    
    Returned in single-session detailed views.
    """
    items: List[RecommendationItemOut] = Field(
        ..., 
        description="List of specific products recommended during this analysis session"
    )
