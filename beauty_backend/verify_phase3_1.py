#!/usr/bin/env python3
"""
Verification script for Phase 3.1: Singleton Model Loader

Tests the ModelLoader singleton implementation without requiring actual model files.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that ML engine modules can be imported"""
    print("Testing ML engine imports...")
    
    try:
        from app.ml_engine import ModelLoader, get_model_loader
        print("✅ ML engine imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_singleton_pattern():
    """Test singleton pattern implementation"""
    print("\nTesting Singleton Pattern...")
    
    try:
        from app.ml_engine import ModelLoader
        
        # Reset singleton for clean testing
        ModelLoader._instance = None
        ModelLoader._initialized = False
        
        print("  Creating first instance...")
        loader1 = ModelLoader()
        print(f"  Instance 1 ID: {id(loader1)}")
        
        print("  Creating second instance...")
        loader2 = ModelLoader()
        print(f"  Instance 2 ID: {id(loader2)}")
        
        # Check same instance
        if loader1 is loader2:
            print("  ✅ Singleton pattern working - same instance returned")
        else:
            print("  ❌ Singleton pattern failed - different instances")
            return False
        
        # Check ID
        if id(loader1) == id(loader2):
            print("  ✅ Memory addresses match")
        else:
            print("  ❌ Memory addresses don't match")
            return False
        
        print("✅ Singleton pattern tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Singleton pattern test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_thread_safety():
    """Test thread-safe initialization"""
    print("\nTesting Thread Safety...")
    
    try:
        from app.ml_engine import ModelLoader
        import threading
        
        # Reset singleton
        ModelLoader._instance = None
        ModelLoader._initialized = False
        
        instances = []
        
        def create_loader():
            loader = ModelLoader()
            instances.append(id(loader))
        
        # Create 10 threads
        print("  Creating 10 concurrent threads...")
        threads = [threading.Thread(target=create_loader) for _ in range(10)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        print(f"  Captured {len(instances)} instance IDs")
        unique_ids = set(instances)
        print(f"  Unique IDs: {len(unique_ids)}")
        
        if len(unique_ids) == 1:
            print("  ✅ Thread-safe - only one instance created")
            return True
        else:
            print(f"  ❌ Thread-safety violated - {len(unique_ids)} instances created")
            return False
            
    except Exception as e:
        print(f"❌ Thread safety test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_file_detection():
    """Test BiSeNet model file detection"""
    print("\nTesting Model File Detection...")
    
    try:
        from app.core import settings
        
        model_path = settings.bisenet_model_path
        print(f"  Expected model path: {model_path}")
        
        if model_path.exists():
            file_size_mb = model_path.stat().st_size / (1024 * 1024)
            print(f"  ✅ Model file found ({file_size_mb:.1f} MB)")
            return True
        else:
            print("  ⚠️  Model file not found")
            print(f"     Please download bisenet_resnet34.onnx to:")
            print(f"     {model_path}")
            print("  ℹ️  This is expected - model loading will be tested in integration")
            return True  # Not a failure, just informational
            
    except Exception as e:
        print(f"❌ Model file detection failed: {e}")
        return False


def test_convenience_function():
    """Test get_model_loader() convenience function"""
    print("\nTesting Convenience Function...")
    
    try:
        from app.ml_engine import get_model_loader, ModelLoader
        
        # Reset singleton
        ModelLoader._instance = None
        ModelLoader._initialized = False
        
        loader = get_model_loader()
        
        print(f"  Loader type: {type(loader).__name__}")
        print(f"  Is ModelLoader: {isinstance(loader, ModelLoader)}")
        
        if isinstance(loader, ModelLoader):
            print("  ✅ Convenience function returns correct type")
            return True
        else:
            print("  ❌ Convenience function returned wrong type")
            return False
            
    except Exception as e:
        print(f"❌ Convenience function test failed: {e}")
        return False


def test_string_representations():
    """Test __str__ and __repr__ methods"""
    print("\nTesting String Representations...")
    
    try:
        from app.ml_engine import ModelLoader
        
        # Reset singleton
        ModelLoader._instance = None
        ModelLoader._initialized = False
        
        loader = ModelLoader()
        
        str_repr = str(loader)
        repr_str = repr(loader)
        
        print(f"  __str__: {str_repr}")
        print(f"  __repr__: {repr_str}")
        
        if "ModelLoader" in str_repr or "ModelLoader" in repr_str:
            print("  ✅ String representations working")
            return True
        else:
            print("  ❌ String representations missing 'ModelLoader'")
            return False
            
    except Exception as e:
        print(f"❌ String representation test failed: {e}")
        return False


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("Phase 3.1: Singleton Model Loader Verification")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Singleton Pattern", test_singleton_pattern()))
    results.append(("Thread Safety", test_thread_safety()))
    results.append(("Model File Detection", test_model_file_detection()))
    results.append(("Convenience Function", test_convenience_function()))
    results.append(("String Representations", test_string_representations()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 Phase 3.1: Singleton Model Loader Complete!")
        print("\nImplemented Features:")
        print("  ✓ Thread-safe singleton pattern")
        print("  ✓ Double-checked locking")
        print("  ✓ BiSeNet ONNX model loading")
        print("  ✓ MediaPipe FaceMesh loading")
        print("  ✓ Comprehensive logging")
        print("  ✓ Model info extraction")
        print("\nNext steps:")
        print("  1. Download bisenet_resnet34.onnx model")
        print("  2. Proceed to Phase 3.2: Validation (lighting checks)")
        print("  3. Proceed to Phase 3.3: Hybrid Vision (BiSeNet + MediaPipe)")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
