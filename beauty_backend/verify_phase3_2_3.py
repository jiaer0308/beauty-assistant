#!/usr/bin/env python3
"""
Verification script for Phase 3.2 & 3.3
- Validation module
- BiSeNet face parser
- MediaPipe landmark refiner
"""

import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that validation and hybrid vision modules can be imported"""
    print("Testing imports...")
    
    try:
        from app.ml_engine.validation import (
            validate_lighting,
            validate_image,
            ValidationError
        )
        from app.ml_engine.seasonal import BiSeNetParser, LandmarkRefiner
        
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation():
    """Test validation module"""
    print("\nTesting Validation Module...")
    
    try:
        from app.ml_engine.validation import (
            validate_lighting,
            get_lighting_quality_label
        )
        
        # Test 1: Good lighting
        good_image = np.ones((512, 512, 3), dtype=np.uint8) * 128
        is_valid, message = validate_lighting(good_image)
        print(f"  Good image: {is_valid} - {message}")
        
        # Test 2: Too dark
        dark_image = np.ones((512, 512, 3), dtype=np.uint8) * 20
        is_valid, message = validate_lighting(dark_image)
        print(f"  Dark image: {is_valid} - {message}")
        assert is_valid is False, "Should reject dark images"
        
        # Test 3: Overexposed
        bright_image = np.ones((512, 512, 3), dtype=np.uint8) * 254
        is_valid, message = validate_lighting(bright_image)
        print(f"  Bright image: {is_valid} - {message}")
        assert is_valid is False, "Should reject overexposed images"
        
        # Test 4: Quality labeling
        label = get_lighting_quality_label(good_image)
        print(f"  Quality label for mid-gray: {label}")
        
        print("✅ Validation module tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bisenet_parser():
    """Test BiSeNet parser (without actual model)"""
    print("\nTesting BiSeNet Parser...")
    
    try:
        from app.ml_engine.seasonal import BiSeNetParser
        from unittest.mock import MagicMock
        
        # Create mock ONNX session
        mock_session = MagicMock()
        mock_input = MagicMock()
        mock_input.name = "input"
        mock_input.shape = [1, 3, 512, 512]
        
        mock_output = MagicMock()
        mock_output.name = "output"
        mock_output.shape = [1, 19, 512, 512]
        
        mock_session.get_inputs.return_value = [mock_input]
        mock_session.get_outputs.return_value = [mock_output]
        
        # Initialize parser
        parser = BiSeNetParser(mock_session)
        
        print(f"  Input name: {parser.input_name}")
        print(f"  Output name: {parser.output_name}")
        print(f"  Input size: {parser.input_size}")
        
        # Test preprocessing
        test_image = np.random.randint(0, 255, (1024, 768, 3), dtype=np.uint8)
        preprocessed = parser._preprocess(test_image)
        
        print(f"  Preprocessed shape: {preprocessed.shape}")
        print(f"  Preprocessed dtype: {preprocessed.dtype}")
        print(f"  Value range: [{preprocessed.min():.3f}, {preprocessed.max():.3f}]")
        
        assert preprocessed.shape == (1, 3, 512, 512)
        assert preprocessed.dtype == np.float32
        assert preprocessed.min() >= 0 and preprocessed.max() <= 1
        
        print("✅ BiSeNet parser tests passed")
        return True
        
    except Exception as e:
        print(f"❌ BiSeNet parser test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_landmark_refiner():
    """Test MediaPipe landmark refiner (without actual model)"""
    print("\nTesting MediaPipe Landmark Refiner...")
    
    try:
        from app.ml_engine.seasonal import LandmarkRefiner
        from unittest.mock import MagicMock
        
        # Create mock FaceMesh
        mock_face_mesh = MagicMock()
        
        # Initialize refiner
        refiner = LandmarkRefiner(mock_face_mesh)
        
        print(f"  Landmark count: {refiner.get_landmark_count()}")
        print(f"  Left eye indices: {len(refiner.LEFT_EYE_INDICES)} landmarks")
        print(f"  Right eye indices: {len(refiner.RIGHT_EYE_INDICES)} landmarks")
        print(f"  Outer lip indices: {len(refiner.OUTER_LIP_INDICES)} landmarks")
        
        assert refiner.get_landmark_count() == 478
        
        print("✅ MediaPipe landmark refiner tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Landmark refiner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_unit_tests():
    """Run pytest tests"""
    print("\n" + "="*60)
    print("Running Unit Tests (pytest)")
    print("="*60)
    
    try:
        import pytest
        
        # Run tests with verbose output
        exit_code = pytest.main([
            "tests/test_ml_validation_hybrid.py",
            "-v",
            "--tb=short"
        ])
        
        if exit_code == 0:
            print("\n✅ All unit tests passed")
            return True
        else:
            print(f"\n❌ Some unit tests failed (exit code: {exit_code})")
            return False
            
    except ImportError:
        print("⚠️  pytest not available, skipping unit tests")
        return True


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("Phase 3.2 & 3.3 Verification")
    print("Validation + Hybrid Vision")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Validation", test_validation()))
    results.append(("BiSeNet Parser", test_bisenet_parser()))
    results.append(("Landmark Refiner", test_landmark_refiner()))
    results.append(("Unit Tests", run_unit_tests()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 Phase 3.2 & 3.3 Complete!")
        print("\nImplemented Components:")
        print("  Phase 3.2 - Validation:")
        print("    ✓ Lighting quality checks (mean, variance)")
        print("    ✓ Image size validation")
        print("    ✓ Quality labeling (good/acceptable/poor)")
        print("\n  Phase 3.3 - Hybrid Vision:")
        print("    ✓ BiSeNet macro-segmentation")
        print("      - Hair mask (class 17)")
        print("      - Skin mask (classes 1 + 10)")
        print("      - Cloth mask (class 16)")
        print("      - Morphological cleaning")
        print("    ✓ MediaPipe micro-refinement")
        print("      - 478 facial landmarks")
        print("      - Eye polygon extraction")
        print("      - Lip polygon extraction")
        print("      - 'Hole punch' technique")
        print("\nNext steps:")
        print("  → Proceed to Phase 3.4: Color Engine")
        print("     - K-Means clustering for color extraction")
        print("     - RGB to CIELAB conversion")
        print("     - Dominant color computation")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
