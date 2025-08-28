#!/usr/bin/env python3
"""
Simple test script to verify the UVI package structure and imports work correctly.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_basic_imports():
    """Test that basic imports work."""
    print("Testing basic UVI imports...")
    
    try:
        from uvi import UVI
        print("[PASS] Successfully imported UVI class")
    except ImportError as e:
        print(f"[FAIL] Failed to import UVI class: {e}")
        return False
    
    try:
        from uvi import parsers
        print("[PASS] Successfully imported parsers package")
    except ImportError as e:
        print(f"[FAIL] Failed to import parsers package: {e}")
        return False
    
    try:
        from uvi import utils
        print("[PASS] Successfully imported utils package")
    except ImportError as e:
        print(f"[FAIL] Failed to import utils package: {e}")
        return False
    
    return True

def test_parser_imports():
    """Test that individual parser imports work."""
    print("\nTesting parser imports...")
    
    parsers_to_test = [
        'VerbNetParser',
        'FrameNetParser', 
        'PropBankParser',
        'OntoNotesParser',
        'WordNetParser',
        'BSOParser',
        'SemNetParser',
        'ReferenceParser',
        'VNAPIParser'
    ]
    
    success_count = 0
    for parser_name in parsers_to_test:
        try:
            exec(f"from uvi.parsers import {parser_name}")
            print(f"[PASS] Successfully imported {parser_name}")
            success_count += 1
        except ImportError as e:
            print(f"[FAIL] Failed to import {parser_name}: {e}")
    
    print(f"Parser imports: {success_count}/{len(parsers_to_test)} successful")
    return success_count == len(parsers_to_test)

def test_utils_imports():
    """Test that utility imports work."""
    print("\nTesting utils imports...")
    
    utils_to_test = [
        'SchemaValidator',
        'CrossReferenceManager',
        'CorpusFileManager'
    ]
    
    success_count = 0
    for util_name in utils_to_test:
        try:
            exec(f"from uvi.utils import {util_name}")
            print(f"[PASS] Successfully imported {util_name}")
            success_count += 1
        except ImportError as e:
            print(f"[FAIL] Failed to import {util_name}: {e}")
    
    print(f"Utils imports: {success_count}/{len(utils_to_test)} successful")
    return success_count == len(utils_to_test)

def test_uvi_initialization():
    """Test that UVI class can be initialized."""
    print("\nTesting UVI initialization...")
    
    try:
        from uvi import UVI
        
        # Test basic initialization (without loading)
        uvi = UVI(corpora_path='corpora', load_all=False)
        print("[PASS] UVI initialization works")
        
        # Test basic methods
        supported_corpora = uvi.supported_corpora
        print(f"[PASS] UVI supports {len(supported_corpora)} corpora: {supported_corpora}")
        
        corpus_info = uvi.get_corpus_info()
        print(f"[PASS] UVI corpus info method works, found info for {len(corpus_info)} corpora")
        
        # Test that methods exist (even if they return placeholders)
        profile = uvi.get_complete_semantic_profile('test')
        print(f"[PASS] get_complete_semantic_profile method exists")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] UVI initialization failed: {e}")
        return False

def test_package_metadata():
    """Test package metadata."""
    print("\nTesting package metadata...")
    
    try:
        from uvi import get_version, get_supported_corpora
        
        version = get_version()
        print(f"[PASS] UVI version: {version}")
        
        supported_corpora = get_supported_corpora()
        print(f"[PASS] Supported corpora: {len(supported_corpora)} types")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Package metadata test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("UVI Package Structure Test")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_parser_imports,
        test_utils_imports,
        test_uvi_initialization,
        test_package_metadata
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("SUCCESS: All tests passed! UVI package structure is working correctly.")
        return 0
    else:
        print("FAILURE: Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())