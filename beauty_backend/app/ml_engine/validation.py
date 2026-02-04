#!/usr/bin/env python3
"""
Image Validation Module - Phase 0 of SCA Pipeline

Validates image quality before processing using OpenCV statistics.
Ensures lighting quality is acceptable for accurate color analysis.

Rejection Criteria:
- Too dark (mean < 40)
- Overexposed (mean > 250)
- Low contrast/blurry (variance < 10)
"""

import cv2
import numpy as np
from typing import Tuple
import logging


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation failures"""
    pass


def validate_lighting(image: np.ndarray) -> Tuple[bool, str]:
    """
    Validate image lighting quality using OpenCV statistics
    
    Uses grayscale conversion and statistical analysis to detect:
    - Underexposure (too dark)
    - Overexposure (blown highlights)
    - Low contrast (blur/poor quality)
    
    Args:
        image: RGB image as numpy array (H, W, 3)
    
    Returns:
        Tuple of (is_valid, message):
        - is_valid: True if lighting is acceptable
        - message: Description of lighting quality or rejection reason
    
    Raises:
        ValueError: If image is invalid (not RGB, empty, etc.)
    
    Examples:
        >>> image = cv2.imread("photo.jpg")
        >>> image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        >>> is_valid, msg = validate_lighting(image)
        >>> if not is_valid:
        ...     print(f"Rejected: {msg}")
    """
    # Validate input
    if image is None or image.size == 0:
        raise ValueError("Image is None or empty")
    
    if len(image.shape) != 3 or image.shape[2] != 3:
        raise ValueError(
            f"Image must be RGB (H, W, 3), got shape {image.shape}"
        )
    
    # Convert to grayscale for luminance analysis
    # This gives us the perceived brightness
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Calculate statistics
    mean_brightness = gray.mean()
    variance = gray.var()
    
    # Log metrics for debugging
    logger.debug(
        f"Lighting metrics: mean={mean_brightness:.1f}, variance={variance:.1f}"
    )
    
    # Check 1: Too dark
    # Mean < 40 indicates severe underexposure
    if mean_brightness < 40:
        message = (
            f"Image too dark (mean brightness={mean_brightness:.1f}). "
            f"Please take photo in better lighting."
        )
        logger.warning(f"Validation failed: {message}")
        return False, message
    
    # Check 2: Overexposed
    # Mean > 250 indicates blown highlights
    if mean_brightness > 250:
        message = (
            f"Image overexposed (mean brightness={mean_brightness:.1f}). "
            f"Reduce lighting or move away from direct light."
        )
        logger.warning(f"Validation failed: {message}")
        return False, message
    
    # Check 3: Low contrast / Blurry
    # Variance < 10 indicates uniform image (blur, fog, or poor quality)
    if variance < 10:
        message = (
            f"Image has low contrast (variance={variance:.1f}). "
            f"Ensure camera is focused and image is clear."
        )
        logger.warning(f"Validation failed: {message}")
        return False, message
    
    # All checks passed
    message = f"Lighting quality acceptable (mean={mean_brightness:.1f}, var={variance:.1f})"
    logger.info(message)
    return True, message


def validate_image_size(image: np.ndarray, min_size: int = 256, max_size: int = 4096) -> Tuple[bool, str]:
    """
    Validate image dimensions
    
    Args:
        image: RGB image array
        min_size: Minimum width/height
        max_size: Maximum width/height
    
    Returns:
        (is_valid, message)
    """
    height, width = image.shape[:2]
    
    if width < min_size or height < min_size:
        return False, f"Image too small ({width}x{height}), minimum {min_size}x{min_size}"
    
    if width > max_size or height > max_size:
        return False, f"Image too large ({width}x{height}), maximum {max_size}x{max_size}"
    
    return True, f"Image size acceptable ({width}x{height})"


def validate_image(image: np.ndarray) -> None:
    """
    Comprehensive image validation
    
    Validates:
    1. Image size (256-4096 pixels)
    2. Lighting quality (OpenCV statistics)
    
    Args:
        image: RGB image array
    
    Raises:
        ValidationError: If validation fails with descriptive message
    
    Example:
        >>> try:
        ...     validate_image(image)
        ...     # Proceed with analysis
        ... except ValidationError as e:
        ...     return {"error": str(e)}
    """
    # Validate size
    is_valid, message = validate_image_size(image)
    if not is_valid:
        raise ValidationError(message)
    
    # Validate lighting
    is_valid, message = validate_lighting(image)
    if not is_valid:
        raise ValidationError(message)
    
    logger.info("✅ Image validation passed")


def get_lighting_quality_label(image: np.ndarray) -> str:
    """
    Get human-readable lighting quality label
    
    Returns:
        'good', 'acceptable', or 'poor'
    """
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    mean_brightness = gray.mean()
    variance = gray.var()
    
    # Good: ideal range
    if 80 <= mean_brightness <= 200 and variance >= 50:
        return "good"
    
    # Acceptable: passes validation but not ideal
    if 40 <= mean_brightness <= 250 and variance >= 10:
        return "acceptable"
    
    # Poor: fails validation
    return "poor"
