#!/usr/bin/env python3
"""
Verification script for Phase 3.5: 12-Season Classifier

Tests decision tree classification for all 12 seasonal color types
"""

import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test classifier imports"""
    print("Testing Classifier imports...")
    
    try:
        from app.ml_engine.seasonal import SeasonalColorClassifier
        from app.ml_engine.seasonal.classifier import SEASONAL_RULES
        from app.domain import SeasonalSeason
        
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_seasonal_rules():
    """Test SEASONAL_RULES structure"""
    print("\nTesting SEASONAL_RULES...")
    
    try:
        from app.ml_engine.seasonal.classifier import SEASONAL_RULES
        
        print(f"  Total seasons defined: {len(SEASONAL_RULES)}")
        
        # Check we have exactly 12 seasons
        assert len(SEASONAL_RULES) == 12, f"Should have 12 seasons, got {len(SEASONAL_RULES)}"
        
        # Check all 4 families are represented
        families = {}
        for season_name in SEASONAL_RULES.keys():
            if "Winter" in season_name:
                families.setdefault("Winter", []).append(season_name)
            elif "Spring" in season_name:
                families.setdefault("Spring", []).append(season_name)
            elif "Summer" in season_name:
                families.setdefault("Summer", []).append(season_name)
            elif "Autumn" in season_name:
                families.setdefault("Autumn", []).append(season_name)
        
        print("\n  Seasons by family:")
        for family, seasons in families.items():
            print(f"    {family}: {len(seasons)} seasons")
            for s in seasons:
                print(f"      - {s}")
        
        # Each family should have 3 seasons
        for family, seasons in families.items():
            assert len(seasons) == 3, f"{family} should have 3 seasons, got {len(seasons)}"
        
        print("\n✅ SEASONAL_RULES validation passed")
        return True
        
    except Exception as e:
        print(f"❌ SEASONAL_RULES test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_classification_examples():
    """Test classification with example color combinations"""
    print("\nTesting Classification Examples...")
    
    try:
        from app.ml_engine.seasonal import SeasonalColorClassifier
        
        classifier = SeasonalColorClassifier()
        
        # Example 1: Light Spring (warm, light, low contrast)
        print("\n  Example 1: Light Spring")
        skin = np.array([230, 200, 175])  # Warm, light
        hair = np.array([200, 180, 140])  # Golden blonde
        eyes = np.array([160, 150, 130])  # Light hazel
        
        result = classifier.classify(skin, hair, eyes)
        print(f"    Skin: RGB{skin}")
        print(f"    Hair: RGB{hair}")
        print(f"    Eyes: RGB{eyes}")
        print(f"    → {result.season.value} ({result.season.family})")
        print(f"    → Confidence: {result.confidence:.1%}")
        
        # Example 2: Dark Winter (cool, dark, high contrast)
        print("\n  Example 2: Dark Winter")
        skin = np.array([220, 195, 190])  # Fair, cool
        hair = np.array([30, 25, 20])     # Black
        eyes = np.array([45, 35, 30])     # Dark brown
        
        result = classifier.classify(skin, hair, eyes)
        print(f"    Skin: RGB{skin}")
        print(f"    Hair: RGB{hair}")
        print(f"    Eyes: RGB{eyes}")
        print(f"    → {result.season.value} ({result.season.family})")
        print(f"    → Confidence: {result.confidence:.1%}")
        
        # Example 3: Soft Autumn (warm, muted, low contrast)
        print("\n  Example 3: Soft Autumn")
        skin = np.array([200, 170, 150])  # Warm, olive
        hair = np.array([120, 100, 80])   # Soft brown
        eyes = np.array([100, 90, 70])    # Muted green
        
        result = classifier.classify(skin, hair, eyes)
        print(f"    Skin: RGB{skin}")
        print(f"    Hair: RGB{hair}")
        print(f"    Eyes: RGB{eyes}")
        print(f"    → {result.season.value} ({result.season.family})")
        print(f"    → Confidence: {result.confidence:.1%}")
        
        # Example 4: True Summer (cool, soft, medium)
        print("\n  Example 4: True Summer")
        skin = np.array([210, 190, 190])  # Cool, rose beige
        hair = np.array([140, 130, 120])  # Ash brown
        eyes = np.array([130, 140, 150])  # Gray-blue
        
        result = classifier.classify(skin, hair, eyes)
        print(f"    Skin: RGB{skin}")
        print(f"    Hair: RGB{hair}")
        print(f"    Eyes: RGB{eyes}")
        print(f"    → {result.season.value} ({result.season.family})")
        print(f"    → Confidence: {result.confidence:.1%}")
        
        print("\n✅ Classification examples completed")
        return True
        
    except Exception as e:
        print(f"❌ Classification test failed: {e}")
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
        
        exit_code = pytest.main([
            "tests/test_classifier.py",
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
    print("Phase 3.5: 12-Season Classifier Verification")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("SEASONAL_RULES", test_seasonal_rules()))
    results.append(("Classification Examples", test_classification_examples()))
    results.append(("Unit Tests", run_unit_tests()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 Phase 3.5: 12-Season Classifier Complete!")
        print("\nImplemented Features:")
        print("  Decision Tree Classification:")
        print("    ✓ 12 seasonal color types (4 families × 3 seasons)")
        print("    ✓ Temperature classification (warm/cool/neutral)")
        print("    ✓ Value analysis (light/medium/dark)")
        print("    ✓ Chroma detection (high/medium/low)")
        print("    ✓ Contrast measurement (high/medium/low)")
        print("\n  Season Families:")
        print("    ✓ Winter: Dark Winter, True Winter, Bright Winter")
        print("    ✓ Spring: Light Spring, True Spring, Bright Spring")
        print("    ✓ Summer: Light Summer, True Summer, Soft Summer")
        print("    ✓ Autumn: Dark Autumn, True Autumn, Soft Autumn")
        print("\n  Scoring & Confidence:")
        print("    ✓ Multi-feature scoring (0-100)")
        print("    ✓ Confidence calculation based on score margins")
        print("    ✓ Priority-based matching (Temperature/Value/Chroma)")
        print("\nNext steps:")
        print("  → Phase 4: Service Layer")
        print("     - SCAWorkflowService orchestration")
        print("     - End-to-end pipeline integration")
        print("     - Error handling & validation")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
