"""
Domain Entities Module

Business entities with identity and lifecycle.
"""

from app.domain.entities.season_result import SeasonResult
from app.domain.entities.user import User
from app.domain.entities.history import RecommendationSession, RecommendationItem
from app.domain.entities.knowledge_base import Season, Color, SeasonColor, Brand, Category, CosmeticProduct, CosmeticSeasonMapping

__all__ = [
    "SeasonResult", 
    "User", 
    "RecommendationSession", 
    "RecommendationItem",
    "Season",
    "Color",
    "SeasonColor",
    "Brand",
    "Category",
    "CosmeticProduct",
    "CosmeticSeasonMapping"
]
