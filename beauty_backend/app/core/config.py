#!/usr/bin/env python3
"""
Application configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from pathlib import Path
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file
    """
    # Application metadata
    app_name: str = "Beauty Assistant API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security configuration
    # Use a secure default for development, but it should be overridden via environment variables in production
    secret_key: str = "your-super-secret-key-for-development-only"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # Default to 7 days for now (flexible for prototypes)
    
    # Database configuration
    database_url: str = "mysql+mysqlconnector://baDB:Panda24685l%24@www.dcs5604.com:3306/beauty_assisant"
    
    # Model configuration
    model_dir: Path = Path(__file__).parent.parent / "ml_engine" / "data"
    bisenet_model_name: str = "bisenet_resnet34.onnx"
    
    # File upload configuration
    max_file_size_mb: int = 10
    allowed_image_types: str = "image/jpeg,image/png,image/jpg"
    
    # Performance tuning
    enable_model_cache: bool = True
    workers: int = 1
    
    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    upload_dir: Path = base_dir / "uploads"
    output_dir: Path = base_dir / "output"
    temp_dir: Path = base_dir / "temp"
    
    @property
    def bisenet_model_path(self) -> Path:
        """Get full path to BiSeNet ONNX model"""
        return self.model_dir / self.bisenet_model_name
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size from MB to bytes"""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def get_allowed_image_types(self) -> List[str]:
        """Get allowed image types as list"""
        return [t.strip() for t in self.allowed_image_types.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create global settings instance
settings = Settings()

# Ensure required directories exist
for directory in [settings.upload_dir, settings.output_dir, settings.temp_dir, settings.model_dir]:
    os.makedirs(directory, exist_ok=True)
