"""
CorpusCollectionAnalyzer Class

A specialized class for analyzing corpus collection data and providing
statistics and metadata about loaded corpora and their relationships.

This class is part of the CorpusLoader refactoring to separate concerns
and improve maintainability.
"""

from typing import Dict, Any
from datetime import datetime


class CorpusCollectionAnalyzer:
    """
    A specialized class for analyzing corpus collection data and providing
    statistics and metadata.
    
    This class handles the analysis of loaded corpus data, generating
    statistics and metadata reports for all loaded collections.
    """
    
    def __init__(self, loaded_data: Dict[str, Any], load_status: Dict[str, Any], 
                 build_metadata: Dict[str, Any], reference_collections: Dict[str, Any],
                 corpus_paths: Dict[str, str]):
        """
        Initialize the CorpusCollectionAnalyzer.
        
        Args:
            loaded_data: Dictionary containing all loaded corpus data
            load_status: Dictionary tracking load status of each corpus
            build_metadata: Dictionary containing build timestamps and metadata
            reference_collections: Dictionary of built reference collections
            corpus_paths: Dictionary mapping corpus names to their file paths
        """
        self.loaded_data = loaded_data
        self.load_status = load_status
        self.build_metadata = build_metadata
        self.reference_collections = reference_collections
        self.corpus_paths = corpus_paths
    
    def get_collection_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for all collections.
        
        Returns:
            dict: Statistics for each collection
        """
        statistics = {}
        
        for corpus_name, corpus_data in self.loaded_data.items():
            try:
                if corpus_name == 'verbnet':
                    stats = corpus_data.get('statistics', {})
                    stats.update({
                        'classes': len(corpus_data.get('classes', {})),
                        'members': len(corpus_data.get('members', {}))
                    })
                    statistics[corpus_name] = stats
                    
                elif corpus_name == 'framenet':
                    stats = corpus_data.get('statistics', {})
                    stats.update({
                        'frames': len(corpus_data.get('frames', {})),
                        'lexical_units': len(corpus_data.get('lexical_units', {}))
                    })
                    statistics[corpus_name] = stats
                    
                elif corpus_name == 'propbank':
                    stats = corpus_data.get('statistics', {})
                    stats.update({
                        'predicates': len(corpus_data.get('predicates', {})),
                        'rolesets': len(corpus_data.get('rolesets', {}))
                    })
                    statistics[corpus_name] = stats
                    
                else:
                    statistics[corpus_name] = corpus_data.get('statistics', {})
                    
            except Exception as e:
                statistics[corpus_name] = {'error': str(e)}
        
        # Add reference collection statistics
        statistics['reference_collections'] = {
            name: len(collection) if isinstance(collection, (list, dict, set)) else 0
            for name, collection in self.reference_collections.items()
        }
        
        return statistics
    
    def get_build_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about last build times and versions.
        
        Returns:
            dict: Build metadata
        """
        return {
            'build_metadata': self.build_metadata,
            'load_status': self.load_status,
            'corpus_paths': self.corpus_paths,
            'timestamp': datetime.now().isoformat()
        }