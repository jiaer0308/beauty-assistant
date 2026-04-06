#!/usr/bin/env python3
"""
Cosmetic Product Schemas (Pydantic V2)

Defines the response models for cosmetic knowledge-base lookups.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CosmeticShade(BaseModel):
    """Shade info for a single cosmetic product."""

    id: int = Field(..., description="The cosmetic product ID", examples=[42])
    product_name: str = Field(..., description="Product name", examples=["Liquid Blush"])
    shade_name: str = Field(..., description="Shade name", examples=["Orgasm"])
    hex_code: Optional[str] = Field(
        default=None,
        description="Hex colour code of the shade (e.g. '#C8857A')",
        examples=["#C8857A"],
    )

    model_config = ConfigDict(from_attributes=True)


class CosmeticShadesResponse(BaseModel):
    """Batch shade lookup response."""

    shades: List[CosmeticShade] = Field(
        ...,
        description="Shade data for each requested cosmetic ID that was found",
    )


class CosmeticSessionItem(BaseModel):
    """Full cosmetic product details within a recommendation session."""

    id: int = Field(..., description="Cosmetic product ID", examples=[42])
    product_name: str = Field(..., description="Product name", examples=["Liquid Blush"])
    shade_name: str = Field(..., description="Shade name", examples=["Orgasm"])
    hex_code: Optional[str] = Field(
        default=None,
        description="Hex colour code of the shade (e.g. '#C8857A')",
        examples=["#C8857A"],
    )
    image_url: Optional[str] = Field(
        default=None,
        description="URL to the product image",
        examples=["https://example.com/product.jpg"],
    )

    model_config = ConfigDict(from_attributes=True)


class CosmeticSessionResponse(BaseModel):
    """Session-based cosmetic recommendations response."""

    session_id: int = Field(..., description="The recommendation session ID", examples=[7])
    cosmetics: List[CosmeticSessionItem] = Field(
        ...,
        description="All cosmetics recommended in this session",
    )
