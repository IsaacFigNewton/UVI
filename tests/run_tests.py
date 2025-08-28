#!/usr/bin/env python3
"""
Simple test runner for UVI package tests.

This script provides a convenient way to run all tests with proper output formatting.
"""

import sys
import unittest
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def run_tests():
    """Run all UVI tests with comprehensive output."""
    
    print("=" * 60)
    print("UVI (Unified Verb Index) - Test Suite")
    print("=" * 60)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    # Run with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=True
    )
    
    print("\nRunning UVI unit tests...\n")
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n[SUCCESS] ALL TESTS PASSED")
        print("The UVI package is functioning correctly!")
    else:
        print("\n[FAILED] SOME TESTS FAILED")
        print("Please review the test output above.")
    
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)