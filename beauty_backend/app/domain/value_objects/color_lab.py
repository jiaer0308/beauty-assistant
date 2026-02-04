#!/usr/bin/env python3
"""
CIELAB Color Space Value Object

Represents a color in the CIELAB color space (L*a*b*).
This is an immutable value object used for color analysis.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ColorLAB:
    """
    CIELAB color space value object
    
    Attributes:
        L: Lightness component (0-100)
           0 = black, 100 = white
        a: Green-Red axis component (-128 to 127)
           Negative = green, Positive = red
        b: Blue-Yellow axis component (-128 to 127)
           Negative = blue, Positive = yellow
    """
    L: float
    a: float
    b: float
    
    def __post_init__(self):
        """Validate color values after initialization"""
        if not (0 <= self.L <= 100):
            raise ValueError(f"L must be between 0 and 100, got {self.L}")
        
        if not (-128 <= self.a <= 127):
            raise ValueError(f"a must be between -128 and 127, got {self.a}")
        
        if not (-128 <= self.b <= 127):
            raise ValueError(f"b must be between -128 and 127, got {self.b}")
    
    @property
    def is_warm(self) -> bool:
        """
        Determine if color has warm temperature
        Based on b* value (positive = yellow = warm)
        """
        return self.b > 0
    
    @property
    def is_cool(self) -> bool:
        """
        Determine if color has cool temperature
        Based on b* value (negative = blue = cool)
        """
        return self.b < 0
    
    def contrast_with(self, other: 'ColorLAB') -> float:
        """
        Calculate contrast (ΔL) with another color
        
        Args:
            other: Another ColorLAB instance
        
        Returns:
            Absolute difference in lightness (0-100)
        """
        return abs(self.L - other.L)
    
    def to_tuple(self) -> Tuple[float, float, float]:
        """Convert to tuple representation"""
        return (self.L, self.a, self.b)
    
    def __str__(self) -> str:
        """Human-readable string representation"""
        temp = "warm" if self.is_warm else "cool" if self.is_cool else "neutral"
        return f"LAB(L={self.L:.1f}, a={self.a:.1f}, b={self.b:.1f}, {temp})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return f"ColorLAB(L={self.L}, a={self.a}, b={self.b})"
