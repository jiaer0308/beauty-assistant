#!/usr/bin/env python3
"""
User Favorites API Endpoints

Manages the user's global favorites list, fully decoupled from any
specific recommendation_session. All endpoints require a valid JWT token.
The current user is extracted from the Authorization: Bearer <token> header.
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import joinedload

from app.api.deps import CurrentUserDep, DBDep
from app.domain.entities.knowledge_base import CosmeticProduct
from app.domain.entities.user import user_favorite_cosmetics
from app.schemas.favorites import FavoriteItemResponse, FavoritesListResponse

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# GET /api/v1/favorites/
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=FavoritesListResponse,
    summary="Get all favorited cosmetics",
    description=(
        "Returns a paginated list of cosmetics the current authenticated user has "
        "favorited, filtered by their user ID extracted from the JWT token."
    ),
)
def get_favorites(
    current_user: CurrentUserDep, 
    db: DBDep,
    page: int = 1,
    limit: int = 20,
):
    """
    GET /api/v1/favorites/
    
    Args:
        page (int): The page number.
        limit (int): Number of items per page.

    Returns:
        FavoritesListResponse: Total count + pagination data + list of enriched cosmetic products.
    """
    # Base query for the current user's favorites
    query = db.query(CosmeticProduct).join(
        user_favorite_cosmetics,
        user_favorite_cosmetics.c.cosmetic_id == CosmeticProduct.id
    ).filter(
        user_favorite_cosmetics.c.user_id == current_user.id
    ).options(
        joinedload(CosmeticProduct.brand),
        joinedload(CosmeticProduct.category)
    )

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    cosmetics = query.offset(offset).limit(limit).all()

    has_next = (offset + limit) < total

    items: List[FavoriteItemResponse] = []
    for cosmetic in cosmetics:
        items.append(
            FavoriteItemResponse(
                id=cosmetic.id,
                product_name=cosmetic.product_name,
                shade_name=cosmetic.shade_name,
                brand_name=cosmetic.brand.name if cosmetic.brand else None,
                category_id=cosmetic.category_id,
                hex_code=cosmetic.hex_code,
                image_url=cosmetic.image_url,
            )
        )

    return FavoritesListResponse(
        total=total,
        page=page,
        size=limit,
        has_next=has_next,
        items=items
    )


# ---------------------------------------------------------------------------
# POST /api/v1/favorites/{cosmetic_id}
# ---------------------------------------------------------------------------

@router.post(
    "/{cosmetic_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Add a cosmetic to favorites",
    description=(
        "Adds a cosmetic item to the current authenticated user's favorites. "
        "Safe to call multiple times — duplicates are silently ignored."
    ),
)
def add_favorite(cosmetic_id: int, current_user: CurrentUserDep, db: DBDep):
    """
    POST /api/v1/favorites/{cosmetic_id}

    Args:
        cosmetic_id (int): The ID of the cosmetic product to favorite.

    Returns:
        dict: Confirmation message with the cosmetic_id.

    Raises:
        HTTPException 404: If the cosmetic product does not exist.
    """
    # 1. Verify the cosmetic exists
    cosmetic = db.query(CosmeticProduct).filter(
        CosmeticProduct.id == cosmetic_id,
        CosmeticProduct.is_active == True,
    ).first()

    if not cosmetic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cosmetic product with ID {cosmetic_id} was not found.",
        )

    # 2. Check if already favorited (use direct insert to mimic INSERT IGNORE)
    already_exists = db.execute(
        user_favorite_cosmetics.select().where(
            user_favorite_cosmetics.c.user_id == current_user.id,
            user_favorite_cosmetics.c.cosmetic_id == cosmetic_id,
        )
    ).first()

    if not already_exists:
        db.execute(
            user_favorite_cosmetics.insert().values(
                user_id=current_user.id,
                cosmetic_id=cosmetic_id,
            )
        )
        db.commit()
        logger.info(f"User {current_user.id} favorited cosmetic {cosmetic_id}")

    return {"message": "Added to favorites.", "cosmetic_id": cosmetic_id}


# ---------------------------------------------------------------------------
# DELETE /api/v1/favorites/{cosmetic_id}
# ---------------------------------------------------------------------------

@router.delete(
    "/{cosmetic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a cosmetic from favorites",
    description=(
        "Removes a cosmetic from the current authenticated user's favorites. "
        "Safe to call even if the item was not previously favorited."
    ),
)
def remove_favorite(cosmetic_id: int, current_user: CurrentUserDep, db: DBDep):
    """
    DELETE /api/v1/favorites/{cosmetic_id}

    Args:
        cosmetic_id (int): The ID of the cosmetic product to un-favorite.

    Returns:
        None (HTTP 204 No Content).
    """
    db.execute(
        user_favorite_cosmetics.delete().where(
            user_favorite_cosmetics.c.user_id == current_user.id,
            user_favorite_cosmetics.c.cosmetic_id == cosmetic_id,
        )
    )
    db.commit()
    logger.info(f"User {current_user.id} removed cosmetic {cosmetic_id} from favorites")
    return None
