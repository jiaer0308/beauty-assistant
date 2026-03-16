#!/usr/bin/env python3
"""
Phase 4 Verification Script

Tests the complete alignment-first pipeline:
1. Face Alignment (MediaPipe → Affine Transform)
2. BiSeNet Segmentation (on aligned face)
3. Color Extraction (on aligned image)
4. Classification (12-season decision tree)

Usage:
    python verify_phase4.py
"""

import asyncio
import sys
import cv2
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.sca_workflow_service import SCAWorkflowService, ValidationError


def create_test_image() -> bytes:
    """
    Create a synthetic test image with a simulated face
    
    Returns:
        JPEG image bytes
    """
    # Create a 512x512 synthetic image with a face-like pattern
    image = np.zeros((512, 512, 3), dtype=np.uint8)
    
    # Add warm background (simulating skin tone)
    image[:, :] = [210, 180, 160]  # Warm beige
    
    # Add darker region for hair (top portion)
    image[0:150, :] = [60, 40, 30]  # Dark brown
    
    # Add some variance to simulate realistic image
    noise = np.random.randint(-10, 10, (512, 512, 3), dtype=np.int16)
    image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # Encode as JPEG
    success, encoded = cv2.imencode('.jpg', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    
    if not success:
        raise RuntimeError("Failed to encode test image")
    
    return encoded.tobytes()


async def test_workflow():
    """
    Test the complete SCA workflow
    """
    print("=" * 60)
    print("Phase 4: SCA Workflow Verification")
    print("=" * 60)
    print()
    
    # Initialize service
    print("[1/4] Initializing SCAWorkflowService...")
    try:
        service = SCAWorkflowService()
        print("✓ Service initialized successfully")
    except Exception as e:
        print(f"✗ Service initialization failed: {e}")
        return False
    
    print()
    
    # Create test image
    print("[2/4] Loading test image...")
    try:
        test_image_path = './tests/DeepAutumn.png'
        # Read the actual image bytes from file
        with open(test_image_path, 'rb') as f:
            test_image_bytes = f.read()
        print(f"✓ Test image loaded: {len(test_image_bytes)} bytes from {test_image_path}")
    except FileNotFoundError:
        print(f"✗ Test image not found at '{test_image_path}'")
        print("  Creating synthetic test image instead...")
        test_image_bytes = create_test_image()
        print(f"✓ Synthetic image created: {len(test_image_bytes)} bytes")
    except Exception as e:
        print(f"✗ Image loading failed: {e}")
        return False
    
    print()
    
    # Run analysis
    print("[3/4] Running complete SCA pipeline...")
    print("-" * 60)
    try:
        result = await service.analyze(test_image_bytes)
        print("-" * 60)
        print("✓ Analysis completed successfully")
    except ValidationError as e:
        print(f"✗ Validation error: {e}")
        return False
    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Display results
    print("[4/4] Analysis Results:")
    print("-" * 60)
    print(f"Season:           {result.display_name}")
    print(f"Confidence:       {result.confidence:.1%}")
    print(f"Skin Temperature: {result.skin_temperature}")
    print(f"Contrast Score:   {result.contrast_score:.1f}")
    print()
    print(f"Dominant Colors (RGB):")
    print(f"  Skin:  {result.skin_color}")
    print(f"  Hair:  {result.hair_color}")
    print(f"  Eye:   {result.eye_color}")
    print()
    print(f"Alignment Metadata:")
    print(f"  Rotation Angle: {result.rotation_angle:.1f}°")
    print(f"  Face BBox:      {result.face_bbox}")
    print()
    print(f"Processing Time:  {result.processing_time_ms}ms")
    print(f"Lighting Quality: {result.lighting_quality}")
    print("-" * 60)
    print()
    
    # Validate results
    print("Validation Checks:")
    checks = [
        (result.season is not None, "Season classified"),
        (0.0 <= result.confidence <= 1.0, "Confidence in valid range"),
        (0.0 <= result.contrast_score <= 100.0, "Contrast in valid range"),
        (len(result.skin_color) == 3, "Skin color is RGB"),
        (len(result.hair_color) == 3, "Hair color is RGB"),
        (result.processing_time_ms > 0, "Processing time recorded"),
    ]
    
    all_passed = True
    for check, description in checks:
        status = "✓" if check else "✗"
        print(f"  {status} {description}")
        if not check:
            all_passed = False
    
    print()
    print("=" * 60)
    if all_passed:
        print("✓ ALL CHECKS PASSED - Phase 4 Implementation Complete!")
    else:
        print("✗ Some checks failed - Please review implementation")
    print("=" * 60)
    
    return all_passed


def main():
    """Main entry point"""
    print()
    print("Starting Phase 4 verification...")
    print()
    
    try:
        success = asyncio.run(test_workflow())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nVerification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
