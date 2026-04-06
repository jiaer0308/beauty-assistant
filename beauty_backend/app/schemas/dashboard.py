#!/usr/bin/env python3
"""
Dashboard API Schemas (Pydantic V2)

These models define the exact JSON contract between the FastAPI backend
and the Flutter mobile client for the home dashboard screen.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class RecommendedProduct(BaseModel):
    """A specific cosmetic product recommendation fetched directly from the DB."""
    id: int = Field(..., examples=[42], description="Database ID of the cosmetic product")
    brand: str = Field(..., examples=["NARS"], description="Brand name")
    name: str = Field(..., examples=["Liquid Blush"], description="Product name")
    shade: str = Field(..., examples=["Orgasm"], description="Shade name")
    image_url: str = Field(..., examples=["https://example.com/image.png"], description="URL of the product image")
    category_id: int = Field(..., examples=[6], description="Category ID — 6=Lipstick, 7=Lip Gloss, 8=Lip Stain. Used by the client to determine AR compatibility.")
    hex_code: Optional[str] = Field(None, examples=["#C04040"], description="Hex color code of the shade, if available")


class DashboardResult(BaseModel):
    """The latest Seasonal attributes returned by the database."""
    display_name: str = Field(..., examples=["Deep Autumn"], description="Human-friendly season name")
    season: Optional[str] = Field(None, examples=["deep_autumn"], description="Machine-readable season identifier")


class DashboardResponse(BaseModel):
    """
    Complete Dashboard API response.
    
    Returned by ``GET /api/v1/dashboard``.
    Contains graceful empty fallbacks if the user has no sessions.
    """
    success: bool = True
    result: Optional[DashboardResult] = Field(None, description="The most recent colour analysis session result, if available")
    recommended_products: List[RecommendedProduct] = Field(
        default_factory=list, description="A personalized array of products matching the user's latest analysis outcome"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "result": {
                    "display_name": "Deep Autumn",
                    "season": "deep_autumn"
                },
                "recommended_products": [
                    {
                        "brand": "NARS",
                        "name": "Liquid Blush",
                        "shade": "Orgasm",
                        "image_url": "https://example.com/image.png"
                    }
                ]
            }
        }
    }
