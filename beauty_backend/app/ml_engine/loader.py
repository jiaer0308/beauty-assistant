#!/usr/bin/env python3
"""
Singleton Model Loader for Beauty Assistant Backend

Loads heavy ML models (BiSeNet ONNX and MediaPipe FaceMesh) once at server startup.
This ensures low latency (<3s) by avoiding repeated model initialization.

Architecture Pattern: Singleton
- Models are loaded ONCE globally when first accessed
- All subsequent requests reuse the same model instances
- Thread-safe implementation
"""

import onnxruntime as ort
import mediapipe as mp
from pathlib import Path
from typing import Optional
import logging
import threading

from app.core import settings


logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Singleton Model Loader
    
    Loads BiSeNet (ONNX) and MediaPipe FaceMesh models once at startup.
    Implements thread-safe singleton pattern to ensure only one instance exists.
    
    Usage:
        models = ModelLoader()  # First call loads models
        models = ModelLoader()  # Subsequent calls return same instance
        
        # Access models
        session = models.bisenet_session
        face_mesh = models.face_mesh
    """
    
    _instance: Optional['ModelLoader'] = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        """
        Thread-safe singleton implementation
        
        Returns:
            Same ModelLoader instance across all calls
        """
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking pattern
                if cls._instance is None:
                    logger.info("Creating ModelLoader singleton instance")
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Initialize models (only once)
        
        First call: Loads BiSeNet and MediaPipe
        Subsequent calls: No-op (models already loaded)
        """
        # Skip if already initialized
        if ModelLoader._initialized:
            return
        
        with ModelLoader._lock:
            # Double-checked locking
            if ModelLoader._initialized:
                return
            
            logger.info("="*60)
            logger.info("Initializing ML Models (Singleton)")
            logger.info("="*60)
            
            try:
                self._load_bisenet()
                self._load_mediapipe()
                
                ModelLoader._initialized = True
                logger.info("="*60)
                logger.info("✅ All models loaded successfully")
                logger.info("="*60)
                
            except Exception as e:
                logger.error(f"❌ Model initialization failed: {e}")
                raise RuntimeError(f"Failed to initialize models: {e}") from e
    
    def _load_bisenet(self):
        """
        Load BiSeNet ONNX model for face parsing
        
        BiSeNet performs semantic segmentation to extract:
        - Hair mask (class 17)
        - Skin mask (classes 1 + 10)
        - Cloth mask (class 16)
        
        Input: 512x512 RGB image
        Output: 19-class segmentation mask
        """
        logger.info("Loading BiSeNet ONNX model...")
        
        model_path = settings.bisenet_model_path
        
        # Validate model file exists
        if not model_path.exists():
            raise FileNotFoundError(
                f"BiSeNet model not found at {model_path}\n"
                f"Please download bisenet_resnet34.onnx and place it in {model_path.parent}"
            )
        
        # Check file size (should be ~100MB)
        file_size_mb = model_path.stat().st_size / (1024 * 1024)
        logger.info(f"  Model file: {model_path}")
        logger.info(f"  File size: {file_size_mb:.1f} MB")
        
        # Create ONNX Runtime session
        # Use CPUExecutionProvider for compatibility
        # For GPU: Add 'CUDAExecutionProvider' before 'CPUExecutionProvider'
        providers = ['CPUExecutionProvider']
        
        try:
            self.bisenet_session = ort.InferenceSession(
                str(model_path),
                providers=providers
            )
            
            # Log model info
            input_name = self.bisenet_session.get_inputs()[0].name
            input_shape = self.bisenet_session.get_inputs()[0].shape
            output_name = self.bisenet_session.get_outputs()[0].name
            output_shape = self.bisenet_session.get_outputs()[0].shape
            
            logger.info(f"  Input: {input_name} {input_shape}")
            logger.info(f"  Output: {output_name} {output_shape}")
            logger.info(f"  Provider: {self.bisenet_session.get_providers()[0]}")
            logger.info("  ✅ BiSeNet loaded successfully")
            
        except Exception as e:
            logger.error(f"  ❌ Failed to load BiSeNet: {e}")
            raise
    
    def _load_mediapipe(self):
        """
        Load MediaPipe FaceMesh for facial landmark detection
        
        MediaPipe provides 478 facial landmarks for:
        - Eye polygon extraction (for "hole punch" technique)
        - Lip polygon extraction
        - Iris landmark detection (468-478)
        
        Used for micro-refinement of BiSeNet segmentation masks
        """
        logger.info("Loading MediaPipe FaceMesh...")
        
        try:
            # Initialize FaceMesh with production-ready settings
            self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=True,           # Process single images (not video)
                max_num_faces=1,                  # Expect only 1 face
                refine_landmarks=True,            # Enable iris landmarks (468-478)
                min_detection_confidence=0.5,     # Detection threshold
                min_tracking_confidence=0.5       # Tracking threshold (unused in static mode)
            )
            
            logger.info("  Configuration:")
            logger.info("    - static_image_mode: True")
            logger.info("    - max_num_faces: 1")
            logger.info("    - refine_landmarks: True (iris detection enabled)")
            logger.info("    - min_detection_confidence: 0.5")
            logger.info("  ✅ MediaPipe FaceMesh loaded successfully")
            
        except Exception as e:
            logger.error(f"  ❌ Failed to load MediaPipe: {e}")
            raise
    
    @property
    def is_initialized(self) -> bool:
        """Check if models are initialized"""
        return ModelLoader._initialized
    
    def get_model_info(self) -> dict:
        """
        Get information about loaded models
        
        Returns:
            Dictionary with model metadata
        """
        if not self.is_initialized:
            return {"status": "not_initialized"}
        
        return {
            "status": "initialized",
            "bisenet": {
                "input_name": self.bisenet_session.get_inputs()[0].name,
                "input_shape": self.bisenet_session.get_inputs()[0].shape,
                "output_name": self.bisenet_session.get_outputs()[0].name,
                "output_shape": self.bisenet_session.get_outputs()[0].shape,
                "provider": self.bisenet_session.get_providers()[0]
            },
            "mediapipe": {
                "max_num_faces": 1,
                "refine_landmarks": True,
                "landmark_count": 478
            }
        }
    
    def __repr__(self) -> str:
        """Developer-friendly representation"""
        status = "initialized" if self.is_initialized else "not initialized"
        return f"ModelLoader(status={status})"
    
    def __str__(self) -> str:
        """Human-readable representation"""
        if self.is_initialized:
            return "ModelLoader: ✅ BiSeNet + MediaPipe loaded"
        return "ModelLoader: ⏳ Not initialized"


# Convenience function for getting the singleton instance
def get_model_loader() -> ModelLoader:
    """
    Get the ModelLoader singleton instance
    
    Returns:
        ModelLoader instance with loaded models
    """
    return ModelLoader()
