#!/usr/bin/env python3
"""
Basic Usage Example for UVI (Unified Verb Index) Package

This script demonstrates the basic functionality of the UVI package
implemented in Phase 1, including corpus detection, loading, and
basic data access.
"""

import sys
import os
from pathlib import Path

# Add src directory to path for importing UVI
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi.UVI import UVI

def main():
    """Demonstrate basic UVI functionality."""
    
    print("=" * 60)
    print("UVI (Unified Verb Index) - Basic Usage Example")
    print("=" * 60)
    
    # Initialize UVI without loading all corpora (for demonstration)
    print("\n1. Initializing UVI...")
    try:
        uvi = UVI(corpora_path='corpora/', load_all=False)
        print(f"   SUCCESS: UVI initialized successfully")
        print(f"   Package module: {uvi.__class__.__module__}")
    except Exception as e:
        print(f"   ERROR: Error initializing UVI: {e}")
        return
    
    # Show detected corpora
    print("\n2. Detected Corpora:")
    corpus_info = uvi.get_corpus_info()
    for corpus_name, info in corpus_info.items():
        status = "FOUND" if info['path'] != 'Not found' else "MISSING"
        print(f"   {status:7} {corpus_name:15} -> {info['path']}")
    
    # Show supported corpora
    print(f"\n3. Supported Corpora: {len(uvi.supported_corpora)} total")
    for i, corpus in enumerate(uvi.supported_corpora, 1):
        print(f"   {i:2}. {corpus}")
    
    # Load and demonstrate VerbNet parsing
    print("\n4. Loading VerbNet Corpus...")
    if 'verbnet' in uvi.corpus_paths:
        try:
            uvi._load_corpus('verbnet')
            if uvi.is_corpus_loaded('verbnet'):
                verbnet_data = uvi.corpora_data['verbnet']
                classes = verbnet_data.get('classes', {})
                print(f"   SUCCESS: VerbNet loaded successfully")
                print(f"   Classes loaded: {len(classes)}")
                
                # Show sample class information
                if classes:
                    print("\n5. Sample VerbNet Class Information:")
                    sample_classes = list(classes.items())[:3]
                    
                    for class_id, class_data in sample_classes:
                        print(f"\n   Class: {class_id}")
                        print(f"   |-- Members: {len(class_data.get('members', []))}")
                        print(f"   |-- Thematic Roles: {len(class_data.get('themroles', []))}")
                        print(f"   |-- Frames: {len(class_data.get('frames', []))}")
                        print(f"   +-- Subclasses: {len(class_data.get('subclasses', []))}")
                        
                        # Show sample members
                        members = class_data.get('members', [])
                        if members:
                            member_names = [m.get('name', 'N/A') for m in members[:3]]
                            print(f"       Sample members: {', '.join(member_names)}")
                
                print(f"\n6. Loaded Corpora: {uvi.get_loaded_corpora()}")
                
            else:
                print("   ERROR: VerbNet failed to load")
        except Exception as e:
            print(f"   ERROR: Error loading VerbNet: {e}")
    else:
        print("   ERROR: VerbNet corpus not found")
    
    print("\n7. UVI Package Information:")
    try:
        import uvi
        print(f"   SUCCESS: Package version: {uvi.get_version()}")
        print(f"   Supported corpora count: {len(uvi.get_supported_corpora())}")
    except Exception as e:
        print(f"   ERROR: Error accessing package info: {e}")
    
    print("\n" + "=" * 60)
    print("Phase 1 Implementation Complete!")
    print("=" * 60)
    print("\nPhase 1 Features Implemented:")
    print("- Basic UVI class structure with __init__ method")
    print("- Import dependencies (xml, json, csv, pathlib, re)")
    print("- Corpus file path configuration and auto-detection")
    print("- Corpus data loaders for all 9 corpora (scaffolding)")
    print("- File system navigation methods")
    print("- VerbNet XML parsing (fully functional)")
    print("- Package initialization with __init__.py")
    print("- Basic utility methods for corpus management")
    print("\nNext: Implement Phase 2 - Complete corpus file parsers")

if __name__ == "__main__":
    main()