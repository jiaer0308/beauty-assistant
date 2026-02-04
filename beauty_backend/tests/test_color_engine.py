#!/usr/bin/env python3
"""
Unit tests for color extraction and CIELAB conversion
"""

import pytest
import numpy as np
from unittest.mock import patch

from app.ml_engine.seasonal.color import (
    extract_dominant_color,
    rgb_to_lab,
    calculate_chroma,
    validate_color_extraction,
    get_skin_temperature_label
)


class TestRGBtoLAB:
    """Tests for RGB to CIELAB conversion"""
    
    def test_rgb_to_lab_single_color(self):
        """Test conversion of single RGB color"""
        # White
        white_rgb = np.array([255, 255, 255])
        white_lab = rgb_to_lab(white_rgb)
        
        # White should have L ≈ 100
        assert white_lab.shape == (3,)
        assert 98 <= white_lab[0] <= 100
        assert -2 <= white_lab[1] <= 2  # Near zero a
        assert -2 <= white_lab[2] <= 2  # Near zero b
    
    def test_rgb_to_lab_black(self):
        """Test black conversion"""
        black_rgb = np.array([0, 0, 0])
        black_lab = rgb_to_lab(black_rgb)
        
        # Black should have L ≈ 0
        assert black_lab[0] <= 2
    
    def test_rgb_to_lab_warm_color(self):
        """Test warm color (positive b*)"""
        # Peachy/warm color
        warm_rgb = np.array([255, 200, 150])
        warm_lab = rgb_to_lab(warm_rgb)
        
        # Should have positive b (yellow/warm)
        assert warm_lab[2] > 0
    
    def test_rgb_to_lab_cool_color(self):
        """Test cool color (negative b*)"""
        # Bluish color
        cool_rgb = np.array([150, 180, 255])
        cool_lab = rgb_to_lab(cool_rgb)
        
        # Should have negative b (blue/cool)
        assert cool_lab[2] < 0
    
    def test_rgb_to_lab_multiple_colors(self):
        """Test batch conversion of multiple colors"""
        colors = np.array([
            [255, 0, 0],    # Red
            [0, 255, 0],    # Green
            [0, 0, 255]     # Blue
        ])
        
        lab_colors = rgb_to_lab(colors)
        
        assert lab_colors.shape == (3, 3)
        # All should have different L, a, b values
        assert not np.allclose(lab_colors[0], lab_colors[1])
    
    def test_rgb_to_lab_image(self):
        """Test conversion of RGB image"""
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        lab_image = rgb_to_lab(image)
        
        assert lab_image.shape == (100, 100, 3)
        # L should be in [0, 100]
        assert lab_image[:, :, 0].min() >= 0
        assert lab_image[:, :, 0].max() <= 100


class TestColorExtraction:
    """Tests for K-Means color extraction"""
    
    def test_extract_dominant_color_basic(self):
        """Test basic color extraction"""
        # Create simple image with uniform color
        image = np.ones((100, 100, 3), dtype=np.uint8) * np.array([200, 150, 100])
        mask = np.ones((100, 100), dtype=np.uint8)
        
        color = extract_dominant_color(image, mask)
        
        # Should return a color close to input
        assert color.shape == (3,)
        assert color.dtype == np.uint8
        assert not np.array_equal(color, [0, 0, 0])  # Not black
    
    def test_extract_dominant_color_insufficient_pixels(self):
        """Test extraction with too few pixels"""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[0:2, 0:2] = 1  # Only 4 pixels
        
        color = extract_dominant_color(image, mask)
        
        # Should return black for insufficient pixels
        assert np.array_equal(color, [0, 0, 0])
    
    def test_extract_dominant_color_multimodal(self):
        """Test extraction with multiple color clusters"""
        # Create image with highlights, mid-tones, shadows
        image = np.zeros((300, 100, 3), dtype=np.uint8)
        image[0:100, :] = [240, 220, 200]  # Highlights
        image[100:200, :] = [180, 150, 130]  # Mid-tones
        image[200:300, :] = [100, 80, 60]   # Shadows
        
        mask = np.ones((300, 100), dtype=np.uint8)
        
        color = extract_dominant_color(image, mask, k_clusters=3)
        
        # Should select mid-tone cluster (not highlights or shadows)
        # Color should be closer to mid-tones [180, 150, 130]
        assert 100 < color[0] < 240
        assert not np.array_equal(color, [0, 0, 0])


class TestChromaCalculation:
    """Tests for chroma calculation"""
    
    def test_calculate_chroma_vivid(self):
        """Test chroma for vivid color"""
        # Bright, saturated red
        vivid_rgb = np.array([255, 0, 0])
        chroma = calculate_chroma(vivid_rgb)
        
        # Should have high chroma (>50)
        assert chroma > 50
    
    def test_calculate_chroma_gray(self):
        """Test chroma for gray (unsaturated)"""
        # Gray has no chroma
        gray_rgb = np.array([128, 128, 128])
        chroma = calculate_chroma(gray_rgb)
        
        # Should have near-zero chroma
        assert chroma < 5
    
    def test_calculate_chroma_skin_tone(self):
        """Test chroma for typical skin tone"""
        skin_rgb = np.array([210, 180, 160])
        chroma = calculate_chroma(skin_rgb)
        
        # Skin tones typically have moderate chroma (20-40)
        assert 10 < chroma < 50


class TestColorValidation:
    """Tests for color validation"""
    
    def test_validate_color_extraction_valid(self):
        """Test validation with valid color"""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        mask = np.ones((100, 100), dtype=np.uint8)
        color = np.array([200, 150, 100], dtype=np.uint8)
        
        is_valid, message = validate_color_extraction(image, mask, color)
        
        assert is_valid is True
        assert "valid" in message.lower()
    
    def test_validate_color_extraction_black(self):
        """Test validation rejects black (extraction failure)"""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        mask = np.ones((100, 100), dtype=np.uint8)
        color = np.array([0, 0, 0], dtype=np.uint8)
        
        is_valid, message = validate_color_extraction(image, mask, color)
        
        assert is_valid is False
        assert "failed" in message.lower()
    
    def test_validate_color_extraction_insufficient_pixels(self):
        """Test validation rejects small masks"""
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[0:5, 0:5] = 1  # Only 25 pixels
        color = np.array([200, 150, 100], dtype=np.uint8)
        
        is_valid, message = validate_color_extraction(image, mask, color)
        
        assert is_valid is False
        assert "insufficient" in message.lower()


class TestTemperatureLabel:
    """Tests for temperature labeling"""
    
    def test_temperature_warm(self):
        """Test warm temperature detection"""
        # High b/a ratio = yellow = warm
        # Example: a=5, b=20 -> ratio=4.0 > 1.8 = warm
        label = get_skin_temperature_label(5.0, 20.0)
        assert label == "warm"
    
    def test_temperature_cool(self):
        """Test cool temperature detection"""
        # Low b/a ratio = pink = cool
        # Example: a=15, b=10 -> ratio=0.67 < 1.2 = cool
        label = get_skin_temperature_label(15.0, 10.0)
        assert label == "cool"
    
    def test_temperature_neutral(self):
        """Test neutral temperature"""
        # Medium b/a ratio = neutral
        # Example: a=10, b=15 -> ratio=1.5, between 1.2 and 1.8 = neutral
        label = get_skin_temperature_label(10.0, 15.0)
        assert label == "neutral"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
