#!/usr/bin/env python3
"""
Unit tests for ModelLoader singleton
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from app.ml_engine import ModelLoader, get_model_loader


class TestModelLoader:
    """Tests for ModelLoader singleton pattern"""
    
    def test_singleton_pattern(self):
        """Test that ModelLoader returns same instance"""
        # Note: This test may fail if models are actually loaded
        # In real environment, we'd mock the model loading
        
        loader1 = get_model_loader()
        loader2 = get_model_loader()
        
        # Same instance
        assert loader1 is loader2
        assert id(loader1) == id(loader2)
    
    def test_singleton_thread_safety(self):
        """Test thread-safe initialization"""
        import threading
        
        instances = []
        
        def create_loader():
            loader = ModelLoader()
            instances.append(id(loader))
        
        # Create 10 threads trying to get instance simultaneously
        threads = [threading.Thread(target=create_loader) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All should have same ID
        assert len(set(instances)) == 1, "Multiple instances created!"
    
    @patch('app.ml_engine.loader.ort.InferenceSession')
    @patch('app.ml_engine.loader.mp.solutions.face_mesh.FaceMesh')
    def test_model_initialization(self, mock_face_mesh, mock_onnx_session):
        """Test model initialization with mocks"""
        # Setup mocks
        mock_onnx_session.return_value = MagicMock()
        mock_face_mesh.return_value = MagicMock()
        
        # Reset singleton for testing
        ModelLoader._instance = None
        ModelLoader._initialized = False
        
        # Create loader
        loader = ModelLoader()
        
        # Should be initialized
        assert loader.is_initialized is True
        assert hasattr(loader, 'bisenet_session')
        assert hasattr(loader, 'face_mesh')
    
    @patch('app.ml_engine.loader.ort.InferenceSession')
    @patch('app.ml_engine.loader.mp.solutions.face_mesh.FaceMesh')
    def test_get_model_info(self, mock_face_mesh, mock_onnx_session):
        """Test get_model_info method"""
        # Setup mocks
        mock_session = MagicMock()
        mock_session.get_inputs.return_value = [
            MagicMock(name="input", shape=[1, 3, 512, 512])
        ]
        mock_session.get_outputs.return_value = [
            MagicMock(name="output", shape=[1, 19, 512, 512])
        ]
        mock_session.get_providers.return_value = ['CPUExecutionProvider']
        
        mock_onnx_session.return_value = mock_session
        mock_face_mesh.return_value = MagicMock()
        
        # Reset singleton
        ModelLoader._instance = None
        ModelLoader._initialized = False
        
        loader = ModelLoader()
        info = loader.get_model_info()
        
        assert info["status"] == "initialized"
        assert "bisenet" in info
        assert "mediapipe" in info
        assert info["bisenet"]["provider"] == "CPUExecutionProvider"
        assert info["mediapipe"]["landmark_count"] == 478
    
    def test_string_representations(self):
        """Test __str__ and __repr__"""
        loader = ModelLoader()
        
        str_repr = str(loader)
        repr_str = repr(loader)
        
        assert "ModelLoader" in str_repr or "ModelLoader" in repr_str


class TestModelLoaderIntegration:
    """Integration tests (require actual model files)"""
    
    @pytest.mark.skipif(
        not Path("app/ml_engine/data/bisenet_resnet34.onnx").exists(),
        reason="BiSeNet model file not found"
    )
    def test_load_real_bisenet(self):
        """Test loading real BiSeNet model"""
        loader = ModelLoader()
        
        assert loader.is_initialized
        assert hasattr(loader, 'bisenet_session')
        
        # Check model info
        info = loader.get_model_info()
        assert info["status"] == "initialized"
        assert "bisenet" in info
    
    def test_load_real_mediapipe(self):
        """Test loading real MediaPipe FaceMesh"""
        loader = ModelLoader()
        
        assert loader.is_initialized
        assert hasattr(loader, 'face_mesh')
        
        # Check model info
        info = loader.get_model_info()
        assert info["status"] == "initialized"
        assert info["mediapipe"]["landmark_count"] == 478


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
