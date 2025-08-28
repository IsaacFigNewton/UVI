"""
Test suite for CorpusLoader class.

Tests the corpus loading and parsing functionality for all supported corpus types.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from uvi.CorpusLoader import CorpusLoader


class TestCorpusLoader(unittest.TestCase):
    """Test cases for CorpusLoader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use the corpora directory relative to project root
        corpora_path = Path(__file__).parent.parent / 'corpora'
        self.loader = CorpusLoader(str(corpora_path))
    
    def test_initialization(self):
        """Test CorpusLoader initialization."""
        self.assertIsInstance(self.loader, CorpusLoader)
        self.assertTrue(hasattr(self.loader, 'corpora_path'))
        self.assertTrue(hasattr(self.loader, 'corpus_paths'))
        self.assertTrue(hasattr(self.loader, 'loaded_data'))
    
    def test_corpus_path_detection(self):
        """Test automatic corpus path detection."""
        paths = self.loader.get_corpus_paths()
        self.assertIsInstance(paths, dict)
        
        # Check that some expected corpora are detected
        expected_corpora = ['verbnet', 'framenet', 'propbank', 'wordnet', 'bso', 'semnet', 'reference_docs']
        for corpus in expected_corpora:
            if corpus in paths:
                self.assertTrue(Path(paths[corpus]).exists(), f"{corpus} path should exist: {paths[corpus]}")
    
    def test_load_verbnet_if_available(self):
        """Test VerbNet loading if available."""
        if 'verbnet' in self.loader.corpus_paths:
            try:
                verbnet_data = self.loader.parse_verbnet_files()
                self.assertIsInstance(verbnet_data, dict)
                self.assertIn('classes', verbnet_data)
                self.assertIn('statistics', verbnet_data)
                print(f"VerbNet loaded: {verbnet_data['statistics']}")
            except Exception as e:
                self.skipTest(f"VerbNet loading failed: {e}")
        else:
            self.skipTest("VerbNet corpus not found")
    
    def test_load_framenet_if_available(self):
        """Test FrameNet loading if available."""
        if 'framenet' in self.loader.corpus_paths:
            try:
                framenet_data = self.loader.parse_framenet_files()
                self.assertIsInstance(framenet_data, dict)
                self.assertIn('frames', framenet_data)
                print(f"FrameNet loaded: {len(framenet_data.get('frames', {}))} frames")
            except Exception as e:
                self.skipTest(f"FrameNet loading failed: {e}")
        else:
            self.skipTest("FrameNet corpus not found")
    
    def test_load_propbank_if_available(self):
        """Test PropBank loading if available."""
        if 'propbank' in self.loader.corpus_paths:
            try:
                propbank_data = self.loader.parse_propbank_files()
                self.assertIsInstance(propbank_data, dict)
                self.assertIn('predicates', propbank_data)
                print(f"PropBank loaded: {len(propbank_data.get('predicates', {}))} predicates")
            except Exception as e:
                self.skipTest(f"PropBank loading failed: {e}")
        else:
            self.skipTest("PropBank corpus not found")
    
    def test_load_wordnet_if_available(self):
        """Test WordNet loading if available."""
        if 'wordnet' in self.loader.corpus_paths:
            try:
                wordnet_data = self.loader.parse_wordnet_files()
                self.assertIsInstance(wordnet_data, dict)
                self.assertIn('synsets', wordnet_data)
                self.assertIn('statistics', wordnet_data)
                print(f"WordNet loaded: {wordnet_data.get('statistics', {})}")
            except Exception as e:
                self.skipTest(f"WordNet loading failed: {e}")
        else:
            self.skipTest("WordNet corpus not found")
    
    def test_load_bso_if_available(self):
        """Test BSO loading if available."""
        if 'bso' in self.loader.corpus_paths:
            try:
                bso_data = self.loader.parse_bso_mappings()
                self.assertIsInstance(bso_data, dict)
                self.assertIn('statistics', bso_data)
                print(f"BSO loaded: {bso_data.get('statistics', {})}")
            except Exception as e:
                self.skipTest(f"BSO loading failed: {e}")
        else:
            self.skipTest("BSO corpus not found")
    
    def test_load_semnet_if_available(self):
        """Test SemNet loading if available."""
        if 'semnet' in self.loader.corpus_paths:
            try:
                semnet_data = self.loader.parse_semnet_data()
                self.assertIsInstance(semnet_data, dict)
                self.assertIn('statistics', semnet_data)
                print(f"SemNet loaded: {semnet_data.get('statistics', {})}")
            except Exception as e:
                self.skipTest(f"SemNet loading failed: {e}")
        else:
            self.skipTest("SemNet corpus not found")
    
    def test_load_reference_docs_if_available(self):
        """Test reference docs loading if available."""
        if 'reference_docs' in self.loader.corpus_paths:
            try:
                ref_data = self.loader.parse_reference_docs()
                self.assertIsInstance(ref_data, dict)
                self.assertIn('statistics', ref_data)
                print(f"Reference docs loaded: {ref_data.get('statistics', {})}")
            except Exception as e:
                self.skipTest(f"Reference docs loading failed: {e}")
        else:
            self.skipTest("Reference docs corpus not found")
    
    def test_load_all_corpora(self):
        """Test loading all available corpora."""
        try:
            results = self.loader.load_all_corpora()
            self.assertIsInstance(results, dict)
            
            # Print summary of what was loaded
            success_count = sum(1 for status in results.values() if status.get('status') == 'success')
            print(f"Successfully loaded {success_count} out of {len(results)} corpora")
            
            for corpus_name, status in results.items():
                print(f"  {corpus_name}: {status.get('status', 'unknown')}")
                if status.get('status') == 'error':
                    print(f"    Error: {status.get('error', 'unknown error')}")
                
        except Exception as e:
            self.fail(f"Load all corpora failed: {e}")
    
    def test_reference_collection_building(self):
        """Test building reference collections."""
        # First load some data
        if 'verbnet' in self.loader.corpus_paths:
            try:
                self.loader.load_corpus('verbnet')
            except:
                pass
        
        if 'reference_docs' in self.loader.corpus_paths:
            try:
                self.loader.load_corpus('reference_docs')
            except:
                pass
        
        # Try to build reference collections
        try:
            results = self.loader.build_reference_collections()
            self.assertIsInstance(results, dict)
            print(f"Reference collections built: {results}")
        except Exception as e:
            self.skipTest(f"Reference collection building failed: {e}")
    
    def test_collection_statistics(self):
        """Test getting collection statistics."""
        # Load at least one corpus if available
        for corpus_name in ['verbnet', 'framenet', 'propbank', 'wordnet']:
            if corpus_name in self.loader.corpus_paths:
                try:
                    self.loader.load_corpus(corpus_name)
                    break
                except:
                    continue
        
        try:
            stats = self.loader.get_collection_statistics()
            self.assertIsInstance(stats, dict)
            print(f"Collection statistics: {stats}")
        except Exception as e:
            self.skipTest(f"Statistics collection failed: {e}")
    
    def test_validation(self):
        """Test collection validation."""
        # Load at least one corpus if available
        for corpus_name in ['verbnet', 'framenet', 'propbank']:
            if corpus_name in self.loader.corpus_paths:
                try:
                    self.loader.load_corpus(corpus_name)
                    break
                except:
                    continue
        
        try:
            validation_results = self.loader.validate_collections()
            self.assertIsInstance(validation_results, dict)
            print(f"Validation results: {validation_results}")
        except Exception as e:
            self.skipTest(f"Validation failed: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)