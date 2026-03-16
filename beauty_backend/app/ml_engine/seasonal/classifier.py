#!/usr/bin/env python3
"""
12-Season Classifier - Phase 3 of SCA Pipeline

Implements decision tree classification for 12 seasonal color types
based on skin, hair, and eye colors.

Classification Features:
- Temperature (warm/cool/neutral) - from skin LAB a*/b* ratio
- Value (lightness) - from hair/eye L*
- Chroma (saturation) - from skin/hair/eye
- Contrast - difference between skin and hair lightness

Season Families:
- Winter: Cool, Dark, Clear
- Spring: Warm, Light, Clear
- Summer: Cool, Light, Muted
- Autumn: Warm, Dark, Muted
"""

import numpy as np
from typing import Dict, Tuple
import logging

from app.domain import SeasonalSeason, SeasonResult
from app.ml_engine.seasonal.color import (
    rgb_to_lab,
    calculate_chroma,
    get_skin_temperature_label
)


logger = logging.getLogger(__name__)


# Mapping from user-friendly names to enum names
# User provides: "Dark Winter", "True Winter", "Bright Winter"
# Enum has: "Deep Winter", "Cool Winter", "Clear Winter"
NAME_MAPPING = {
    # WINTER
    "Dark Winter": "Deep Winter",
    "True Winter": "Cool Winter", 
    "Bright Winter": "Clear Winter",
    
    # SPRING
    "Light Spring": "Light Spring",  # Same
    "True Spring": "Warm Spring",
    "Bright Spring": "Clear Spring",
    
    # SUMMER
    "Light Summer": "Light Summer",  # Same
    "True Summer": "Cool Summer",
    "Soft Summer": "Soft Summer",    # Same
    
    # AUTUMN
    "Dark Autumn": "Deep Autumn",
    "True Autumn": "Warm Autumn",
    "Soft Autumn": "Soft Autumn"     # Same
}


# 12-Season Classification Rules (using user-friendly names)
SEASONAL_RULES = {
    # --- WINTER FAMILY (Cool, Dark, Clear) ---
    "Dark Winter": {  # Maps to Deep Winter
        "undertone": "Neutral-Cool",
        "value_logic": "Dark",      # Hair L < 30, Eye L < 30
        "chroma_logic": "Medium",
        "contrast": "High",         # Skin L - Hair L > 50
        "priority": "Value"         # Deep is dominant
    },
    "True Winter": {  # Maps to Cool Winter
        "undertone": "Cool",        # Lab b is very low relative to a
        "value_logic": "Medium-Dark",
        "chroma_logic": "High",
        "contrast": "High",
        "priority": "Temperature"   # Cool is dominant
    },
    "Bright Winter": {  # Maps to Clear Winter
        "undertone": "Neutral-Cool",
        "value_logic": "Medium",
        "chroma_logic": "Highest",  # Eye clarity is very high
        "contrast": "Very High",    # Skin L very high, Hair L very low
        "priority": "Chroma"        # Clarity is dominant
    },

    # --- SPRING FAMILY (Warm, Light, Clear) ---
    "Bright Spring": {  # Maps to Clear Spring
        "undertone": "Neutral-Warm",
        "value_logic": "Medium",
        "chroma_logic": "Highest",
        "contrast": "High",
        "priority": "Chroma"
    },
    "True Spring": {  # Maps to Warm Spring
        "undertone": "Warm",        # Lab b is high
        "value_logic": "Medium-Light",
        "chroma_logic": "High",
        "contrast": "Medium",
        "priority": "Temperature"
    },
    "Light Spring": {  # Same name
        "undertone": "Neutral-Warm",
        "value_logic": "Light",     # Hair L > 60, Eye L > 60
        "chroma_logic": "Medium",
        "contrast": "Low",
        "priority": "Value"
    },

    # --- SUMMER FAMILY (Cool, Light, Muted) ---
    "Light Summer": {  # Same name
        "undertone": "Neutral-Cool",
        "value_logic": "Light",     # Hair L > 60
        "chroma_logic": "Low",
        "contrast": "Low",
        "priority": "Value"
    },
    "True Summer": {  # Maps to Cool Summer
        "undertone": "Cool",
        "value_logic": "Medium-Light",
        "chroma_logic": "Medium",
        "contrast": "Medium-Low",   # Soft contrast
        "priority": "Temperature"
    },
    "Soft Summer": {  # Same name
        "undertone": "Neutral-Cool",
        "value_logic": "Medium",
        "chroma_logic": "Lowest",   # Greyish hair/eyes (Low chroma)
        "contrast": "Low",          # Blended appearance
        "priority": "Chroma"        # Muted is dominant
    },

    # --- AUTUMN FAMILY (Warm, Dark, Muted) ---
    "Soft Autumn": {  # Same name
        "undertone": "Neutral-Warm",
        "value_logic": "Medium",
        "chroma_logic": "Lowest",   # Earthy tones
        "contrast": "Low",
        "priority": "Chroma"
    },
    "True Autumn": {  # Maps to Warm Autumn
        "undertone": "Warm",
        "value_logic": "Medium-Dark",
        "chroma_logic": "Medium",
        "contrast": "Medium",
        "priority": "Temperature"
    },
    "Dark Autumn": {  # Maps to Deep Autumn
        "undertone": "Neutral-Warm",
        "value_logic": "Dark",      # Hair L < 30
        "chroma_logic": "Medium",
        "contrast": "High",
        "priority": "Value"
    }
}


class SeasonalColorClassifier:
    """
    12-Season Color Analysis Classifier
    
    Uses decision tree based on:
    1. Temperature (warm/cool/neutral)
    2. Value (light/medium/dark)
    3. Chroma (high/medium/low)
    4. Contrast (high/medium/low)
    """
    
    def __init__(self):
        """Initialize classifier with thresholds"""
        # Value (Lightness) thresholds
        self.LIGHT_THRESHOLD = 65      # (Adjusted) L > 65 = light
        self.DARK_THRESHOLD = 42      # (Adjusted) L < 35 = dark
        
        # Chroma thresholds
        self.HIGH_CHROMA = 28          # (Adjusted) C* > 28 = high
        self.LOW_CHROMA = 18           # (Adjusted) C* < 18 = muted/low
        
        # Contrast thresholds
        self.HIGH_CONTRAST = 45        # (Adjusted) Easier to hit high contrast
        self.LOW_CONTRAST = 20         
        
        logger.info("SeasonalColorClassifier initialized with adjusted thresholds")
    
    def classify(
        self,
        skin_rgb: np.ndarray,
        hair_rgb: np.ndarray,
        eye_rgb: np.ndarray
    ) -> SeasonResult:
        """
        Classify into one of 12 seasonal color types
        
        Args:
            skin_rgb: Dominant skin color [R, G, B]
            hair_rgb: Dominant hair color [R, G, B]
            eye_rgb: Dominant eye color [R, G, B]
        
        Returns:
            SeasonResult with classified season and confidence
        """
        # Step 1: Convert to LAB color space
        skin_lab = rgb_to_lab(skin_rgb)
        hair_lab = rgb_to_lab(hair_rgb)
        eye_lab = rgb_to_lab(eye_rgb)
        
        # Step 2: Extract features
        features = self._extract_features(
            skin_rgb, skin_lab,
            hair_rgb, hair_lab,
            eye_rgb, eye_lab
        )
        
        logger.debug(f"Extracted features: {features}")
        
        # Step 3: Decision tree classification
        season, confidence = self._decision_tree_classify(features)
        
        # Step 4: Create result with all required fields
        result = SeasonResult(
            season=season,
            confidence=confidence,
            contrast_score=features["raw_values"]["contrast"],
            skin_temperature=features["temperature"],
            skin_color=skin_rgb.tolist() if isinstance(skin_rgb, np.ndarray) else skin_rgb,
            hair_color=hair_rgb.tolist() if isinstance(hair_rgb, np.ndarray) else hair_rgb,
            eye_color=eye_rgb.tolist() if isinstance(eye_rgb, np.ndarray) else eye_rgb,
            processing_time_ms=0,  # Will be set by service layer
            lighting_quality="acceptable"  # Will be set by service layer
        )
        
        logger.info(
            f"Classification: {season.value} "
            f"(confidence: {confidence:.1%})"
        )
        
        return result
    
    def _extract_features(
        self,
        skin_rgb: np.ndarray, skin_lab: np.ndarray,
        hair_rgb: np.ndarray, hair_lab: np.ndarray,
        eye_rgb: np.ndarray, eye_lab: np.ndarray
    ) -> Dict[str, any]:
        """
        Extract classification features from colors
        
        Returns dictionary with:
        - temperature: "warm", "cool", or "neutral"
        - value_category: "light", "medium", or "dark"
        - chroma_level: "high", "medium", or "low"
        - contrast_level: "high", "medium", or "low"
        - raw_values: L, a, b, chroma values
        """
        # Temperature from skin (using a/b ratio)
        temperature = get_skin_temperature_label(skin_lab[1], skin_lab[2])
        
        # Value (lightness) from hair
        hair_lightness = hair_lab[0]
        if hair_lightness > self.LIGHT_THRESHOLD:
            value_category = "light"
        elif hair_lightness < self.DARK_THRESHOLD:
            value_category = "dark"
        else:
            value_category = "medium"
        
        # Chroma (saturation) - average of hair and eye
        hair_chroma = calculate_chroma(hair_rgb)
        eye_chroma = calculate_chroma(eye_rgb)
        avg_chroma = (hair_chroma + eye_chroma) / 2
        
        if avg_chroma > self.HIGH_CHROMA:
            chroma_level = "high"
        elif avg_chroma < self.LOW_CHROMA:
            chroma_level = "low"
        else:
            chroma_level = "medium"
        
        # Contrast (skin - hair lightness difference)
        contrast = abs(skin_lab[0] - hair_lab[0])
        
        if contrast > self.HIGH_CONTRAST:
            contrast_level = "high"
        elif contrast < self.LOW_CONTRAST:
            contrast_level = "low"
        else:
            contrast_level = "medium"
        
        return {
            "temperature": temperature,
            "value_category": value_category,
            "chroma_level": chroma_level,
            "contrast_level": contrast_level,
            "raw_values": {
                "skin_L": skin_lab[0],
                "skin_a": skin_lab[1],
                "skin_b": skin_lab[2],
                "hair_L": hair_lab[0],
                "eye_L": eye_lab[0],
                "hair_chroma": hair_chroma,
                "eye_chroma": eye_chroma,
                "contrast": contrast
            }
        }
    
    def _decision_tree_classify(
        self,
        features: Dict[str, any]
    ) -> Tuple[SeasonalSeason, float]:
        """
        Decision tree classification based on features
        
        Primary split: Temperature (warm/cool/neutral)
        Secondary splits: Value, Chroma, Contrast
        
        Returns:
            (season, confidence)
        """
        temp = features["temperature"]
        value = features["value_category"]
        chroma = features["chroma_level"]
        contrast = features["contrast_level"]
        raw = features["raw_values"]
        
        # Score all seasons and pick the best match
        scores = {}
        
        for season_name, rules in SEASONAL_RULES.items():
            score = self._calculate_season_score(
                features, rules, season_name
            )
            scores[season_name] = score
        
        # Get best matching season
        best_season_name = max(scores, key=scores.get)
        best_score = scores[best_season_name]
        
        # Convert name to enum
        season_enum = self._name_to_enum(best_season_name)
        
        # Calculate confidence (0-1 scale)
        # Higher confidence if score is much better than second-best
        sorted_scores = sorted(scores.values(), reverse=True)
        if len(sorted_scores) > 1:
            score_margin = sorted_scores[0] - sorted_scores[1]
            confidence = min(0.95, 0.5 + score_margin / 20)  # Base 50% + margin bonus
        else:
            confidence = best_score / 100
        
        logger.debug(f"Season scores: {scores}")
        logger.debug(f"Best: {best_season_name} (score: {best_score:.1f}, confidence: {confidence:.1%})")
        
        return season_enum, confidence
    
    def _calculate_season_score(
        self,
        features: Dict[str, any],
        rules: Dict[str, str],
        season_name: str
    ) -> float:
        """
        Calculate score with Fuzzy Logic (Partial Credit).
        Avoids strict 0-point penalties for borderline cases.
        """
        score = 0.0
        
        # Helper: Scoring map for partial matches
        # 30pts max for Primary traits, 20pts max for Secondary
        
        # --- 1. TEMPERATURE (Max 30) ---
        undertone = rules["undertone"]
        actual_temp = features["temperature"]
        
        if undertone == "Warm":
            if actual_temp == "warm": score += 30
            elif actual_temp == "neutral": score += 10 # Partial credit
        elif undertone == "Cool":
            if actual_temp == "cool": score += 30
            elif actual_temp == "neutral": score += 10
        elif "Neutral" in undertone:
            # Neutral seasons accept their leaning side better
            if actual_temp == "neutral": score += 30
            elif (undertone == "Neutral-Warm" and actual_temp == "warm"): score += 20
            elif (undertone == "Neutral-Cool" and actual_temp == "cool"): score += 20
            # Penalty for opposite temp is implicit (0 points)

        # --- 2. VALUE (Max 25) ---
        target_value = rules["value_logic"]
        actual_value = features["value_category"]
        
        # Perfect Match
        if (target_value == "Light" and actual_value == "light") or \
           (target_value == "Dark" and actual_value == "dark") or \
           (target_value == "Medium" and actual_value == "medium"):
            score += 25
        
        # Partial Match (Adjacent)
        elif "Medium" in target_value: # Target is Medium-ish
            # If target is Medium-Light but we are Light -> Good match
            if target_value == "Medium-Light" and actual_value == "light": score += 20
            elif target_value == "Medium-Dark" and actual_value == "dark": score += 20
            # If target is pure Medium, but we are Light/Dark -> Partial
            elif target_value == "Medium": score += 10
        
        # Soft boundary handling for Light/Dark targets
        elif target_value == "Light" and actual_value == "medium": score += 10
        elif target_value == "Dark" and actual_value == "medium": score += 10

        # --- 3. CHROMA (Max 25) ---
        target_chroma = rules["chroma_logic"]
        actual_chroma = features["chroma_level"]
        
        if target_chroma == "Highest" or target_chroma == "High":
            if actual_chroma == "high": score += 25
            elif actual_chroma == "medium": score += 10
            
        elif target_chroma == "Medium":
            if actual_chroma == "medium": score += 25
            elif actual_chroma == "high": score += 10
            elif actual_chroma == "low": score += 10
            
        elif target_chroma == "Low" or target_chroma == "Lowest":
            if actual_chroma == "low": score += 25
            elif actual_chroma == "medium": score += 10 # Critical for Soft Autumn!

        # --- 4. CONTRAST (Max 20) ---
        target_contrast = rules["contrast"]
        actual_contrast = features["contrast_level"]
        
        if "Very High" in target_contrast or "High" in target_contrast:
            if actual_contrast == "high": score += 20
            elif actual_contrast == "medium": score += 10
            
        elif "Medium" in target_contrast:
            if actual_contrast == "medium": score += 20
            elif actual_contrast != "medium": score += 5 # Loose penalty
            
        elif "Low" in target_contrast:
            if actual_contrast == "low": score += 20
            elif actual_contrast == "medium": score += 10

        # --- 5. PRIORITY BONUS (Tie-Breaker) ---
        # If the season's defining characteristic matches perfectly, give a bonus
        priority = rules["priority"]
        
        if priority == "Temperature":
            if (undertone == "Warm" and actual_temp == "warm") or \
               (undertone == "Cool" and actual_temp == "cool"):
                score += 5
                
        elif priority == "Value":
            if (target_value == "Light" and actual_value == "light") or \
               (target_value == "Dark" and actual_value == "dark"):
                score += 5
                
        elif priority == "Chroma":
            # Critical for Soft Autumn (Priority = Chroma)
            # Only give bonus if we strictly hit the target
            if (target_chroma in ["Low", "Lowest"] and actual_chroma == "low") or \
               (target_chroma in ["High", "Highest"] and actual_chroma == "high"):
                score += 5

        return score
    
    def _name_to_enum(self, season_name: str) -> SeasonalSeason:
        """
        Convert season name to SeasonalSeason enum
        
        Maps user-friendly names to enum names:
        "Dark Winter" -> "Deep Winter" -> SeasonalSeason.DEEP_WINTER
        "True Winter" -> "Cool Winter" -> SeasonalSeason.COOL_WINTER
        etc.
        """
        # Map to enum name if needed
        enum_name_friendly = NAME_MAPPING.get(season_name, season_name)
        
        # Convert to enum format (spaces to underscores, uppercase)
        enum_name = enum_name_friendly.upper().replace(" ", "_")
        
        try:
            return SeasonalSeason[enum_name]
        except KeyError:
            logger.error(f"Unknown season name: {season_name} (mapped to {enum_name})")
            # Default to Cool Winter if parsing fails
            return SeasonalSeason.COOL_WINTER
