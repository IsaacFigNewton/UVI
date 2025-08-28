"""
UVI (Unified Verb Index) Package

A comprehensive standalone class providing integrated access to all nine linguistic 
corpora (VerbNet, FrameNet, PropBank, OntoNotes, WordNet, BSO, SemNet, Reference Docs, 
VN API) with cross-resource navigation, semantic validation, and hierarchical analysis 
capabilities.

This class implements the universal interface patterns and shared semantic frameworks 
documented in corpora/OVERVIEW.md, enabling seamless cross-corpus integration and validation.
"""

import xml.etree.ElementTree as ET
import json
import csv
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
import os


class UVI:
    """
    Unified Verb Index: A comprehensive standalone class providing integrated access 
    to all nine linguistic corpora (VerbNet, FrameNet, PropBank, OntoNotes, WordNet,
    BSO, SemNet, Reference Docs, VN API) with cross-resource navigation, semantic 
    validation, and hierarchical analysis capabilities.
    
    This class implements the universal interface patterns and shared semantic 
    frameworks documented in corpora/OVERVIEW.md, enabling seamless cross-corpus
    integration and validation.
    """
    
    def __init__(self, corpora_path: str = 'corpora/', load_all: bool = True):
        """
        Initialize UVI with corpus file paths for standalone operation.
        
        Args:
            corpora_path (str): Path to the corpora directory containing all corpus files
            load_all (bool): Load all corpora on initialization
        """
        self.corpora_path = Path(corpora_path)
        self.load_all = load_all
        
        # Initialize corpus data storage
        self.corpora_data = {}
        self.corpus_paths = {}
        self.loaded_corpora = set()
        
        # Supported corpus types
        self.supported_corpora = [
            'verbnet', 'framenet', 'propbank', 'ontonotes', 'wordnet',
            'bso', 'semnet', 'reference_docs', 'vn_api'
        ]
        
        # Initialize corpus file paths
        self._setup_corpus_paths()
        
        # Load corpora if requested
        if load_all:
            self._load_all_corpora()
    
    def _setup_corpus_paths(self) -> None:
        """
        Set up corpus file paths for all supported corpora.
        Auto-detect corpus directory structures and handle missing corpora gracefully.
        """
        if not self.corpora_path.exists():
            raise FileNotFoundError(f"Corpora directory not found: {self.corpora_path}")
        
        # Define expected corpus directory structures
        corpus_structure = {
            'verbnet': ['verbnet3.4', 'verbnet', 'vn'],
            'framenet': ['framenet', 'fn', 'framenet1.7'],
            'propbank': ['propbank', 'pb', 'propbank3.4'],
            'ontonotes': ['ontonotes', 'on', 'ontonotes5.0'],
            'wordnet': ['wordnet', 'wn', 'wordnet3.1'],
            'bso': ['bso', 'basic_semantic_ontology'],
            'semnet': ['semnet', 'semantic_network'],
            'reference_docs': ['reference_docs', 'ref_docs', 'docs'],
            'vn_api': ['vn_api', 'verbnet_api']
        }
        
        # Auto-detect corpus paths
        for corpus_name, possible_dirs in corpus_structure.items():
            corpus_path = None
            for dir_name in possible_dirs:
                candidate_path = self.corpora_path / dir_name
                if candidate_path.exists():
                    corpus_path = candidate_path
                    break
            
            if corpus_path:
                self.corpus_paths[corpus_name] = corpus_path
            else:
                print(f"Warning: {corpus_name} corpus not found in {self.corpora_path}")
    
    def _load_all_corpora(self) -> None:
        """
        Load and parse all available corpus files.
        """
        for corpus_name in self.supported_corpora:
            if corpus_name in self.corpus_paths:
                try:
                    self._load_corpus(corpus_name)
                except Exception as e:
                    print(f"Error loading {corpus_name}: {e}")
    
    def _load_corpus(self, corpus_name: str) -> None:
        """
        Load a specific corpus by name.
        
        Args:
            corpus_name (str): Name of corpus to load
        """
        if corpus_name not in self.corpus_paths:
            raise FileNotFoundError(f"Corpus {corpus_name} path not found")
        
        corpus_path = self.corpus_paths[corpus_name]
        
        # Load corpus based on type
        if corpus_name == 'verbnet':
            self._load_verbnet(corpus_path)
        elif corpus_name == 'framenet':
            self._load_framenet(corpus_path)
        elif corpus_name == 'propbank':
            self._load_propbank(corpus_path)
        elif corpus_name == 'ontonotes':
            self._load_ontonotes(corpus_path)
        elif corpus_name == 'wordnet':
            self._load_wordnet(corpus_path)
        elif corpus_name == 'bso':
            self._load_bso(corpus_path)
        elif corpus_name == 'semnet':
            self._load_semnet(corpus_path)
        elif corpus_name == 'reference_docs':
            self._load_reference_docs(corpus_path)
        elif corpus_name == 'vn_api':
            self._load_vn_api(corpus_path)
        
        self.loaded_corpora.add(corpus_name)
    
    def _load_verbnet(self, corpus_path: Path) -> None:
        """
        Load VerbNet XML files and build internal data structures.
        
        Args:
            corpus_path (Path): Path to VerbNet corpus directory
        """
        verbnet_data = {
            'classes': {},
            'hierarchy': {},
            'members': {}
        }
        
        # Find VerbNet XML files
        xml_files = list(corpus_path.glob('*.xml'))
        if not xml_files:
            xml_files = list(corpus_path.glob('**/*.xml'))
        
        for xml_file in xml_files:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # Extract class information
                if root.tag == 'VNCLASS':
                    class_id = root.get('ID')
                    if class_id:
                        verbnet_data['classes'][class_id] = self._parse_verbnet_class(root)
            except Exception as e:
                print(f"Error parsing VerbNet file {xml_file}: {e}")
        
        self.corpora_data['verbnet'] = verbnet_data
    
    def _parse_verbnet_class(self, class_element: ET.Element) -> Dict[str, Any]:
        """
        Parse a VerbNet class XML element.
        
        Args:
            class_element (ET.Element): VerbNet class XML element
            
        Returns:
            dict: Parsed VerbNet class data
        """
        class_data = {
            'id': class_element.get('ID'),
            'members': [],
            'themroles': [],
            'frames': [],
            'subclasses': []
        }
        
        # Extract members
        for member in class_element.findall('.//MEMBER'):
            member_data = {
                'name': member.get('name'),
                'wn': member.get('wn'),
                'grouping': member.get('grouping')
            }
            class_data['members'].append(member_data)
        
        # Extract thematic roles
        for themrole in class_element.findall('.//THEMROLE'):
            role_data = {
                'type': themrole.get('type'),
                'selrestrs': []
            }
            # Extract selectional restrictions
            for selrestr in themrole.findall('.//SELRESTR'):
                selrestr_data = {
                    'Value': selrestr.get('Value'),
                    'type': selrestr.get('type')
                }
                role_data['selrestrs'].append(selrestr_data)
            
            class_data['themroles'].append(role_data)
        
        # Extract frames
        for frame in class_element.findall('.//FRAME'):
            frame_data = {
                'description': self._extract_frame_description(frame),
                'examples': [],
                'syntax': [],
                'semantics': []
            }
            
            # Extract examples
            for example in frame.findall('.//EXAMPLE'):
                frame_data['examples'].append(example.text)
            
            # Extract syntax
            for syntax in frame.findall('.//SYNTAX'):
                syntax_data = []
                for np in syntax.findall('.//NP'):
                    np_data = {
                        'value': np.get('value'),
                        'synrestrs': []
                    }
                    for synrestr in np.findall('.//SYNRESTR'):
                        synrestr_data = {
                            'Value': synrestr.get('Value'),
                            'type': synrestr.get('type')
                        }
                        np_data['synrestrs'].append(synrestr_data)
                    syntax_data.append(np_data)
                frame_data['syntax'] = syntax_data
            
            # Extract semantics
            for semantics in frame.findall('.//SEMANTICS'):
                semantics_data = []
                for pred in semantics.findall('.//PRED'):
                    pred_data = {
                        'value': pred.get('value'),
                        'args': []
                    }
                    for arg in pred.findall('.//ARG'):
                        arg_data = {
                            'type': arg.get('type'),
                            'value': arg.get('value')
                        }
                        pred_data['args'].append(arg_data)
                    semantics_data.append(pred_data)
                frame_data['semantics'] = semantics_data
            
            class_data['frames'].append(frame_data)
        
        # Extract subclasses
        for subclass in class_element.findall('.//VNSUBCLASS'):
            subclass_data = self._parse_verbnet_class(subclass)
            class_data['subclasses'].append(subclass_data)
        
        return class_data
    
    def _extract_frame_description(self, frame_element: ET.Element) -> Dict[str, str]:
        """
        Extract frame description from VerbNet frame element.
        
        Args:
            frame_element (ET.Element): VerbNet frame XML element
            
        Returns:
            dict: Frame description data
        """
        description = {
            'primary': frame_element.get('primary', ''),
            'secondary': frame_element.get('secondary', ''),
            'descriptionNumber': frame_element.get('descriptionNumber', ''),
            'xtag': frame_element.get('xtag', '')
        }
        return description
    
    def _load_framenet(self, corpus_path: Path) -> None:
        """
        Load FrameNet XML files.
        
        Args:
            corpus_path (Path): Path to FrameNet corpus directory
        """
        # Placeholder for FrameNet loading logic
        self.corpora_data['framenet'] = {}
    
    def _load_propbank(self, corpus_path: Path) -> None:
        """
        Load PropBank XML files.
        
        Args:
            corpus_path (Path): Path to PropBank corpus directory
        """
        # Placeholder for PropBank loading logic
        self.corpora_data['propbank'] = {}
    
    def _load_ontonotes(self, corpus_path: Path) -> None:
        """
        Load OntoNotes data.
        
        Args:
            corpus_path (Path): Path to OntoNotes corpus directory
        """
        # Placeholder for OntoNotes loading logic
        self.corpora_data['ontonotes'] = {}
    
    def _load_wordnet(self, corpus_path: Path) -> None:
        """
        Load WordNet data files.
        
        Args:
            corpus_path (Path): Path to WordNet corpus directory
        """
        # Placeholder for WordNet loading logic
        self.corpora_data['wordnet'] = {}
    
    def _load_bso(self, corpus_path: Path) -> None:
        """
        Load BSO CSV mapping files.
        
        Args:
            corpus_path (Path): Path to BSO corpus directory
        """
        # Placeholder for BSO loading logic
        self.corpora_data['bso'] = {}
    
    def _load_semnet(self, corpus_path: Path) -> None:
        """
        Load SemNet JSON files.
        
        Args:
            corpus_path (Path): Path to SemNet corpus directory
        """
        # Placeholder for SemNet loading logic
        self.corpora_data['semnet'] = {}
    
    def _load_reference_docs(self, corpus_path: Path) -> None:
        """
        Load reference documentation files.
        
        Args:
            corpus_path (Path): Path to reference docs directory
        """
        # Placeholder for reference docs loading logic
        self.corpora_data['reference_docs'] = {}
    
    def _load_vn_api(self, corpus_path: Path) -> None:
        """
        Load VN API enhanced XML files.
        
        Args:
            corpus_path (Path): Path to VN API corpus directory
        """
        # Placeholder for VN API loading logic
        self.corpora_data['vn_api'] = {}
    
    # Utility methods
    def get_loaded_corpora(self) -> List[str]:
        """
        Get list of successfully loaded corpora.
        
        Returns:
            list: Names of loaded corpora
        """
        return list(self.loaded_corpora)
    
    def is_corpus_loaded(self, corpus_name: str) -> bool:
        """
        Check if a corpus is loaded.
        
        Args:
            corpus_name (str): Name of corpus to check
            
        Returns:
            bool: True if corpus is loaded
        """
        return corpus_name in self.loaded_corpora
    
    def get_corpus_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all detected and loaded corpora.
        
        Returns:
            dict: Corpus information including paths and load status
        """
        corpus_info = {}
        for corpus_name in self.supported_corpora:
            corpus_info[corpus_name] = {
                'path': str(self.corpus_paths.get(corpus_name, 'Not found')),
                'loaded': corpus_name in self.loaded_corpora,
                'data_available': corpus_name in self.corpora_data
            }
        return corpus_info