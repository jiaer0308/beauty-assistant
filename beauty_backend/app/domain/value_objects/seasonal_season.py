#!/usr/bin/env python3
"""
Seasonal Color Analysis - 12 Seasons Classification

Defines the 12 seasonal color types used in seasonal color analysis.
Each season represents a combination of hue (warm/cool), value (contrast),
and chroma (intensity) characteristics.
"""

from enum import Enum


class SeasonalSeason(str, Enum):
    """
    12 Seasonal Color Types
    
    Organized by four main families:
    - Winter: Cool + High Contrast
    - Summer: Cool + Low Contrast
    - Autumn: Warm + High Contrast
    - Spring: Warm + Low Contrast
    
    Each family has 3 subtypes based on chroma and value.
    """
    
    # ========== WINTER FAMILY (Cool + High Contrast) ==========
    DARK_WINTER = "dark_winter"
    """
    Deep Winter: Cool + Very High Contrast + Medium Chroma
    - Dark hair, light cool skin, medium eye color
    - High contrast between features
    - Best colors: Pure, saturated jewel tones
    """
    
    TRUE_WINTER = "true_winter"
    """
    Cool Winter: Very Cool + High Contrast + Low Chroma
    - Ashy dark hair, cool medium skin, soft eyes
    - Cool undertones dominate
    - Best colors: Icy, cool tones with blue undertones
    """
    
    BRIGHT_WINTER = "bright_winter"
    """
    Clear Winter: Cool + High Contrast + High Chroma
    - Dark hair, fair skin, bright clear eyes
    - Strong color contrast and clarity
    - Best colors: Clear, bright, saturated colors
    """
    
    # ========== SUMMER FAMILY (Cool + Low Contrast) ==========
    LIGHT_SUMMER = "light_summer"
    """
    Light Summer: Cool + Low Contrast + Medium Chroma
    - Light ashy hair, fair cool skin, light eyes
    - Soft, delicate coloring
    - Best colors: Soft, muted pastels with cool undertones
    """
    
    TRUE_SUMMER = "true_summer"
    """
    Cool Summer: Very Cool + Medium Contrast + Low Chroma
    - Medium ashy hair, cool medium skin, soft eyes
    - Very cool undertones
    - Best colors: Cool, soft, muted tones
    """
    
    SOFT_SUMMER = "soft_summer"
    """
    Soft Summer: Cool + Low Contrast + Low Chroma
    - Soft medium hair, muted skin, gentle eyes
    - Low color intensity
    - Best colors: Soft, dusty, muted colors
    """
    
    # ========== AUTUMN FAMILY (Warm + High Contrast) ==========
    DARK_AUTUMN = "dark_autumn"
    """
    Deep Autumn: Warm + High Contrast + Medium Chroma
    - Dark rich hair, warm deep skin, dark eyes
    - Rich, deep coloring
    - Best colors: Deep, warm, earthy tones
    """
    
    TRUE_AUTUMN = "true_autumn"
    """
    Warm Autumn: Very Warm + Medium Contrast + Medium Chroma
    - Golden/auburn hair, warm skin, warm eyes
    - Strong warm undertones
    - Best colors: Warm, spicy, golden tones
    """
    
    SOFT_AUTUMN = "soft_autumn"
    """
    Soft Autumn: Warm + Low Contrast + Low Chroma
    - Soft golden hair, muted warm skin, soft eyes
    - Muted warm coloring
    - Best colors: Soft, muted, warm earth tones
    """
    
    # ========== SPRING FAMILY (Warm + Low Contrast) ==========
    LIGHT_SPRING = "light_spring"
    """
    Light Spring: Warm + Low Contrast + Medium Chroma
    - Light golden hair, fair warm skin, bright eyes
    - Fresh, light coloring
    - Best colors: Light, fresh, warm pastels
    """
    
    TRUE_SPRING = "true_spring"
    """
    Warm Spring: Very Warm + Low Contrast + High Chroma
    - Golden/red hair, peachy warm skin, warm eyes
    - Very warm and bright
    - Best colors: Warm, clear, golden tones
    """
    
    BRIGHT_SPRING = "bright_spring"
    """
    Clear Spring: Warm + Medium Contrast + High Chroma
    - Bright hair, clear skin, bright clear eyes
    - Clear, bright coloring
    - Best colors: Clear, bright warm colors
    """
    
    @property
    def display_name(self) -> str:
        """Get human-readable display name"""
        return self.value.replace("_", " ").title()
    
    @property
    def family(self) -> str:
        """Get season family (Winter, Summer, Autumn, Spring)"""
        if "winter" in self.value:
            return "Winter"
        elif "summer" in self.value:
            return "Summer"
        elif "autumn" in self.value:
            return "Autumn"
        else:
            return "Spring"
    
    @property
    def is_warm(self) -> bool:
        """Check if season has warm undertones"""
        return self.family in ["Autumn", "Spring"]
    
    @property
    def is_cool(self) -> bool:
        """Check if season has cool undertones"""
        return self.family in ["Winter", "Summer"]
    
    @property
    def has_high_contrast(self) -> bool:
        """Check if season has high contrast"""
        return self.family in ["Winter", "Autumn"]
    
    def __str__(self) -> str:
        """String representation"""
        return self.display_name
