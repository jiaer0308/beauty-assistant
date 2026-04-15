#!/usr/bin/env python3
"""
Quiz Engine — Phase 3 Quiz Scoring Module

Converts the 9 user-supplied QuizData answers into per-season score
adjustments and fuses them with the existing image-derived scores.

Key design decisions
--------------------
- **Weighted Penalty** (not a hard veto): a quiz answer shifts season
  probabilities but never forces a score to zero.
- **Additive per question**: each question contributes independently.
- **1:1 Flutter Sync**: Uses exact strings from the Flutter onboarding quiz.
"""

import logging
from typing import Dict, Optional

from app.schemas.sca import QuizData

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Fusion weights (must sum to 1.0)
# ---------------------------------------------------------------------------
IMAGE_WEIGHT: float = 0.70
QUIZ_WEIGHT: float = 0.30

# ---------------------------------------------------------------------------
# Season groupings used by the mapping rules
# ---------------------------------------------------------------------------
_WARM_SEASONS = frozenset({
    "soft_autumn", "true_autumn", "dark_autumn",
    "light_spring", "true_spring", "bright_spring",
})
_COOL_SEASONS = frozenset({
    "light_summer", "true_summer", "soft_summer",
    "dark_winter", "true_winter", "bright_winter",
})
_DEEP_SEASONS = frozenset({
    "dark_autumn", "dark_winter",
})
_LIGHT_SEASONS = frozenset({
    "light_spring", "light_summer",
})
_CLEAR_SEASONS = frozenset({
    "bright_spring", "bright_winter",
})
_MUTED_SEASONS = frozenset({
    "soft_autumn", "soft_summer",
})

# All 12 season keys
ALL_SEASONS = _WARM_SEASONS | _COOL_SEASONS

# Per-question penalty / bonus magnitude
_VEIN_BONUS        = 0.40
_VEIN_PENALTY      = 0.25
_JEWELRY_BONUS     = 0.25
_JEWELRY_PENALTY   = 0.15
_SUN_BONUS         = 0.20
_SUN_PENALTY       = 0.10
_HAIR_DEPTH_BONUS  = 0.20
_HAIR_DEPTH_PENALTY= 0.10


class QuizEngine:
    """
    Converts user quiz answers into fused per-season scores.
    """

    def compute_quiz_adjustments(
        self,
        quiz: QuizData,
        image_scores: Dict[str, float],
    ) -> Dict[str, float]:
        """Fuse image scores with quiz-derived adjustments."""
        norm_image = _normalise(image_scores)
        quiz_adj = self._build_quiz_adjustment(quiz)

        fused: Dict[str, float] = {}
        for season in ALL_SEASONS:
            img = norm_image.get(season, 0.0)
            adj = quiz_adj.get(season, 0.0)
            fused[season] = IMAGE_WEIGHT * img + QUIZ_WEIGHT * _clamp(adj)

        return _normalise(fused)

    def compute_quiz_influence(
        self,
        quiz: QuizData,
        image_scores: Dict[str, float],
        fused_scores: Dict[str, float],
    ) -> float:
        """Return a 0–1 float estimating quiz influence."""
        norm_image = _normalise(image_scores)
        best_image = max(norm_image, key=norm_image.get)
        best_fused = max(fused_scores, key=fused_scores.get)

        if best_image != best_fused:
            return round(QUIZ_WEIGHT + 0.20, 2)
        
        delta = sum(
            abs(fused_scores.get(s, 0.0) - norm_image.get(s, 0.0))
            for s in ALL_SEASONS
        ) / len(ALL_SEASONS)
        return round(min(delta * 2, QUIZ_WEIGHT), 2)

    def _build_quiz_adjustment(self, quiz: QuizData) -> Dict[str, float]:
        """Accumulate per-question bonuses/penalties."""
        adj: Dict[str, float] = {s: 0.5 for s in ALL_SEASONS}

        self._apply_wrist_vein(quiz.wrist_vein, adj)
        self._apply_jewelry(quiz.jewelry, adj)
        self._apply_sun_reaction(quiz.sun_reaction, adj)
        self._apply_hair_color(quiz.hair_color, adj)

        if quiz.skin_type:
            logger.debug("skin_type=%s noted", quiz.skin_type)

        return adj

    @staticmethod
    def _apply_wrist_vein(answer: Optional[str], adj: Dict[str, float]) -> None:
        if not answer:
            return
        if answer == "Green or Olive":
            _boost(adj, _WARM_SEASONS, _VEIN_BONUS)
            _penalise(adj, _COOL_SEASONS, _VEIN_PENALTY)
        elif answer == "Blue or Purple":
            _boost(adj, _COOL_SEASONS, _VEIN_BONUS)
            _penalise(adj, _WARM_SEASONS, _VEIN_PENALTY)
        elif answer == "Mixed / Unsure":
            _boost(adj, _WARM_SEASONS, _VEIN_BONUS * 0.15)

    @staticmethod
    def _apply_jewelry(answer: Optional[str], adj: Dict[str, float]) -> None:
        if not answer:
            return
        if answer == "Yellow Gold":
            _boost(adj, _WARM_SEASONS, _JEWELRY_BONUS)
            _penalise(adj, _COOL_SEASONS, _JEWELRY_PENALTY)
        elif answer == "Silver / White Gold":
            _boost(adj, _COOL_SEASONS, _JEWELRY_BONUS)
            _penalise(adj, _WARM_SEASONS, _JEWELRY_PENALTY)
        elif answer == "Rose Gold":
            # Rose gold is often associated with neutral-warm
            _boost(adj, _WARM_SEASONS, _JEWELRY_BONUS * 0.1)

    @staticmethod
    def _apply_sun_reaction(answer: Optional[str], adj: Dict[str, float]) -> None:
        if not answer:
            return
        if answer == "Burn easily, rarely tan":
            _boost(adj, _COOL_SEASONS, _SUN_BONUS)
            _boost(adj, _LIGHT_SEASONS, _SUN_BONUS * 0.5)
        elif answer == "Tan easily, rarely burn":
            _boost(adj, _WARM_SEASONS, _SUN_BONUS)
            _boost(adj, _DEEP_SEASONS, _SUN_BONUS * 0.5)
        elif answer == "Burn first, then tan":
            # Intermediate
            _boost(adj, ALL_SEASONS, 0.0)

    @staticmethod
    def _apply_hair_color(answer: Optional[str], adj: Dict[str, float]) -> None:
        if not answer:
            return
        if answer in ("Black", "Warm Brown"):
            _boost(adj, _DEEP_SEASONS, _HAIR_DEPTH_BONUS)
            _penalise(adj, _LIGHT_SEASONS, _HAIR_DEPTH_PENALTY)
        elif answer in ("Ashy Blonde", "Golden Blonde"):
            _boost(adj, _LIGHT_SEASONS, _HAIR_DEPTH_BONUS)
            _penalise(adj, _DEEP_SEASONS, _HAIR_DEPTH_PENALTY)


def _boost(adj: Dict[str, float], seasons: frozenset, amount: float) -> None:
    for s in seasons:
        adj[s] = adj.get(s, 0.5) + amount


def _penalise(adj: Dict[str, float], seasons: frozenset, amount: float) -> None:
    for s in seasons:
        adj[s] = max(0.0, adj.get(s, 0.5) - amount)


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _normalise(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Normalise a score dict so values sum to 1.0 (probability distribution).

    Sum-normalisation is used rather than max-normalisation so that the
    relative gaps between seasons are preserved — a dominant season with
    0.9 vs. 0.1 for all others is immediately distinguishable from a
    near-tie at 0.18 vs 0.16.
    """
    if not scores:
        return {}
    total = sum(scores.values())
    if total == 0:
        return {k: 0.0 for k in scores}
    return {k: v / total for k, v in scores.items()}

