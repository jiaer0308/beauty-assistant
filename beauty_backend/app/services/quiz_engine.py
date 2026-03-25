#!/usr/bin/env python3
"""
Quiz Engine — Phase 3 Quiz Scoring Module

Converts the five user-supplied QuizData answers into per-season score
adjustments and fuses them with the existing image-derived scores using
a configurable weighted blend:

    final_score[season] = IMAGE_WEIGHT × image_score[season]
                        + QUIZ_WEIGHT  × quiz_adj[season]

Key design decisions
--------------------
- **Weighted Penalty** (not a hard veto): a quiz answer shifts season
  probabilities but never forces a score to zero.  High image confidence
  for a particular season can still override quiz signals.
- **Additive per question**: each of the five questions contributes
  independently; a `None` answer is a no-op (contributes 0).
- **Family-level logic**: answers map to season *families* (Warm/Cool)
  and optionally to specific depth tiers (Light/Deep).

Season families
---------------
Warm: soft_autumn, warm_autumn, deep_autumn, light_spring, warm_spring, clear_spring
Cool: light_summer, cool_summer, soft_summer, deep_winter, cool_winter, clear_winter
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
    "soft_autumn", "warm_autumn", "deep_autumn",
    "light_spring", "warm_spring", "clear_spring",
})
_COOL_SEASONS = frozenset({
    "light_summer", "cool_summer", "soft_summer",
    "deep_winter", "cool_winter", "clear_winter",
})
_DEEP_SEASONS = frozenset({
    "deep_autumn", "deep_winter",
})
_LIGHT_SEASONS = frozenset({
    "light_spring", "light_summer",
})
_CLEAR_SEASONS = frozenset({
    "clear_spring", "clear_winter",
})
_MUTED_SEASONS = frozenset({
    "soft_autumn", "soft_summer",
})

# All 12 season keys
ALL_SEASONS = _WARM_SEASONS | _COOL_SEASONS

# Per-question penalty / bonus magnitude  (max 1.0 means ±100 pp swing)
_VEIN_BONUS        = 0.40   # strong signal
_VEIN_PENALTY      = 0.25   # weighted penalty (not a veto)
_JEWELRY_BONUS     = 0.25
_JEWELRY_PENALTY   = 0.15
_SUN_BONUS         = 0.20
_SUN_PENALTY       = 0.10
_HAIR_DEPTH_BONUS  = 0.20
_HAIR_DEPTH_PENALTY= 0.10


class QuizEngine:
    """
    Converts user quiz answers into fused per-season scores.

    Usage::

        engine = QuizEngine()
        fused = engine.compute_quiz_adjustments(quiz_data, image_scores)
        best_season = max(fused, key=fused.get)
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute_quiz_adjustments(
        self,
        quiz: QuizData,
        image_scores: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Fuse image scores with quiz-derived adjustments.

        Parameters
        ----------
        quiz:
            Pydantic ``QuizData`` object from the API request.
        image_scores:
            Dict mapping season key → raw score (any positive numeric range).
            Values do **not** need to be normalised; normalisation is done
            inside this method.

        Returns
        -------
        Dict[str, float]
            Fused scores in the same key-space, normalised to [0, 1].
        """
        # 1. Normalise image scores → [0, 1]
        norm_image = _normalise(image_scores)

        # 2. Build quiz adjustment map
        quiz_adj = self._build_quiz_adjustment(quiz)

        # 3. Weighted fusion
        fused: Dict[str, float] = {}
        for season in ALL_SEASONS:
            img = norm_image.get(season, 0.0)
            adj = quiz_adj.get(season, 0.0)
            fused[season] = IMAGE_WEIGHT * img + QUIZ_WEIGHT * _clamp(adj)

        # 4. Re-normalise so the best season clearly wins
        fused = _normalise(fused)

        logger.debug(
            "QuizEngine fusion: top-3 = %s",
            sorted(fused.items(), key=lambda x: x[1], reverse=True)[:3],
        )
        return fused

    def compute_quiz_influence(
        self,
        quiz: QuizData,
        image_scores: Dict[str, float],
        fused_scores: Dict[str, float],
    ) -> float:
        """
        Return a 0–1 float estimating how much the quiz *shifted* the result
        vs. pure image analysis.  Used for the ``quiz_influence`` response field.
        """
        norm_image = _normalise(image_scores)
        best_image   = max(norm_image, key=norm_image.get)
        best_fused   = max(fused_scores, key=fused_scores.get)

        # If the top season changed, influence is high; otherwise proportional
        if best_image != best_fused:
            return round(QUIZ_WEIGHT + 0.20, 2)   # significant shift
        # Measure score perturbation magnitude
        delta = sum(
            abs(fused_scores.get(s, 0.0) - norm_image.get(s, 0.0))
            for s in ALL_SEASONS
        ) / len(ALL_SEASONS)
        return round(min(delta * 2, QUIZ_WEIGHT), 2)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_quiz_adjustment(self, quiz: QuizData) -> Dict[str, float]:
        """
        Accumulate per-question bonuses/penalties into a score map.

        Each populated quiz field adds to the map independently; ``None``
        values are skipped entirely.
        """
        adj: Dict[str, float] = {s: 0.5 for s in ALL_SEASONS}  # neutral baseline

        self._apply_vein_color(quiz.vein_color, adj)
        self._apply_jewelry_preference(quiz.jewelry_preference, adj)
        self._apply_sun_reaction(quiz.sun_reaction, adj)
        self._apply_natural_hair_color(quiz.natural_hair_color, adj)
        # skin_type currently used for logging; reserved for future cosmetics filter
        if quiz.skin_type:
            logger.debug("skin_type=%s noted (used for cosmetics filtering later)", quiz.skin_type)

        return adj

    # --- Individual question handlers ---

    @staticmethod
    def _apply_vein_color(answer: Optional[str], adj: Dict[str, float]) -> None:
        """
        Vein colour is the strongest undertone signal.

        - ``green``       → warm undertone
        - ``blue_purple`` → cool undertone
        - ``both``        → slight warm lean (both is more common in warm-neutral)
        """
        if not answer:
            return
        if answer == "green":
            _boost(adj, _WARM_SEASONS, _VEIN_BONUS)
            _penalise(adj, _COOL_SEASONS, _VEIN_PENALTY)
        elif answer == "blue_purple":
            _boost(adj, _COOL_SEASONS, _VEIN_BONUS)
            _penalise(adj, _WARM_SEASONS, _VEIN_PENALTY)
        elif answer == "both":
            # Neutral — very slight warm lean
            _boost(adj, _WARM_SEASONS, _VEIN_BONUS * 0.15)

    @staticmethod
    def _apply_jewelry_preference(answer: Optional[str], adj: Dict[str, float]) -> None:
        """
        Gold flatters warm, silver flatters cool.
        """
        if not answer:
            return
        if answer == "gold":
            _boost(adj, _WARM_SEASONS, _JEWELRY_BONUS)
            _penalise(adj, _COOL_SEASONS, _JEWELRY_PENALTY)
        elif answer == "silver":
            _boost(adj, _COOL_SEASONS, _JEWELRY_BONUS)
            _penalise(adj, _WARM_SEASONS, _JEWELRY_PENALTY)
        # "both" → no adjustment

    @staticmethod
    def _apply_sun_reaction(answer: Optional[str], adj: Dict[str, float]) -> None:
        """
        Users who always burn tend to have cool/light undertones.
        Users who tan easily tend to have warm undertones.
        """
        if not answer:
            return
        if answer == "always_burn":
            _boost(adj, _COOL_SEASONS, _SUN_BONUS)
            _boost(adj, _LIGHT_SEASONS, _SUN_BONUS * 0.5)
        elif answer == "tan_easily":
            _boost(adj, _WARM_SEASONS, _SUN_BONUS)
            _boost(adj, _DEEP_SEASONS, _SUN_BONUS * 0.5)
        # "rarely_burn" → neutral

    @staticmethod
    def _apply_natural_hair_color(answer: Optional[str], adj: Dict[str, float]) -> None:
        """
        Natural hair colour is a proxy for depth and warmth.
        """
        if not answer:
            return
        if answer in ("black", "dark_brown"):
            _boost(adj, _DEEP_SEASONS, _HAIR_DEPTH_BONUS)
            _penalise(adj, _LIGHT_SEASONS, _HAIR_DEPTH_PENALTY)
        elif answer in ("blonde", "light_brown"):
            _boost(adj, _LIGHT_SEASONS, _HAIR_DEPTH_BONUS)
            _penalise(adj, _DEEP_SEASONS, _HAIR_DEPTH_PENALTY)
        elif answer == "red":
            # Red hair is almost exclusively warm
            _boost(adj, _WARM_SEASONS, _HAIR_DEPTH_BONUS)
            _boost(adj, frozenset({"warm_autumn", "warm_spring"}), _HAIR_DEPTH_BONUS * 0.5)
        # grey → no strong adjustment


# ---------------------------------------------------------------------------
# Stateless math helpers
# ---------------------------------------------------------------------------

def _boost(adj: Dict[str, float], seasons: frozenset, amount: float) -> None:
    for s in seasons:
        adj[s] = adj.get(s, 0.5) + amount


def _penalise(adj: Dict[str, float], seasons: frozenset, amount: float) -> None:
    for s in seasons:
        adj[s] = max(0.0, adj.get(s, 0.5) - amount)


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _normalise(scores: Dict[str, float]) -> Dict[str, float]:
    """Linearly scale so max value == 1.0.  Safe for empty / all-zero maps."""
    if not scores:
        return {}
    max_val = max(scores.values())
    if max_val == 0:
        return {k: 0.0 for k in scores}
    return {k: v / max_val for k, v in scores.items()}
