"""
CorpusCollectionValidator Class

A class for validating corpus collection integrity and cross-references.
This class is responsible for validating VerbNet, FrameNet, PropBank collections
and their cross-references.

Extracted from CorpusLoader as part of the refactoring plan to separate concerns.
"""

from typing import Dict, Any
import logging


class CorpusCollectionValidator:
    """
    A class for validating corpus collection integrity and cross-references.
    """
    
    def __init__(self, loaded_data: Dict[str, Any], logger: logging.Logger):
        """
        Initialize CorpusCollectionValidator with loaded data and logger.
        
        Args:
            loaded_data (dict): Dictionary containing all loaded corpus data
            logger (logging.Logger): Logger instance for error reporting
        """
        self.loaded_data = loaded_data
        self.logger = logger
    
    def validate_collections(self) -> Dict[str, Any]:
        """
        Validate integrity of all collections.
        
        Returns:
            dict: Validation results for each collection
        """
        validation_results = {}
        
        for corpus_name, corpus_data in self.loaded_data.items():
            try:
                if corpus_name == 'verbnet':
                    validation_results[corpus_name] = self._validate_verbnet_collection(corpus_data)
                elif corpus_name == 'framenet':
                    validation_results[corpus_name] = self._validate_framenet_collection(corpus_data)
                elif corpus_name == 'propbank':
                    validation_results[corpus_name] = self._validate_propbank_collection(corpus_data)
                else:
                    validation_results[corpus_name] = {'status': 'no_validation', 'errors': []}
                    
            except Exception as e:
                validation_results[corpus_name] = {
                    'status': 'validation_error',
                    'errors': [str(e)]
                }
        
        return validation_results
    
    def _validate_verbnet_collection(self, verbnet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate VerbNet collection integrity.
        
        Args:
            verbnet_data (dict): VerbNet data to validate
            
        Returns:
            dict: Validation results
        """
        errors = []
        warnings = []
        
        classes = verbnet_data.get('classes', {})
        if classes is None:
            classes = {}
        
        # Check for empty classes
        for class_id, class_data in classes.items():
            if not class_data.get('members'):
                warnings.append(f"Class {class_id} has no members")
            
            if not class_data.get('frames'):
                warnings.append(f"Class {class_id} has no frames")
            
            # Validate frame structure
            frames = class_data.get('frames', [])
            if frames is None:
                frames = []
            for i, frame in enumerate(frames):
                if not frame.get('description', {}).get('primary'):
                    warnings.append(f"Class {class_id} frame {i} missing primary description")
        
        status = 'valid' if not errors else 'invalid'
        if warnings and status == 'valid':
            status = 'valid_with_warnings'
        
        return {
            'status': status,
            'errors': errors,
            'warnings': warnings,
            'total_classes': len(classes)
        }
    
    def _validate_framenet_collection(self, framenet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate FrameNet collection integrity.
        
        Args:
            framenet_data (dict): FrameNet data to validate
            
        Returns:
            dict: Validation results
        """
        errors = []
        warnings = []
        
        frames = framenet_data.get('frames', {})
        if frames is None:
            frames = {}
        
        # Check for frames without lexical units
        for frame_name, frame_data in frames.items():
            if not frame_data.get('lexical_units'):
                warnings.append(f"Frame {frame_name} has no lexical units")
            
            if not frame_data.get('definition'):
                warnings.append(f"Frame {frame_name} missing definition")
        
        status = 'valid' if not errors else 'invalid'
        if warnings and status == 'valid':
            status = 'valid_with_warnings'
        
        return {
            'status': status,
            'errors': errors,
            'warnings': warnings,
            'total_frames': len(frames)
        }
    
    def _validate_propbank_collection(self, propbank_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate PropBank collection integrity.
        
        Args:
            propbank_data (dict): PropBank data to validate
            
        Returns:
            dict: Validation results
        """
        errors = []
        warnings = []
        
        predicates = propbank_data.get('predicates', {})
        if predicates is None:
            predicates = {}
        
        # Check for predicates without rolesets
        for lemma, predicate_data in predicates.items():
            if not predicate_data.get('rolesets'):
                warnings.append(f"Predicate {lemma} has no rolesets")
            
            rolesets = predicate_data.get('rolesets', [])
            if rolesets is None:
                rolesets = []
            for roleset in rolesets:
                if not roleset.get('roles'):
                    warnings.append(f"Roleset {roleset.get('id', 'unknown')} has no roles")
        
        status = 'valid' if not errors else 'invalid'
        if warnings and status == 'valid':
            status = 'valid_with_warnings'
        
        return {
            'status': status,
            'errors': errors,
            'warnings': warnings,
            'total_predicates': len(predicates)
        }
    
    def validate_cross_references(self) -> Dict[str, Any]:
        """
        Validate cross-references between collections.
        
        Returns:
            dict: Cross-reference validation results
        """
        validation_results = {
            'vn_pb_mappings': {},
            'vn_fn_mappings': {},
            'vn_wn_mappings': {},
            'on_mappings': {}
        }
        
        # Validate VerbNet-PropBank mappings
        if 'verbnet' in self.loaded_data and 'propbank' in self.loaded_data:
            validation_results['vn_pb_mappings'] = self._validate_vn_pb_mappings()
        
        # Add other cross-reference validations as needed
        
        return validation_results
    
    def _validate_vn_pb_mappings(self) -> Dict[str, Any]:
        """
        Validate VerbNet-PropBank mappings.
        
        Returns:
            dict: VN-PB mapping validation results
        """
        errors = []
        warnings = []
        
        verbnet_data = self.loaded_data['verbnet']
        propbank_data = self.loaded_data['propbank']
        
        vn_classes = verbnet_data.get('classes', {})
        pb_predicates = propbank_data.get('predicates', {})
        
        # Check for missing cross-references
        # This is a placeholder - actual validation would depend on mapping structure
        
        return {
            'status': 'checked',
            'errors': errors,
            'warnings': warnings
        }