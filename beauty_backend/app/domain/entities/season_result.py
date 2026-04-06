#!/usr/bin/env python3
"""
Seasonal Color Analysis Result Entity

Represents the complete result of a seasonal color analysis,
including the classified season, confidence metrics, and color data.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any

from app.domain.value_objects import SeasonalSeason


@dataclass
class SeasonResult:
    """
    Complete seasonal color analysis result entity
    
    This is the primary business entity returned from the analysis workflow.
    It encapsulates all information about the classification result.
    """
    
    # ========== Classification Result ==========
    season: SeasonalSeason
    """Classified seasonal color type"""
    
    confidence: float
    """Classification confidence score (0.0 to 1.0)"""
    
    # ========== Color Metrics ==========
    contrast_score: float
    """Contrast between skin and hair (ΔL in CIELAB space, 0-100)"""
    
    skin_temperature: str
    """Skin undertone temperature: 'warm' or 'cool'"""
    
    # ========== Dominant Colors (RGB) ==========
    skin_color: List[int]
    """Dominant skin color as RGB [R, G, B]"""
    
    hair_color: List[int]
    """Dominant hair color as RGB [R, G, B]"""
    
    eye_color: List[int]
    """Dominant eye color as RGB [R, G, B]"""
    
    # ========== Processing Metadata ==========
    processing_time_ms: int
    """Total processing time in milliseconds"""
    
    lighting_quality: str
    """Lighting quality assessment: 'good', 'acceptable', or 'poor'"""
    
    timestamp: datetime = field(default_factory=datetime.now)
    """Timestamp when analysis was performed"""
    
    # ========== Optional Alignment Metadata ==========
    rotation_angle: float = 0.0
    """Face rotation angle detected (degrees)"""
    
    face_bbox: tuple = (0, 0, 0, 0)
    """Face bounding box in original image (x, y, w, h)"""

    # ========== Recommendations (populated after fusion) ==========
    recommendations: Dict[str, Any] = field(default_factory=dict)
    """Colour palette and cosmetic recommendations from knowledge base"""

    quiz_influence: float = 0.0
    """0–1 float indicating how much quiz data shifted the final result"""
    
    session_id: int | None = None
    """The database ID of the created recommendation session"""

    def __post_init__(self):
        """Validate entity after initialization"""
        # Validate confidence
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        
        # Validate contrast score
        if not (0.0 <= self.contrast_score <= 100.0):
            raise ValueError(f"Contrast score must be between 0 and 100, got {self.contrast_score}")
        
        # Validate skin temperature
        if self.skin_temperature not in ["warm", "cool", "neutral"]:
            raise ValueError(f"Skin temperature must be 'warm', 'cool', or 'neutral', got {self.skin_temperature}")
        
        # Validate RGB colors
        for color_name, color in [
            ("skin", self.skin_color),
            ("hair", self.hair_color),
            ("eye", self.eye_color)
        ]:
            if len(color) != 3:
                raise ValueError(f"{color_name}_color must have 3 components (RGB), got {len(color)}")
            
            if not all(0 <= c <= 255 for c in color):
                raise ValueError(f"{color_name}_color values must be 0-255, got {color}")
        
        # Validate lighting quality
        if self.lighting_quality not in ["good", "acceptable", "poor"]:
            raise ValueError(
                f"Lighting quality must be 'good', 'acceptable', or 'poor', got {self.lighting_quality}"
            )
        
        # Validate processing time
        if self.processing_time_ms < 0:
            raise ValueError(f"Processing time cannot be negative, got {self.processing_time_ms}")
    
    @property
    def display_name(self) -> str:
        """Get human-readable season name"""
        return self.season.display_name
    
    @property
    def season_family(self) -> str:
        """Get season family (Winter, Summer, Autumn, Spring)"""
        return self.season.family
    
    @property
    def confidence_percentage(self) -> float:
        """Get confidence as percentage"""
        return self.confidence * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert entity to API response format
        
        Returns:
            Dictionary matching the API schema from workflow design
        """
        return {
            "result": {
                "season": self.season.value,
                "display_name": self.display_name,
                "confidence": round(self.confidence, 2)
            },
            "metrics": {
                "contrast_score": round(self.contrast_score, 1),
                "skin_temperature": self.skin_temperature,
                "dominant_colors": {
                    "skin": self.skin_color,
                    "hair": self.hair_color,
                    "eye": self.eye_color
                }
            },
            "debug_info": {
                "lighting_quality": self.lighting_quality,
                "processing_time_ms": self.processing_time_ms
            },
            "recommendations": self.recommendations,
            "quiz_influence": round(self.quiz_influence, 4),
        }
    
    def __str__(self) -> str:
        """Human-readable string representation"""
        return (
            f"{self.display_name} "
            f"(confidence: {self.confidence_percentage:.0f}%, "
            f"contrast: {self.contrast_score:.1f}, "
            f"{self.skin_temperature} undertones)"
        )
    
    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return (
            f"SeasonResult(season={self.season.value}, "
            f"confidence={self.confidence:.2f}, "
            f"contrast={self.contrast_score:.1f})"
        )
