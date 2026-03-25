#!/usr/bin/env python3
"""
Unit Tests – RecommendationMapper (app/services/recommendation_mapper.py)

Covers:
  1. All 12 SeasonalSeason values have entries in the knowledge base
  2. Each season has exactly 5 best, 5 neutral, and 5 avoid colours
  3. Each cosmetic entry has category, brand, shade, and hex fields
  4. Unknown season raises ValueError (not KeyError)
"""

from __future__ import annotations

import pytest

from app.domain.value_objects.seasonal_season import SeasonalSeason
from app.services.recommendation_mapper import RecommendationMapper


# ---------------------------------------------------------------------------
# Fixture – single mapper instance reused across all tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mapper() -> RecommendationMapper:
    return RecommendationMapper()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAllSeasonsPresent:
    def test_all_twelve_seasons_have_recommendations(self, mapper: RecommendationMapper):
        """Every SeasonalSeason enum value must be in the knowledge base."""
        for season_enum in SeasonalSeason:
            season_key = season_enum.value
            recs = mapper.get_recommendations(season_key)
            assert recs is not None, f"Missing recommendations for {season_key}"

    def test_mapper_keys_count(self, mapper: RecommendationMapper):
        """Knowledge base should have exactly 12 seasons."""
        assert len(mapper.all_season_keys()) == 12


class TestColorStructure:
    @pytest.mark.parametrize("season_enum", list(SeasonalSeason))
    def test_best_colors_count(self, mapper: RecommendationMapper, season_enum: SeasonalSeason):
        recs = mapper.get_recommendations(season_enum.value)
        assert len(recs["best_colors"]) == 5, (
            f"{season_enum.value}: expected 5 best_colors, got {len(recs['best_colors'])}"
        )

    @pytest.mark.parametrize("season_enum", list(SeasonalSeason))
    def test_neutral_colors_count(self, mapper: RecommendationMapper, season_enum: SeasonalSeason):
        recs = mapper.get_recommendations(season_enum.value)
        assert len(recs["neutral_colors"]) == 5, (
            f"{season_enum.value}: expected 5 neutral_colors"
        )

    @pytest.mark.parametrize("season_enum", list(SeasonalSeason))
    def test_avoid_colors_count(self, mapper: RecommendationMapper, season_enum: SeasonalSeason):
        recs = mapper.get_recommendations(season_enum.value)
        assert len(recs["avoid_colors"]) == 5, (
            f"{season_enum.value}: expected 5 avoid_colors"
        )

    @pytest.mark.parametrize("season_enum", list(SeasonalSeason))
    def test_color_swatches_have_name_and_hex(
        self, mapper: RecommendationMapper, season_enum: SeasonalSeason
    ):
        recs = mapper.get_recommendations(season_enum.value)
        for category in ("best_colors", "neutral_colors", "avoid_colors"):
            for swatch in recs[category]:
                assert "name" in swatch, f"{season_enum.value}/{category}: missing 'name'"
                assert "hex"  in swatch, f"{season_enum.value}/{category}: missing 'hex'"
                assert swatch["hex"].startswith("#"), (
                    f"{season_enum.value}/{category}: hex should start with #"
                )


class TestCosmeticsStructure:
    @pytest.mark.parametrize("season_enum", list(SeasonalSeason))
    def test_cosmetics_count(self, mapper: RecommendationMapper, season_enum: SeasonalSeason):
        recs = mapper.get_recommendations(season_enum.value)
        assert len(recs["cosmetics"]) == 5, (
            f"{season_enum.value}: expected 5 cosmetics"
        )

    @pytest.mark.parametrize("season_enum", list(SeasonalSeason))
    def test_cosmetics_fields(self, mapper: RecommendationMapper, season_enum: SeasonalSeason):
        recs = mapper.get_recommendations(season_enum.value)
        for product in recs["cosmetics"]:
            for field in ("category", "brand", "shade", "hex"):
                assert field in product, (
                    f"{season_enum.value}: cosmetic missing field '{field}' in {product}"
                )
            assert product["hex"].startswith("#"), (
                f"{season_enum.value}: cosmetic hex should start with #"
            )


class TestUnknownSeason:
    def test_invalid_season_raises_value_error(self, mapper: RecommendationMapper):
        with pytest.raises(ValueError, match="No recommendations found for season"):
            mapper.get_recommendations("unicorn_season")
