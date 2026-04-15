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
from enum import IntEnum
from typing import Any, Dict

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.domain.entities.knowledge_base import (
    Season,
    SeasonColor,
    CategoryType,
    CosmeticSeasonMapping,
    CosmeticProduct,
    Category,
)

logger = logging.getLogger(__name__)


class CategoryID(IntEnum):
    """Maps cosmetic category names to their primary-key IDs in the ``categories`` table."""

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

        # Apply quiz-based filters
        if quiz_data:
            excluded_category_ids: set = set()
            # Tracks categories that should be visually boosted (sorted first) in the response.
            priority_category_ids: set = set()

            # 1. Skin Type
            skin_type = quiz_data.get("skin_type")
            if skin_type == "Oily":
                excluded_category_ids.update([CategoryID.CREAM, CategoryID.BB_CC_CREAM])
                priority_category_ids.update([CategoryID.POWDER, CategoryID.MINERAL, CategoryID.FOUNDATION, CategoryID.LIQUID_FOUNDATION])
            elif skin_type == "Dry":
                excluded_category_ids.update([CategoryID.POWDER, CategoryID.MINERAL])
                priority_category_ids.update([CategoryID.CREAM, CategoryID.BB_CC_CREAM, CategoryID.LIQUID_FOUNDATION])
            elif skin_type == "Combination":
                priority_category_ids.update([CategoryID.LIQUID_FOUNDATION, CategoryID.POWDER])
            elif skin_type == "Sensitive":
                priority_category_ids.update([CategoryID.MINERAL, CategoryID.BB_CC_CREAM])

            # 2. Foundation Coverage
            coverage = quiz_data.get("foundation_coverage")
            if coverage == "Sheer / Light":
                # Exclude heavy base products
                excluded_category_ids.update([CategoryID.CREAM, CategoryID.LIQUID_FOUNDATION])
            elif coverage == "Medium":
                # Exclude both ultra-light and ultra-heavy base products
                excluded_category_ids.update([CategoryID.POWDER, CategoryID.MINERAL, CategoryID.CREAM])
            elif coverage == "Full":
                # Exclude light-coverage products; force full-coverage options
                excluded_category_ids.update([CategoryID.BB_CC_CREAM, CategoryID.POWDER, CategoryID.MINERAL, CategoryID.FOUNDATION])
                priority_category_ids.update([CategoryID.CREAM, CategoryID.LIQUID_FOUNDATION, CategoryID.CONCEALER])

            # 3. Makeup Finish
            finish = quiz_data.get("makeup_finish")
            if finish == "Matte / Velvet":
                excluded_category_ids.update([CategoryID.HIGHLIGHTER, CategoryID.LIP_GLOSS])
                priority_category_ids.add(CategoryID.POWDER)
            elif finish == "Dewy / Glowy":
                excluded_category_ids.add(CategoryID.POWDER)
                priority_category_ids.update([CategoryID.HIGHLIGHTER, CategoryID.BB_CC_CREAM, CategoryID.LIP_GLOSS])

            # 4. Skin Concerns — force-include functional product categories
            concerns = quiz_data.get("skin_concerns") or []
            if any(c in concerns for c in ["Dark Circles", "Redness/Acne", "Pigmentation"]):
                priority_category_ids.add(CategoryID.CONCEALER)   # concealer is essential
            if "Dullness" in concerns:
                priority_category_ids.add(CategoryID.HIGHLIGHTER)  # highlighter to add radiance
            if "Large Pores" in concerns:
                excluded_category_ids.add(CategoryID.HIGHLIGHTER)  # highlighter accentuates pores
                priority_category_ids.add(CategoryID.POWDER)       # blurring powder is essential

            # 5. Lip Style (唇妆质地)
            lip_style = quiz_data.get("lip_style")
            if lip_style == "MLBB (Nudes/Balms)":
                excluded_category_ids.add(CategoryID.LIP_STAIN)
                priority_category_ids.update([CategoryID.LIP_GLOSS, CategoryID.LIPSTICK])
            elif lip_style == "Bold & Statement":
                priority_category_ids.update([CategoryID.LIPSTICK, CategoryID.LIP_STAIN])
            elif lip_style == "Fresh & Feminine":
                priority_category_ids.update([CategoryID.LIP_GLOSS, CategoryID.LIP_STAIN, CategoryID.LIPSTICK])

            # Database layer: apply blacklist exclusions before fetching
            if excluded_category_ids:
                cosmetics_query = cosmetics_query.filter(
                    ~CosmeticProduct.category_id.in_(list(excluded_category_ids))
                )

        cosmetics_query = cosmetics_query.options(
            joinedload(CosmeticProduct.brand),
            joinedload(CosmeticProduct.category)
        ).order_by(func.random())
        
        # In-memory assembly: group by category (max 5 per category), tag boosted items.
        cosmetics_by_category: Dict[str, list] = {}
        for product in cosmetics_query.all():
            cat_name = product.category.name
            cat_id = product.category_id

            if cat_name not in cosmetics_by_category:
                cosmetics_by_category[cat_name] = []

            if len(cosmetics_by_category[cat_name]) < 5:
                is_priority = bool(quiz_data and cat_id in priority_category_ids)

                cosmetics_by_category[cat_name].append({
                    "id": product.id,
                    "category": cat_name,
                    "category_id": cat_id,
                    "brand": product.brand.name,
                    "name": product.product_name,
                    "shade": product.shade_name,
                    "hex": product.hex_code or "",
                    "image_url": product.image_url or "",
                    "is_priority": is_priority,  # passed to frontend for visual highlighting
                })

        # Flatten category buckets into a single list
        cosmetics: list = []
        for items in cosmetics_by_category.values():
            cosmetics.extend(items)

        # Sort: priority (boosted) products appear first in the recommendation list
        cosmetics.sort(key=lambda x: x["is_priority"], reverse=True)

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
