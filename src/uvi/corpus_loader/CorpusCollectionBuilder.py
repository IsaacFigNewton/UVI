"""
CorpusCollectionBuilder Class

A specialized class for building reference collections from loaded corpus data.
This class extracts reference data building methods from the CorpusLoader class
to provide focused functionality for constructing reference collections.

This class builds collections for:
- Predicate definitions
- Thematic role definitions  
- Verb-specific features
- Syntactic restrictions
- Selectional restrictions
"""

from typing import Dict, Any, List, Set
import logging


class CorpusCollectionBuilder:
    """
    A specialized class for building reference collections from loaded corpus data.
    
    This class handles the construction of various reference collections that are
    derived from the loaded corpus data, including predicate definitions, thematic
    role definitions, verb-specific features, syntactic restrictions, and 
    selectional restrictions.
    """
    
    def __init__(self, loaded_data: Dict[str, Any], logger: logging.Logger):
        """
        Initialize CorpusCollectionBuilder with loaded corpus data and logger.
        
        Args:
            loaded_data (Dict[str, Any]): Dictionary containing all loaded corpus data
            logger (logging.Logger): Logger instance for logging operations
        """
        self.loaded_data = loaded_data
        self.logger = logger
        self.reference_collections = {}
    
    def build_reference_collections(self) -> Dict[str, bool]:
        """
        Build all reference collections for VerbNet components.
        
        Returns:
            dict: Status of reference collection builds
        """
        results = {
            'predicate_definitions': self.build_predicate_definitions(),
            'themrole_definitions': self.build_themrole_definitions(),
            'verb_specific_features': self.build_verb_specific_features(),
            'syntactic_restrictions': self.build_syntactic_restrictions(),
            'selectional_restrictions': self.build_selectional_restrictions()
        }
        
        self.logger.info(f"Reference collections build complete: {sum(results.values())}/{len(results)} successful")
        
        return results
    
    def build_predicate_definitions(self) -> bool:
        """
        Build predicate definitions collection.
        
        Returns:
            bool: Success status
        """
        try:
            if 'reference_docs' in self.loaded_data:
                ref_data = self.loaded_data['reference_docs']
                predicates = ref_data.get('predicates', {})
                
                self.reference_collections['predicates'] = predicates
                self.logger.info(f"Built predicate definitions: {len(predicates)} predicates")
                return True
            else:
                self.logger.warning("Reference docs not loaded, cannot build predicate definitions")
                return False
        except Exception as e:
            self.logger.error(f"Error building predicate definitions: {e}")
            return False
    
    def build_themrole_definitions(self) -> bool:
        """
        Build thematic role definitions collection.
        
        Returns:
            bool: Success status
        """
        try:
            if 'reference_docs' in self.loaded_data:
                ref_data = self.loaded_data['reference_docs']
                themroles = ref_data.get('themroles', {})
                
                self.reference_collections['themroles'] = themroles
                self.logger.info(f"Built thematic role definitions: {len(themroles)} roles")
                return True
            else:
                self.logger.warning("Reference docs not loaded, cannot build themrole definitions")
                return False
        except Exception as e:
            self.logger.error(f"Error building themrole definitions: {e}")
            return False
    
    def build_verb_specific_features(self) -> bool:
        """
        Build verb-specific features collection.
        
        Returns:
            bool: Success status
        """
        try:
            features = set()
            
            # Extract from VerbNet data if available
            if 'verbnet' in self.loaded_data:
                verbnet_data = self.loaded_data['verbnet']
                classes = verbnet_data.get('classes', {})
                
                for class_data in classes.values():
                    for frame in class_data.get('frames', []):
                        for semantics_group in frame.get('semantics', []):
                            for pred in semantics_group:
                                if pred.get('value'):
                                    features.add(pred['value'])
            
            # Extract from reference docs if available
            if 'reference_docs' in self.loaded_data:
                ref_data = self.loaded_data['reference_docs']
                vs_features = ref_data.get('verb_specific', {})
                features.update(vs_features.keys())
            
            self.reference_collections['verb_specific_features'] = sorted(list(features))
            self.logger.info(f"Built verb-specific features: {len(features)} features")
            return True
            
        except Exception as e:
            self.logger.error(f"Error building verb-specific features: {e}")
            return False
    
    def build_syntactic_restrictions(self) -> bool:
        """
        Build syntactic restrictions collection.
        
        Returns:
            bool: Success status
        """
        try:
            restrictions = set()
            
            # Extract from VerbNet data if available
            if 'verbnet' in self.loaded_data:
                verbnet_data = self.loaded_data['verbnet']
                classes = verbnet_data.get('classes', {})
                
                for class_data in classes.values():
                    for frame in class_data.get('frames', []):
                        for syntax_group in frame.get('syntax', []):
                            for element in syntax_group:
                                for synrestr in element.get('synrestrs', []):
                                    if synrestr.get('Value'):
                                        restrictions.add(synrestr['Value'])
            
            self.reference_collections['syntactic_restrictions'] = sorted(list(restrictions))
            self.logger.info(f"Built syntactic restrictions: {len(restrictions)} restrictions")
            return True
            
        except Exception as e:
            self.logger.error(f"Error building syntactic restrictions: {e}")
            return False
    
    def build_selectional_restrictions(self) -> bool:
        """
        Build selectional restrictions collection.
        
        Returns:
            bool: Success status
        """
        try:
            restrictions = set()
            
            # Extract from VerbNet data if available
            if 'verbnet' in self.loaded_data:
                verbnet_data = self.loaded_data['verbnet']
                classes = verbnet_data.get('classes', {})
                
                for class_data in classes.values():
                    for themrole in class_data.get('themroles', []):
                        for selrestr in themrole.get('selrestrs', []):
                            if selrestr.get('Value'):
                                restrictions.add(selrestr['Value'])
            
            self.reference_collections['selectional_restrictions'] = sorted(list(restrictions))
            self.logger.info(f"Built selectional restrictions: {len(restrictions)} restrictions")
            return True
            
        except Exception as e:
            self.logger.error(f"Error building selectional restrictions: {e}")
            return False