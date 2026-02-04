#!/usr/bin/env python3
"""
Unit tests for 12-season classifier
"""

import pytest
import numpy as np

from app.ml_engine.seasonal.classifier import SeasonalColorClassifier, SEASONAL_RULES
from app.domain import SeasonalSeason


class TestSeasonalClassifier:
    """Tests for 12-season classifier"""
    
    @pytest.fixture
    def classifier(self):
        """Create classifier instance"""
        return SeasonalColorClassifier()
    
    def test_classifier_initialization(self, classifier):
        """Test classifier initialization"""
        assert classifier.LIGHT_THRESHOLD == 65
        assert classifier.DARK_THRESHOLD == 35
        assert classifier.HIGH_CHROMA == 28
        assert classifier.LOW_CHROMA == 18
    
    def test_feature_extraction_warm_light(self, classifier):
        """Test feature extraction for warm, light coloring"""
        # Warm skin (high b/a ratio)
        skin_rgb = np.array([220, 190, 165])  # Peachy/warm
        
        # Light hair
        hair_rgb = np.array([200, 180, 150])  # Blonde
        
        # Light eyes
        eye_rgb = np.array([150, 170, 190])   # Blue
        
        from app.ml_engine.seasonal.color import rgb_to_lab
        skin_lab = rgb_to_lab(skin_rgb)
        hair_lab = rgb_to_lab(hair_rgb)
        eye_lab = rgb_to_lab(eye_rgb)
        
        features = classifier._extract_features(
            skin_rgb, skin_lab,
            hair_rgb, hair_lab,
            eye_rgb, eye_lab
        )
        
        # Should be warm (high b/a ratio)
        assert features["temperature"] in ["warm", "neutral"]
        
        # Hair is light (L > 60)
        assert features["value_category"] == "light"
    
    def test_feature_extraction_cool_dark(self, classifier):
        """Test feature extraction for cool, dark coloring"""
        # Cool skin (low b/a ratio - more pink than yellow)
        skin_rgb = np.array([210, 185, 185])  # Pinkish
        
        # Dark hair
        hair_rgb = np.array([40, 35, 30])     # Brown/black
        
        # Dark eyes
        eye_rgb = np.array([50, 40, 35])      # Brown
        
        from app.ml_engine.seasonal.color import rgb_to_lab
        skin_lab = rgb_to_lab(skin_rgb)
        hair_lab = rgb_to_lab(hair_rgb)
        eye_lab = rgb_to_lab(eye_rgb)
        
        features = classifier._extract_features(
            skin_rgb, skin_lab,
            hair_rgb, hair_lab,
            eye_rgb, eye_lab
        )
        
        # Should be cool or neutral
        assert features["temperature"] in ["cool", "neutral"]
        
        # Hair is dark (L < 30)
        assert features["value_category"] == "dark"
    
    def test_classify_light_spring(self, classifier):
        """Test classification for Light Spring (warm, light, low contrast)"""
        # Light Spring: Warm undertone, light hair/eyes, soft contrast
        skin_rgb = np.array([230, 200, 175])  # Warm, light skin
        hair_rgb = np.array([200, 180, 140])  # Golden blonde
        eye_rgb = np.array([160, 150, 130])   # Light hazel
        
        result = classifier.classify(skin_rgb, hair_rgb, eye_rgb)
        
        # Should classify as Spring family
        assert result.season.family == "Spring"
        
        # Should have reasonable confidence
        assert 0.3 <= result.confidence <= 1.0
    
    def test_classify_dark_winter(self, classifier):
        """Test classification for Dark Winter (cool, dark, high contrast)"""
        # Dark Winter: Cool undertone, very dark hair, high contrast
        skin_rgb = np.array([220, 195, 190])  # Fair, cool skin
        hair_rgb = np.array([30, 25, 20])     # Black hair
        eye_rgb = np.array([45, 35, 30])      # Dark brown eyes
        
        result = classifier.classify(skin_rgb, hair_rgb, eye_rgb)
        
        # Should classify as Winter family
        assert result.season.family == "Winter"
        
        # Should have reasonable confidence
        assert 0.3 <= result.confidence <= 1.0
   
    def test_classify_soft_autumn(self, classifier):
        """Test classification for Soft Autumn (warm, muted, low contrast)"""
        # Soft Autumn: Warm undertone, muted colors, low contrast
        skin_rgb = np.array([200, 170, 150])  # Warm, olive skin
        hair_rgb = np.array([120, 100, 80])   # Soft brown
        eye_rgb = np.array([100, 90, 70])     # Muted green-brown
        
        result = classifier.classify(skin_rgb, hair_rgb, eye_rgb)
        
        # Should classify as Autumn family
        assert result.season.family == "Autumn"
        
        # Should have reasonable confidence
        assert 0.3 <= result.confidence <= 1.0
    
    def test_classify_true_summer(self, classifier):
        """Test classification for True Summer (cool, soft, medium value)"""
        # True Summer: Cool undertone, soft colors, medium value
        skin_rgb = np.array([210, 190, 190])  # Cool, rose beige
        hair_rgb = np.array([140, 130, 120])  # Soft ash brown
        eye_rgb = np.array([130, 140, 150])   # Gray-blue
        
        result = classifier.classify(skin_rgb, hair_rgb, eye_rgb)
        
        # Should classify as Summer family
        assert result.season.family == "Summer"
        
        # Should have reasonable confidence
        assert 0.3 <= result.confidence <= 1.0
    
    def test_all_seasons_have_rules(self):
        """Test that all 12 seasons have rules defined"""
        assert len(SEASONAL_RULES) == 12
        
        # Check all families are represented
        families = {
            rule["priority"] for rule in SEASONAL_RULES.values()
        }
        
        # Each family should have Temperature, Value, and Chroma priorities
        priorities = {
            rule["priority"] for rule in SEASONAL_RULES.values()
        }
        assert "Temperature" in priorities
        assert "Value" in priorities
        assert "Chroma" in priorities
    
    def test_score_calculation(self, classifier):
        """Test season scoring logic"""
        # Perfect match features for True Winter
        features = {
            "temperature": "cool",
            "value_category": "medium",
            "chroma_level": "high",
            "contrast_level": "high",
            "raw_values": {
                "skin_L": 70,
                "hair_L": 25,
                "contrast": 45
            }
        }
        
        rules = SEASONAL_RULES["True Winter"]
        score = classifier._calculate_season_score(features, rules, "True Winter")
        
        # Should get high score for good match
        assert score >= 60  # Out of 100
    
    def test_name_to_enum_conversion(self, classifier):
        """Test season name to enum conversion with mapping"""
        # Test conversions with mapping
        # "Dark Winter" maps to "Deep Winter" -> DEEP_WINTER
        assert classifier._name_to_enum("Dark Winter") == SeasonalSeason.DEEP_WINTER
        
        # "Bright Spring" maps to "Clear Spring" -> CLEAR_SPRING
        assert classifier._name_to_enum("Bright Spring") == SeasonalSeason.CLEAR_SPRING
        
        # "Soft Summer" stays the same -> SOFT_SUMMER
        assert classifier._name_to_enum("Soft Summer") == SeasonalSeason.SOFT_SUMMER
        
        # "True Autumn" maps to "Warm Autumn" -> WARM_AUTUMN
        assert classifier._name_to_enum("True Autumn") == SeasonalSeason.WARM_AUTUMN


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
