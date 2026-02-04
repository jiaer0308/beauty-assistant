#!/usr/bin/env python3
"""
Unit tests for domain layer components
"""

import pytest
from datetime import datetime

from app.domain import ColorLAB, SeasonalSeason, SeasonResult


class TestColorLAB:
    """Tests for ColorLAB value object"""
    
    def test_valid_color_creation(self):
        """Test creating valid ColorLAB instances"""
        color = ColorLAB(L=50.0, a=10.0, b=20.0)
        assert color.L == 50.0
        assert color.a == 10.0
        assert color.b == 20.0
    
    def test_color_immutability(self):
        """Test that ColorLAB is immutable"""
        color = ColorLAB(L=50.0, a=10.0, b=20.0)
        with pytest.raises(Exception):  # FrozenInstanceError
            color.L = 60.0
    
    def test_invalid_L_value(self):
        """Test L value validation"""
        with pytest.raises(ValueError, match="L must be between 0 and 100"):
            ColorLAB(L=150.0, a=0.0, b=0.0)
        
        with pytest.raises(ValueError, match="L must be between 0 and 100"):
            ColorLAB(L=-10.0, a=0.0, b=0.0)
    
    def test_invalid_a_value(self):
        """Test a value validation"""
        with pytest.raises(ValueError, match="a must be between -128 and 127"):
            ColorLAB(L=50.0, a=200.0, b=0.0)
    
    def test_invalid_b_value(self):
        """Test b value validation"""
        with pytest.raises(ValueError, match="b must be between -128 and 127"):
            ColorLAB(L=50.0, a=0.0, b=-200.0)
    
    def test_warm_color_detection(self):
        """Test warm color detection (b > 0)"""
        warm_color = ColorLAB(L=70.0, a=5.0, b=25.0)  # Positive b = yellow = warm
        assert warm_color.is_warm is True
        assert warm_color.is_cool is False
    
    def test_cool_color_detection(self):
        """Test cool color detection (b < 0)"""
        cool_color = ColorLAB(L=70.0, a=5.0, b=-15.0)  # Negative b = blue = cool
        assert cool_color.is_cool is True
        assert cool_color.is_warm is False
    
    def test_contrast_calculation(self):
        """Test contrast (ΔL) calculation"""
        skin = ColorLAB(L=70.0, a=5.0, b=18.0)  # Light skin
        hair = ColorLAB(L=15.0, a=0.0, b=0.0)   # Dark hair
        
        contrast = skin.contrast_with(hair)
        assert contrast == 55.0  # |70 - 15| = 55
    
    def test_to_tuple(self):
        """Test tuple conversion"""
        color = ColorLAB(L=50.0, a=10.0, b=-5.0)
        assert color.to_tuple() == (50.0, 10.0, -5.0)
    
    def test_string_representations(self):
        """Test __str__ and __repr__"""
        color = ColorLAB(L=70.0, a=5.0, b=20.0)
        
        # __str__ should be human-readable
        str_repr = str(color)
        assert "L=70.0" in str_repr
        assert "warm" in str_repr
        
        # __repr__ should be developer-friendly
        repr_str = repr(color)
        assert "ColorLAB" in repr_str


class TestSeasonalSeason:
    """Tests for SeasonalSeason enum"""
    
    def test_all_12_seasons_exist(self):
        """Test that all 12 seasons are defined"""
        seasons = list(SeasonalSeason)
        assert len(seasons) == 12
    
    def test_season_values(self):
        """Test that season values are correct"""
        assert SeasonalSeason.DEEP_WINTER.value == "deep_winter"
        assert SeasonalSeason.LIGHT_SPRING.value == "light_spring"
    
    def test_display_name(self):
        """Test display name generation"""
        assert SeasonalSeason.DEEP_WINTER.display_name == "Deep Winter"
        assert SeasonalSeason.CLEAR_SPRING.display_name == "Clear Spring"
    
    def test_family_detection(self):
        """Test season family detection"""
        assert SeasonalSeason.DEEP_WINTER.family == "Winter"
        assert SeasonalSeason.LIGHT_SUMMER.family == "Summer"
        assert SeasonalSeason.DEEP_AUTUMN.family == "Autumn"
        assert SeasonalSeason.CLEAR_SPRING.family == "Spring"
    
    def test_temperature_detection(self):
        """Test warm/cool detection"""
        # Cool seasons: Winter, Summer
        assert SeasonalSeason.DEEP_WINTER.is_cool is True
        assert SeasonalSeason.DEEP_WINTER.is_warm is False
        assert SeasonalSeason.LIGHT_SUMMER.is_cool is True
        
        # Warm seasons: Autumn, Spring
        assert SeasonalSeason.DEEP_AUTUMN.is_warm is True
        assert SeasonalSeason.DEEP_AUTUMN.is_cool is False
        assert SeasonalSeason.WARM_SPRING.is_warm is True
    
    def test_contrast_detection(self):
        """Test high/low contrast detection"""
        # High contrast: Winter, Autumn
        assert SeasonalSeason.DEEP_WINTER.has_high_contrast is True
        assert SeasonalSeason.DEEP_AUTUMN.has_high_contrast is True
        
        # Low contrast: Summer, Spring
        assert SeasonalSeason.LIGHT_SUMMER.has_high_contrast is False
        assert SeasonalSeason.LIGHT_SPRING.has_high_contrast is False


class TestSeasonResult:
    """Tests for SeasonResult entity"""
    
    @pytest.fixture
    def valid_result_data(self):
        """Fixture providing valid result data"""
        return {
            "season": SeasonalSeason.DEEP_AUTUMN,
            "confidence": 0.88,
            "contrast_score": 52.4,
            "skin_temperature": "warm",
            "skin_color": [210, 180, 160],
            "hair_color": [40, 30, 25],
            "eye_color": [85, 60, 40],
            "processing_time_ms": 1200,
            "lighting_quality": "good"
        }
    
    def test_valid_result_creation(self, valid_result_data):
        """Test creating valid SeasonResult"""
        result = SeasonResult(**valid_result_data)
        assert result.season == SeasonalSeason.DEEP_AUTUMN
        assert result.confidence == 0.88
        assert isinstance(result.timestamp, datetime)
    
    def test_invalid_confidence(self, valid_result_data):
        """Test confidence validation"""
        valid_result_data["confidence"] = 1.5
        with pytest.raises(ValueError, match="Confidence must be between 0 and 1"):
            SeasonResult(**valid_result_data)
    
    def test_invalid_contrast_score(self, valid_result_data):
        """Test contrast score validation"""
        valid_result_data["contrast_score"] = 150.0
        with pytest.raises(ValueError, match="Contrast score must be between 0 and 100"):
            SeasonResult(**valid_result_data)
    
    def test_invalid_skin_temperature(self, valid_result_data):
        """Test skin temperature validation"""
        valid_result_data["skin_temperature"] = "hot"
        with pytest.raises(ValueError, match="Skin temperature must be 'warm' or 'cool'"):
            SeasonResult(**valid_result_data)
    
    def test_invalid_color_length(self, valid_result_data):
        """Test RGB color length validation"""
        valid_result_data["skin_color"] = [255, 128]  # Only 2 components
        with pytest.raises(ValueError, match="skin_color must have 3 components"):
            SeasonResult(**valid_result_data)
    
    def test_invalid_color_range(self, valid_result_data):
        """Test RGB color range validation"""
        valid_result_data["skin_color"] = [300, 128, 64]  # 300 > 255
        with pytest.raises(ValueError, match="skin_color values must be 0-255"):
            SeasonResult(**valid_result_data)
    
    def test_invalid_lighting_quality(self, valid_result_data):
        """Test lighting quality validation"""
        valid_result_data["lighting_quality"] = "excellent"
        with pytest.raises(ValueError, match="Lighting quality must be"):
            SeasonResult(**valid_result_data)
    
    def test_negative_processing_time(self, valid_result_data):
        """Test processing time validation"""
        valid_result_data["processing_time_ms"] = -100
        with pytest.raises(ValueError, match="Processing time cannot be negative"):
            SeasonResult(**valid_result_data)
    
    def test_computed_properties(self, valid_result_data):
        """Test computed properties"""
        result = SeasonResult(**valid_result_data)
        
        assert result.display_name == "Deep Autumn"
        assert result.season_family == "Autumn"
        assert result.confidence_percentage == 88.0
    
    def test_to_dict(self, valid_result_data):
        """Test conversion to API response format"""
        result = SeasonResult(**valid_result_data)
        data = result.to_dict()
        
        # Check structure
        assert "result" in data
        assert "metrics" in data
        assert "debug_info" in data
        
        # Check result section
        assert data["result"]["season"] == "deep_autumn"
        assert data["result"]["display_name"] == "Deep Autumn"
        assert data["result"]["confidence"] == 0.88
        
        # Check metrics section
        assert data["metrics"]["contrast_score"] == 52.4
        assert data["metrics"]["skin_temperature"] == "warm"
        assert data["metrics"]["dominant_colors"]["skin"] == [210, 180, 160]
        
        # Check debug_info section
        assert data["debug_info"]["lighting_quality"] == "good"
        assert data["debug_info"]["processing_time_ms"] == 1200
    
    def test_string_representations(self, valid_result_data):
        """Test __str__ and __repr__"""
        result = SeasonResult(**valid_result_data)
        
        str_repr = str(result)
        assert "Deep Autumn" in str_repr
        assert "88%" in str_repr
        assert "warm" in str_repr
        
        repr_str = repr(result)
        assert "SeasonResult" in repr_str
        assert "deep_autumn" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
