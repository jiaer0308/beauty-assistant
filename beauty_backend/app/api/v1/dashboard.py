#!/usr/bin/env python3
"""
Dashboard API Endpoint (v1)

Serves the Atelier Home Screen on the Flutter application.
"""

from fastapi import APIRouter
from sqlalchemy import func

from app.api.deps import DBDep, CurrentUserDep
from app.domain.entities.history import RecommendationSession
from app.domain.entities.knowledge_base import Season, CosmeticProduct, Brand, CosmeticSeasonMapping
from app.schemas.dashboard import DashboardResponse, DashboardResult, RecommendedProduct


router = APIRouter()


@router.get("", response_model=DashboardResponse, summary="Get Atelier Home Dashboard")
def get_dashboard(
    current_user: CurrentUserDep,
    db: DBDep,
):
    """
    Fetch the most recent recommendation session for the authenticated user
    (guest or registered) to populate the main dashboard.

    Authentication is handled automatically via the ``X-Guest-Token`` header
    for guest users, or a ``Bearer`` JWT for registered users.

    Returns:
        DashboardResponse: The season result and curated products. If no
                           session is found, returns an empty state.
    """
    # 1. Fetch most recent session
    latest_session = (
        db.query(RecommendationSession)
        .filter(RecommendationSession.user_id == current_user.id)
        .order_by(RecommendationSession.created_at.desc())
        .first()
    )

    if not latest_session:
        return DashboardResponse(
            success=True,
            result=None,
            recommended_products=[]
        )

    # 2. Extract Season info
    display_name = "Unknown Season"
    season_key = None
    if latest_session.season_id is not None:
        season_entity = db.query(Season).filter(Season.id == latest_session.season_id).first()
        if season_entity:
            display_name = season_entity.name
            # Derive specific machine string like "Deep Autumn" -> "deep_autumn"
            season_key = display_name.lower().replace(" ", "_").replace("-", "_")

    result = DashboardResult(
        display_name=display_name,
        season=season_key
    )

    # 3. Retrieve Recommended Products by joining related tables
    # Fetch all (CosmeticProduct, Brand) pairs matching the items in this session
    curated_items = (
        db.query(CosmeticProduct, Brand)
        .join(Brand, CosmeticProduct.brand_id == Brand.id)
        .join(CosmeticSeasonMapping, CosmeticSeasonMapping.cosmetic_id == CosmeticProduct.id)
        .filter(CosmeticSeasonMapping.season_id == latest_session.season_id)
        .order_by(func.random())
        .limit(6)
        .all()
    )

    recommended_products = []
    for product, brand in curated_items:
        # Construct the combined name properly (e.g. "Liquid Blush in Orgasm")
        combined_name = f"{product.product_name} in {product.shade_name}"
        
        # Ensure we always return a valid string for the frontend UI format
        image_url = product.image_url if product.image_url else ""
        
        recommended_products.append(
            RecommendedProduct(
                brand=brand.name,
                name=combined_name,
                image_url=image_url
            )
        )

    return DashboardResponse(
        success=True,
        result=result,
        recommended_products=recommended_products
    )
