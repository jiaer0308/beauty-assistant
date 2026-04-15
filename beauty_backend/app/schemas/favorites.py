#!/usr/bin/env python3
"""
Favorites Schemas (Pydantic V2)

Defines the response models for the user favorites endpoints.
Response shape mirrors CosmeticSessionItem for frontend UI consistency.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class FavoriteItemResponse(BaseModel):
    """Full cosmetic product details for a favorited item."""

    id: int = Field(..., description="Cosmetic product ID", examples=[42])
    product_name: str = Field(..., description="Product name", examples=["Liquid Blush"])
    shade_name: str = Field(..., description="Shade name", examples=["Orgasm"])
    brand_name: Optional[str] = Field(
        default=None,
        description="Brand name",
        examples=["NARS"],
    )
    category_id: Optional[int] = Field(
        default=None,
        description="Category ID",
        examples=[1],
    )
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
    favorited_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the user favorited this item",
    )

    model_config = ConfigDict(from_attributes=True)


class FavoritesListResponse(BaseModel):
    """Response wrapper for the list of favorites, including pagination metadata."""

    total: int = Field(..., description="Total number of favorited items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="Whether there's a subsequent page")
    items: List[FavoriteItemResponse] = Field(
        ...,
        description="List of favorited cosmetic products for the current page",
    )
