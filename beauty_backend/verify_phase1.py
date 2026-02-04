#!/usr/bin/env python3
"""
Quick test script to verify Phase 1 infrastructure setup
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that core modules can be imported"""
    print("Testing imports...")
    
    try:
        from app.core import settings, logger
        print("✅ Core imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_settings():
    """Test settings configuration"""
    print("\nTesting settings...")
    
    try:
        from app.core import settings
        
        print(f"  App Name: {settings.app_name}")
        print(f"  Version: {settings.app_version}")
        print(f"  Debug: {settings.debug}")
        print(f"  Model Path: {settings.bisenet_model_path}")
        print(f"  Max File Size: {settings.max_file_size_bytes} bytes")
        
        # Check directories were created
        for name, path in [
            ("Upload", settings.upload_dir),
            ("Output", settings.output_dir),
            ("Temp", settings.temp_dir),
            ("Model", settings.model_dir)
        ]:
            if path.exists():
                print(f"  ✅ {name} directory created: {path}")
            else:
                print(f"  ⚠️  {name} directory missing: {path}")
        
        print("✅ Settings configuration working")
        return True
        
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        return False

def test_logger():
    """Test logging system"""
    print("\nTesting logger...")
    
    try:
        from app.core import logger, log_with_context
        
        # Test basic logging
        logger.info("Test INFO message")
        logger.warning("Test WARNING message")
        
        # Test contextual logging
        log_with_context(
            "info",
            "Test contextual logging",
            user_id=123,
            action="test"
        )
        
        print("✅ Logger working (check console output above)")
        return True
        
    except Exception as e:
        print(f"❌ Logger test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Phase 1 Infrastructure Verification")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Settings", test_settings()))
    results.append(("Logger", test_logger()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 Phase 1 Infrastructure Setup Complete!")
        print("\nNext steps:")
        print("1. Create .env file from .env.example")
        print("2. Download BiSeNet ONNX model to app/ml_engine/data/")
        print("3. Proceed to Phase 2: Domain Layer implementation")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
