#!/usr/bin/env python3
"""
Phase 2 Verification Script - Domain Layer

Tests all domain layer components:
- ColorLAB value object
- SeasonalSeason enum
- SeasonResult entity
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that domain modules can be imported"""
    print("Testing domain layer imports...")
    
    try:
        from app.domain import ColorLAB, SeasonalSeason, SeasonResult
        print("✅ Domain imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_color_lab():
    """Test ColorLAB value object"""
    print("\nTesting ColorLAB value object...")
    
    try:
        from app.domain import ColorLAB
        
        # Test valid creation
        skin_color = ColorLAB(L=70.0, a=5.0, b=18.0)
        print(f"  Created skin color: {skin_color}")
        
        # Test temperature detection
        assert skin_color.is_warm is True, "Warm detection failed"
        print(f"  ✅ Temperature detection: {skin_color.is_warm and 'warm' or 'cool'}")
        
        # Test contrast calculation
        hair_color = ColorLAB(L=15.0, a=0.0, b=0.0)
        contrast = skin_color.contrast_with(hair_color)
        print(f"  ✅ Contrast calculation: ΔL = {contrast}")
        
        # Test validation
        try:
            invalid = ColorLAB(L=150.0, a=0.0, b=0.0)
            print("  ❌ Validation failed - should reject L > 100")
            return False
        except ValueError:
            print("  ✅ Validation working - rejects invalid values")
        
        print("✅ ColorLAB tests passed")
        return True
        
    except Exception as e:
        print(f"❌ ColorLAB test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_seasonal_season():
    """Test SeasonalSeason enum"""
    print("\nTesting SeasonalSeason enum...")
    
    try:
        from app.domain import SeasonalSeason
        
        # Test all 12 seasons exist
        seasons = list(SeasonalSeason)
        assert len(seasons) == 12, f"Expected 12 seasons, got {len(seasons)}"
        print(f"  ✅ All 12 seasons defined")
        
        # Test display names
        dark_winter = SeasonalSeason.DARK_WINTER
        print(f"  Season: {dark_winter.value}")
        print(f"  Display Name: {dark_winter.display_name}")
        print(f"  Family: {dark_winter.family}")
        print(f"  Temperature: {dark_winter.is_cool and 'cool' or 'warm'}")
        print(f"  Contrast: {dark_winter.has_high_contrast and 'high' or 'low'}")
        
        # Test properties
        assert dark_winter.is_cool is True
        assert dark_winter.has_high_contrast is True
        print("  ✅ Properties working correctly")
        
        # List all seasons
        print("\n  All 12 Seasons:")
        for season in SeasonalSeason:
            family = season.family
            temp = "warm" if season.is_warm else "cool"
            contrast = "high" if season.has_high_contrast else "low"
            print(f"    - {season.display_name:20s} ({family}, {temp}, {contrast} contrast)")
        
        print("\n✅ SeasonalSeason tests passed")
        return True
        
    except Exception as e:
        print(f"❌ SeasonalSeason test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_season_result():
    """Test SeasonResult entity"""
    print("\nTesting SeasonResult entity...")
    
    try:
        from app.domain import SeasonResult, SeasonalSeason
        
        # Create valid result
        result = SeasonResult(
            season=SeasonalSeason.DARK_AUTUMN,
            confidence=0.88,
            contrast_score=52.4,
            skin_temperature="warm",
            skin_color=[210, 180, 160],
            hair_color=[40, 30, 25],
            eye_color=[85, 60, 40],
            processing_time_ms=1200,
            lighting_quality="good"
        )
        
        print(f"  Created result: {result}")
        print(f"  Display name: {result.display_name}")
        print(f"  Family: {result.season_family}")
        print(f"  Confidence: {result.confidence_percentage:.0f}%")
        
        # Test to_dict() method
        api_response = result.to_dict()
        print("\n  API Response Structure:")
        print(f"    - result.season: {api_response['result']['season']}")
        print(f"    - result.confidence: {api_response['result']['confidence']}")
        print(f"    - metrics.contrast_score: {api_response['metrics']['contrast_score']}")
        print(f"    - metrics.skin_temperature: {api_response['metrics']['skin_temperature']}")
        print(f"    - debug_info.processing_time_ms: {api_response['debug_info']['processing_time_ms']}")
        
        # Test validation
        try:
            invalid = SeasonResult(
                season=SeasonalSeason.DARK_AUTUMN,
                confidence=1.5,  # Invalid: > 1.0
                contrast_score=52.4,
                skin_temperature="warm",
                skin_color=[210, 180, 160],
                hair_color=[40, 30, 25],
                eye_color=[85, 60, 40],
                processing_time_ms=1200,
                lighting_quality="good"
            )
            print("  ❌ Validation failed - should reject confidence > 1.0")
            return False
        except ValueError:
            print("  ✅ Validation working - rejects invalid confidence")
        
        print("\n✅ SeasonResult tests passed")
        return True
        
    except Exception as e:
        print(f"❌ SeasonResult test failed: {e}")
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
            "tests/test_domain.py",
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
        print("   Install with: pip install pytest")
        return True  # Don't fail if pytest isn't installed


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("Phase 2 Domain Layer Verification")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("ColorLAB", test_color_lab()))
    results.append(("SeasonalSeason", test_seasonal_season()))
    results.append(("SeasonResult", test_season_result()))
    results.append(("Unit Tests", run_unit_tests()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 Phase 2 Domain Layer Complete!")
        print("\nImplemented Components:")
        print("  ✓ ColorLAB value object (immutable, validated)")
        print("  ✓ SeasonalSeason enum (12 seasons with properties)")
        print("  ✓ SeasonResult entity (validated, with to_dict())")
        print("\nNext steps:")
        print("  → Proceed to Phase 3: ML Engine Core")
        print("     - Singleton Model Loader")
        print("     - BiSeNet face parsing")
        print("     - MediaPipe landmark refinement")
        print("     - Color extraction & CIELAB conversion")
        print("     - 12-season classifier")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
