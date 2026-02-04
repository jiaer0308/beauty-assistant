#!/usr/bin/env python3
"""
Unit tests for validation and hybrid vision components
"""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, MagicMock

from app.ml_engine.validation import (
    validate_lighting,
    validate_image_size,
    validate_image,
    get_lighting_quality_label,
    ValidationError
)


class TestValidation:
    """Tests for image validation"""
    
    def test_validate_lighting_good(self):
        """Test lighting validation with good image"""
        # Create synthetic image with good lighting and some variance
        np.random.seed(42)
        image = np.random.randint(100, 150, (512, 512, 3), dtype=np.uint8)
        
        is_valid, message = validate_lighting(image)
        
        assert is_valid is True
        assert "acceptable" in message.lower()
    
    def test_validate_lighting_too_dark(self):
        """Test rejection of too-dark images"""
        # Create very dark image (mean < 40)
        image = np.ones((512, 512, 3), dtype=np.uint8) * 20
        
        is_valid, message = validate_lighting(image)
        
        assert is_valid is False
        assert "too dark" in message.lower()
    
    def test_validate_lighting_overexposed(self):
        """Test rejection of overexposed images"""
        # Create overexposed image (mean > 250)
        image = np.ones((512, 512, 3), dtype=np.uint8) * 254
        
        is_valid, message = validate_lighting(image)
        
        assert is_valid is False
        assert "overexposed" in message.lower()
    
    def test_validate_lighting_low_contrast(self):
        """Test rejection of low contrast/blurry images"""
        # Create uniform image (variance < 10)
        # Perfectly uniform gray will have variance = 0
        image = np.ones((512, 512, 3), dtype=np.uint8) * 128
        
        is_valid, message = validate_lighting(image)
        
        # Should be rejected due to zero variance
        assert is_valid is False
        assert "low contrast" in message.lower()
    
    def test_validate_image_size_valid(self):
        """Test image size validation with valid size"""
        image = np.zeros((512, 512, 3), dtype=np.uint8)
        
        is_valid, message = validate_image_size(image)
        
        assert is_valid is True
    
    def test_validate_image_size_too_small(self):
        """Test rejection of too-small images"""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        is_valid, message = validate_image_size(image)
        
        assert is_valid is False
        assert "too small" in message.lower()
    
    def test_validate_image_size_too_large(self):
        """Test rejection of too-large images"""
        image = np.zeros((5000, 5000, 3), dtype=np.uint8)
        
        is_valid, message = validate_image_size(image)
        
        assert is_valid is False
        assert "too large" in message.lower()
    
    def test_validate_image_invalid_shape(self):
        """Test validation with invalid image shape"""
        # Grayscale image (should be RGB)
        image = np.zeros((512, 512), dtype=np.uint8)
        
        with pytest.raises(ValueError, match="must be RGB"):
            validate_lighting(image)
    
    def test_get_lighting_quality_label(self):
        """Test lighting quality labeling"""
        # Good lighting
        good_image = np.random.randint(80, 200, (512, 512, 3), dtype=np.uint8)
        assert get_lighting_quality_label(good_image) in ["good", "acceptable"]
        
        # Poor lighting (too dark)
        dark_image = np.ones((512, 512, 3), dtype=np.uint8) * 30
        assert get_lighting_quality_label(dark_image) == "poor"


class TestBiSeNetParser:
    """Tests for BiSeNet face parser"""
    
    @pytest.fixture
    def mock_onnx_session(self):
        """Create mock ONNX session"""
        session = MagicMock()
        
        # Mock input/output
        mock_input = MagicMock()
        mock_input.name = "input"
        mock_input.shape = [1, 3, 512, 512]
        
        mock_output = MagicMock()
        mock_output.name = "output"
        mock_output.shape = [1, 19, 512, 512]
        
        session.get_inputs.return_value = [mock_input]
        session.get_outputs.return_value = [mock_output]
        
        # Mock inference output
        # Create fake segmentation with some face pixels
        segmentation = np.zeros((1, 19, 512, 512), dtype=np.float32)
        segmentation[0, 1, 200:300, 200:300] = 1.0  # Face region
        
        session.run.return_value = [segmentation]
        
        return session
    
    def test_bisenet_parser_initialization(self, mock_onnx_session):
        """Test BiSeNet parser initialization"""
        from app.ml_engine.seasonal import BiSeNetParser
        
        parser = BiSeNetParser(mock_onnx_session)
        
        assert parser.input_size == (512, 512)
        assert parser.input_name == "input"
        assert parser.output_name == "output"
    
    def test_bisenet_preprocess(self, mock_onnx_session):
        """Test image preprocessing for BiSeNet"""
        from app.ml_engine.seasonal import BiSeNetParser
        
        parser = BiSeNetParser(mock_onnx_session)
        image = np.random.randint(0, 255, (1024, 768, 3), dtype=np.uint8)
        
        preprocessed = parser._preprocess(image)
        
        # Check shape is (1, 3, 512, 512)
        assert preprocessed.shape == (1, 3, 512, 512)
        assert preprocessed.dtype == np.float32
        # Check normalization [0, 1]
        assert preprocessed.min() >= 0
        assert preprocessed.max() <= 1


class TestLandmarkRefiner:
    """Tests for MediaPipe landmark refiner"""
    
    @pytest.fixture
    def mock_face_mesh(self):
        """Create mock MediaPipe FaceMesh"""
        face_mesh = MagicMock()
        
        # Mock landmarks
        mock_landmarks = MagicMock()
        mock_landmark_list = []
        
        # Create 478 mock landmarks
        for i in range(478):
            landmark = MagicMock()
            landmark.x = 0.5
            landmark.y = 0.5
            landmark.z = 0.0
            mock_landmark_list.append(landmark)
        
        mock_landmarks.landmark = mock_landmark_list
        
        # Mock results
        mock_results = MagicMock()
        mock_results.multi_face_landmarks = [mock_landmarks]
        
        face_mesh.process.return_value = mock_results
        
        return face_mesh
    
    def test_landmark_refiner_initialization(self, mock_face_mesh):
        """Test landmark refiner initialization"""
        from app.ml_engine.seasonal import LandmarkRefiner
        
        refiner = LandmarkRefiner(mock_face_mesh)
        
        assert refiner.get_landmark_count() == 478
    
    def test_refine_masks_with_landmarks(self, mock_face_mesh):
        """Test mask refinement with detected landmarks"""
        from app.ml_engine.seasonal import LandmarkRefiner
        
        refiner = LandmarkRefiner(mock_face_mesh)
        
        image = np.ones((512, 512, 3), dtype=np.uint8) * 128
        raw_skin_mask = np.ones((512, 512), dtype=np.uint8)
        
        result = refiner.refine_masks(image, raw_skin_mask)
        
        assert "skin_mask" in result
        assert "eye_mask" in result
        assert "lip_mask" in result
        
        # Refined skin should have fewer pixels (eyes/lips removed)
        assert result["skin_mask"].sum() < raw_skin_mask.sum()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
