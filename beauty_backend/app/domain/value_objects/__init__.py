"""
Domain Value Objects Module

Immutable value objects representing core business concepts.
"""

from app.domain.value_objects.color_lab import ColorLAB
from app.domain.value_objects.seasonal_season import SeasonalSeason

__all__ = ["ColorLAB", "SeasonalSeason"]
