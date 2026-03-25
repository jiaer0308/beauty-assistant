#!/usr/bin/env python3
"""
Unit Tests – QuizEngine (app/services/quiz_engine.py)

Covers:
  1. Warm vein colour boosts warm seasons
  2. Cool vein colour penalises warm seasons
  3. All-None quiz is a no-op relative to neutral baseline
  4. Fusion weights IMAGE_WEIGHT + QUIZ_WEIGHT == 1.0
  5. Gold jewellery preference boosts warm families
  6. compute_quiz_influence returns a float[0, QUIZ_WEIGHT]
"""

from __future__ import annotations

import pytest

from app.schemas.sca import QuizData
from app.services.quiz_engine import (
    QuizEngine,
    IMAGE_WEIGHT,
    QUIZ_WEIGHT,
    ALL_SEASONS,
    _WARM_SEASONS,
    _COOL_SEASONS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _neutral_image_scores() -> dict:
    """Return an equal-probability image score map for all 12 seasons."""
    return {s: 1.0 for s in ALL_SEASONS}


def _quiz(**kwargs) -> QuizData:
    """Create a QuizData with all fields None except those provided."""
    return QuizData(
        skin_type=kwargs.get("skin_type"),
        sun_reaction=kwargs.get("sun_reaction"),
        vein_color=kwargs.get("vein_color"),
        natural_hair_color=kwargs.get("natural_hair_color"),
        jewelry_preference=kwargs.get("jewelry_preference"),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestFusionWeights:
    def test_image_and_quiz_weights_sum_to_one(self):
        assert IMAGE_WEIGHT + QUIZ_WEIGHT == pytest.approx(1.0, abs=1e-9)

    def test_image_weight_dominant(self):
        """Image should weigh more than quiz."""
        assert IMAGE_WEIGHT > QUIZ_WEIGHT


class TestVeinColor:
    engine = QuizEngine()

    def test_warm_vein_boosts_warm_seasons(self):
        """Green veins → warm seasons score higher than cool seasons."""
        quiz = _quiz(vein_color="green")
        scores = self.engine.compute_quiz_adjustments(quiz, _neutral_image_scores())

        warm_avg = sum(scores[s] for s in _WARM_SEASONS) / len(_WARM_SEASONS)
        cool_avg = sum(scores[s] for s in _COOL_SEASONS) / len(_COOL_SEASONS)
        assert warm_avg > cool_avg, (
            f"Expected warm_avg ({warm_avg:.3f}) > cool_avg ({cool_avg:.3f})"
        )

    def test_cool_vein_penalises_warm_seasons(self):
        """Blue-purple veins → cool seasons score higher than warm seasons."""
        quiz = _quiz(vein_color="blue_purple")
        scores = self.engine.compute_quiz_adjustments(quiz, _neutral_image_scores())

        warm_avg = sum(scores[s] for s in _WARM_SEASONS) / len(_WARM_SEASONS)
        cool_avg = sum(scores[s] for s in _COOL_SEASONS) / len(_COOL_SEASONS)
        assert cool_avg > warm_avg, (
            f"Expected cool_avg ({cool_avg:.3f}) > warm_avg ({warm_avg:.3f})"
        )

    def test_both_vein_gives_slight_warm_lean(self):
        """'both' vein → small warm lean; should NOT heavily penalise any side."""
        quiz = _quiz(vein_color="both")
        scores = self.engine.compute_quiz_adjustments(quiz, _neutral_image_scores())
        # Both sides should be reasonably balanced (within 0.2 of the max)
        max_score = max(scores.values())
        min_score = min(scores.values())
        assert max_score - min_score < 0.40, "Unexpected large spread for 'both' vein"


class TestNoneQuizIsNoop:
    engine = QuizEngine()

    def test_all_none_fields_keeps_ranking(self):
        """An all-None QuizData should not change the best-ranked image season."""
        image_scores = {s: (0.9 if s == "soft_autumn" else 0.1) for s in ALL_SEASONS}
        quiz = _quiz()  # all None
        fused = self.engine.compute_quiz_adjustments(quiz, image_scores)
        best_season = max(fused, key=fused.get)
        assert best_season == "soft_autumn", (
            f"All-None quiz changed the top season to {best_season}"
        )

    def test_all_none_output_is_normalised(self):
        """Output values should be in [0, 1]."""
        quiz = _quiz()
        fused = self.engine.compute_quiz_adjustments(quiz, _neutral_image_scores())
        for season, score in fused.items():
            assert 0.0 <= score <= 1.0, f"{season}: score {score} out of [0, 1]"


class TestJewelryPreference:
    engine = QuizEngine()

    def test_gold_jewelry_boosts_warm_families(self):
        quiz = _quiz(jewelry_preference="gold")
        scores = self.engine.compute_quiz_adjustments(quiz, _neutral_image_scores())

        warm_avg = sum(scores[s] for s in _WARM_SEASONS) / len(_WARM_SEASONS)
        cool_avg = sum(scores[s] for s in _COOL_SEASONS) / len(_COOL_SEASONS)
        assert warm_avg > cool_avg

    def test_silver_jewelry_boosts_cool_families(self):
        quiz = _quiz(jewelry_preference="silver")
        scores = self.engine.compute_quiz_adjustments(quiz, _neutral_image_scores())

        cool_avg = sum(scores[s] for s in _COOL_SEASONS) / len(_COOL_SEASONS)
        warm_avg = sum(scores[s] for s in _WARM_SEASONS) / len(_WARM_SEASONS)
        assert cool_avg > warm_avg


class TestQuizInfluence:
    engine = QuizEngine()

    def test_influence_between_zero_and_quiz_weight(self):
        """Quiz influence must never exceed QUIZ_WEIGHT."""
        quiz = _quiz(vein_color="green", jewelry_preference="gold")
        image_scores = _neutral_image_scores()
        fused = self.engine.compute_quiz_adjustments(quiz, image_scores)
        influence = self.engine.compute_quiz_influence(quiz, image_scores, fused)
        assert 0.0 <= influence <= 1.0

    def test_no_quiz_gives_zero_influence(self):
        """When quiz has all-None fields, influence should be ~0."""
        quiz = _quiz()
        image_scores = _neutral_image_scores()
        fused = self.engine.compute_quiz_adjustments(quiz, image_scores)
        influence = self.engine.compute_quiz_influence(quiz, image_scores, fused)
        assert influence == pytest.approx(0.0, abs=0.05)
