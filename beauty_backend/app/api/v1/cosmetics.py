#!/usr/bin/env python3
"""
Cosmetics API Endpoints (v1)

Provides public knowledge-base lookups for cosmetic products.
No authentication required — product data is public information.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, or_

from app.api.deps import DBDep
from app.domain.entities.history import RecommendationItem, RecommendationSession
from app.domain.entities.knowledge_base import CosmeticProduct, Category
from app.schemas.cosmetic import (
    CosmeticSessionItem,
    CosmeticSessionResponse,
    CosmeticShade,
    CosmeticShadesResponse,
)

router = APIRouter()

@router.get(
    "/shades",
    response_model=CosmeticShadesResponse,
    summary="Get shade hex codes by cosmetic IDs or get all shades for a specific product",
    description=(
        "If 'id' is provided, returns all available shades for that specific product line. "
        "Alternatively, accepts a list of 'ids' to return exactly those corresponding products. "
        "Unknown IDs are silently omitted."
    ),
)
def get_shades(
    ids: Optional[List[int]] = Query(None, description="One or more cosmetic product IDs", example=[1, 2, 3]),
    id: Optional[int] = Query(None, description="A single cosmetic product ID to fetch all of its shades", example=5),
    db: DBDep = None,
) -> CosmeticShadesResponse:
    """
    GET /api/v1/cosmetics/shades?ids=1&ids=2
    GET /api/v1/cosmetics/shades?id=5
    """
    if id is not None:
        # 1. Fetch the base product to get its name and brand
        base_product = db.execute(
            select(CosmeticProduct.product_name, CosmeticProduct.brand_id)
            .where(CosmeticProduct.id == id)
        ).first()

        if not base_product:
            raise HTTPException(status_code=404, detail="Product not found")

        # 2. Fetch all products with the same name and brand (restricted to AR-capable categories)
        rows = (
            db.query(CosmeticProduct.id, CosmeticProduct.product_name, CosmeticProduct.shade_name, CosmeticProduct.hex_code)
            .filter(CosmeticProduct.product_name == base_product.product_name)
            .filter(CosmeticProduct.brand_id == base_product.brand_id)
            .filter(CosmeticProduct.category_id.in_([6, 7, 8]))
            .all()
        )
    elif ids is not None and len(ids) > 0:
        rows = (
            db.query(CosmeticProduct.id, CosmeticProduct.product_name, CosmeticProduct.shade_name, CosmeticProduct.hex_code)
            .filter(CosmeticProduct.id.in_(ids))
            .filter(CosmeticProduct.category_id.in_([6, 7, 8]))
            .all()
        )
    else:
        rows = []

    shades = [
        CosmeticShade(
            id=row.id,
            product_name=row.product_name,
            shade_name=row.shade_name,
            hex_code=row.hex_code
        )
        for row in rows
    ]
    return CosmeticShadesResponse(shades=shades)


@router.get(
    "/sessions/{session_id}",
    response_model=CosmeticShadesResponse,
    summary="Get shade hex codes for a session",
    description=(
        "Returns all cosmetic shade hex codes that were recommended during a specific "
        "recommendation session. Returns 404 if the session does not exist."
    ),
)
def get_cosmetics_by_session(
    session_id: int,
    db: DBDep = None,
) -> CosmeticSessionResponse:
    """
    GET /api/v1/cosmetics/sessions/{session_id}

    Args:
        session_id: The recommendation session ID.

    Returns:
        CosmeticSessionResponse: Session ID + all recommended cosmetic details.

    Raises:
        HTTPException 404: If the session does not exist.
    """
    # 1. Verify session exists (404 guard)
    session_exists = db.execute(
        select(RecommendationSession.id).where(RecommendationSession.id == session_id)
    ).first()

    if not session_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation session {session_id} not found.",
        )

    # 2. Fetch only lip-related cosmetics (lipstick, lip gloss, lip stain) for this session
    stmt = (
        select(
            CosmeticProduct.id,
            CosmeticProduct.product_name,
            CosmeticProduct.shade_name,
            CosmeticProduct.hex_code
        )
        .join(RecommendationItem, RecommendationItem.cosmetic_id == CosmeticProduct.id)
        .join(Category, Category.id == CosmeticProduct.category_id)
        .where(RecommendationItem.session_id == session_id)
        .where(
            or_(
                CosmeticProduct.category_id.in_([6, 7, 8])  # 6=Lipstick, 7=Lip Gloss, 8=Lip Stain
                # Category.name == "Lip Stain"
            )
        )
    )
    rows = db.execute(stmt).all()

    shades = [
        CosmeticShade(
            id=row.id,
            product_name=row.product_name,
            shade_name=row.shade_name,
            hex_code=row.hex_code
        )
        for row in rows
    ]
    return CosmeticShadesResponse(shades=shades)
