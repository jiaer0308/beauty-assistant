#!/usr/bin/env python3
"""Quick test to check if errors are fixed"""
import sys
sys.path.insert(0, '.')

from app.domain.entities.season_result import SeasonResult
from app.domain.value_objects import SeasonalSeason
from datetime import datetime

# Test 1: Can we create SeasonResult with neutral skin temperature?
try:
    result = SeasonResult(
        season=SeasonalSeason.COOL_WINTER,
        confidence=0.85,
        contrast_score=50.0,
        skin_temperature="neutral",  # This should now work
        skin_color=[210, 180, 160],
        hair_color=[60, 40, 30],
        eye_color=[100, 80, 60],
        processing_time_ms=1000,
        lighting_quality="good",
        timestamp=datetime.now(),
        rotation_angle=5.2,
        face_bbox=(100, 100, 300, 400)
    )
    print("✓ Test 1 PASSED: SeasonResult accepts 'neutral' skin temperature")
    print(f"  Result: {result}")
except Exception as e:
    print(f"✗ Test 1 FAILED: {e}")
    sys.exit(1)

# Test 2: Check display_name property works
try:
    display_name = result.display_name
    print(f"✓ Test 2 PASSED: display_name property works: '{display_name}'")
except Exception as e:
    print(f"✗ Test 2 FAILED: {e}")
    sys.exit(1)

print("\n✅ All basic tests passed!")
