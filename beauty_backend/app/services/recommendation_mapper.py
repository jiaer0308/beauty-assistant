#!/usr/bin/env python3
"""
Recommendation Mapper

Retrieves colour + cosmetic recommendations for a classified season
using an SQL database, replacing the legacy JSON-based lookup.

Design notes
------------
- Stateless implementation using SQLAlchemy Sessions.
- Uses ``joinedload`` to eager-load related brand and category data (N+1 prevention).
- ``get_recommendations`` raises a ``ValueError`` for unknown season keys.
"""

import logging
from typing import Any, Dict

from sqlalchemy.orm import Session, joinedload

from app.domain.entities.knowledge_base import (
    Season,
    SeasonColor,
    CategoryType,
    CosmeticSeasonMapping,
    CosmeticProduct,
    Category,
)

logger = logging.getLogger(__name__)


class CategoryID:
    CONCEALER = 1
    LIQUID_FOUNDATION = 2
    POWDER = 3
    HIGHLIGHTER = 4
    FOUNDATION = 5
    LIPSTICK = 6
    LIP_GLOSS = 7
    LIP_STAIN = 8
    BB_CC_CREAM = 9
    CONTOUR = 10
    CREAM = 11
    MINERAL = 12

class RecommendationMapper:
    """
    Retrieves colour + cosmetic recommendations for a classified season.
    """

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_recommendations(
        self, season_key: str, db: Session, quiz_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Return the recommendation block for ``season_key`` from the database.

        Parameters
        ----------
        season_key:
            A ``SeasonalSeason`` enum value string, e.g. ``"soft_autumn"``.
        db:
            The SQLAlchemy database session.
        quiz_data:
            Optional dictionary containing user quiz preferences like
            'foundation_coverage' and 'skin_type'.

        Returns
        -------
        dict with keys: ``best_colors``, ``neutral_colors``, ``avoid_colors``,
        ``cosmetics``.

        Raises
        ------
        ValueError:
            If ``season_key`` is not present in the database.
        """
        # 1. Season Lookup
        season = db.query(Season).filter(Season.name == season_key).first()
        if not season:
            logger.error("Unknown season key for recommendations: %s", season_key)
            raise ValueError(
                f"No recommendations found for season '{season_key}'."
            )

        # 2. Retrieve Colors
        best_colors = []
        neutral_colors = []
        avoid_colors = []
        
        # Use relationship defined in Season model
        # SeasonColor objects have .color relationship
        for season_color in season.colors:
            color_data = {
                "name": season_color.color.name,
                "hex": season_color.color.hex_code
            }
            if season_color.category_type == CategoryType.BEST:
                best_colors.append(color_data)
            elif season_color.category_type == CategoryType.NEUTRAL:
                neutral_colors.append(color_data)
            elif season_color.category_type == CategoryType.AVOID:
                avoid_colors.append(color_data)

        # 3. Retrieve Cosmetics with Eager Loading (N+1 prevention)
        cosmetics_query = (
            db.query(CosmeticProduct)
            .join(CosmeticSeasonMapping)
            .join(Category)
            .filter(
                CosmeticSeasonMapping.season_id == season.id,
                CosmeticProduct.is_active == True
            )
        )

        # Apply Quiz Filters
        # if quiz_data:
        #     # Coverage Filtering: If Sheer/Light, exclude heavy 'Foundation' category
        #     if quiz_data.get("foundation_coverage") == "Sheer/Light":
        #         cosmetics_query = cosmetics_query.filter(Category.name != "Foundation")
            
        #     # Skin Type Filtering: If Oily, exclude categories containing 'Cream'
        #     if quiz_data.get("skin_type") == "Oily":
        #         cosmetics_query = cosmetics_query.filter(~Category.name.like("%Cream%"))

        # Apply Quiz Filters
        if quiz_data:
            excluded_categories = set()

            skin_type = quiz_data.get("skin_type")
            if skin_type == "Oily":
                excluded_categories.update(["Cream", "BB/CC"])

        cosmetics_query = cosmetics_query.options(
            joinedload(CosmeticProduct.brand),
            joinedload(CosmeticProduct.category)
        )
        
        cosmetics_by_category = {}
        for product in cosmetics_query.all():
            cat_name = product.category.name
            if cat_name not in cosmetics_by_category:
                cosmetics_by_category[cat_name] = []
            
            if len(cosmetics_by_category[cat_name]) < 5:
                cosmetics_by_category[cat_name].append({
                    "category": cat_name,
                    "brand": product.brand.name,
                    "name": product.product_name,
                    "shade": product.shade_name,
                    "hex": product.hex_code or "",
                    "image_url": product.image_url or ""
                })

        # Flatten the grouped products back into a single list
        cosmetics = []
        for items in cosmetics_by_category.values():
            cosmetics.extend(items)

        return {
            "best_colors": best_colors,
            "neutral_colors": neutral_colors,
            "avoid_colors": avoid_colors,
            "cosmetics": cosmetics
        }


def get_recommendation_mapper() -> RecommendationMapper:
    """
    Singleton factory — returns a cached ``RecommendationMapper``.
    """
    return RecommendationMapper()
