"""
ML Engine Module

Machine learning inference adapters for the Beauty Assistant backend.
Provides model loading, face parsing, color extraction, and classification.
"""

from app.ml_engine.loader import ModelLoader, get_model_loader

__all__ = ["ModelLoader", "get_model_loader"]
