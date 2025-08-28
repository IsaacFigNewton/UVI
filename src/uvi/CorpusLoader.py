"""
CorpusLoader Class

A standalone class for loading, parsing, and organizing all corpus data
from file sources (VerbNet, FrameNet, PropBank, OntoNotes, WordNet, BSO, 
SemNet, Reference Docs, VN API) with cross-corpus integration.

This class implements comprehensive file-based corpus loading with proper
error handling, schema validation, and cross-corpus reference building.
"""

import xml.etree.ElementTree as ET
import json
import csv
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime
import logging


class CorpusLoader:
    """
    A standalone class for loading, parsing, and organizing all corpus data
    from file sources (VerbNet, FrameNet, PropBank, OntoNotes, WordNet, BSO, 
    SemNet, Reference Docs, VN API) with cross-corpus integration.
    """
    
    def __init__(self, corpora_path: str = 'corpora/'):
        """
        Initialize CorpusLoader with corpus file paths.
        
        Args:
            corpora_path (str): Path to the corpora directory
        """
        self.corpora_path = Path(corpora_path)
        self.loaded_data = {}
        self.corpus_paths = {}
        self.load_status = {}
        self.build_metadata = {}
        self.reference_collections = {}
        self.cross_references = {}
        self.bso_mappings = {}
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Supported corpora with their expected directory names
        self.corpus_mappings = {
            'verbnet': ['verbnet', 'vn', 'verbnet3.4'],
            'framenet': ['framenet', 'fn', 'framenet1.7'],
            'propbank': ['propbank', 'pb', 'propbank3.4'],
            'ontonotes': ['ontonotes', 'on', 'ontonotes5.0'],
            'wordnet': ['wordnet', 'wn', 'wordnet3.1'],
            'bso': ['BSO', 'bso', 'basic_semantic_ontology'],
            'semnet': ['semnet20180205', 'semnet', 'semantic_network'],
            'reference_docs': ['reference_docs', 'ref_docs', 'docs'],
            'vn_api': ['vn_api', 'verbnet_api', 'vn']
        }
        
        # Auto-detect corpus paths
        self._detect_corpus_paths()
    
    def _detect_corpus_paths(self) -> None:
        """
        Automatically detect corpus paths from the base directory.
        """
        if not self.corpora_path.exists():
            self.logger.warning(f"Corpora directory not found: {self.corpora_path}")
            return
        
        for corpus_name, possible_dirs in self.corpus_mappings.items():
            corpus_path = None
            for dir_name in possible_dirs:
                candidate_path = self.corpora_path / dir_name
                if candidate_path.exists() and candidate_path.is_dir():
                    corpus_path = candidate_path
                    break
            
            if corpus_path:
                self.corpus_paths[corpus_name] = corpus_path
                self.logger.info(f"Found {corpus_name} corpus at: {corpus_path}")
            else:
                self.logger.warning(f"Corpus {corpus_name} not found in {self.corpora_path}")
    
    def get_corpus_paths(self) -> Dict[str, str]:
        """
        Get automatically detected corpus paths.
        
        Returns:
            dict: Paths to all detected corpus directories and files
        """
        return {name: str(path) for name, path in self.corpus_paths.items()}
    
    def load_all_corpora(self) -> Dict[str, Any]:
        """
        Load and parse all available corpus files.
        
        Returns:
            dict: Loading status and statistics for each corpus
        """
        self.logger.info("Starting to load all available corpora...")
        
        loading_results = {}
        
        for corpus_name in self.corpus_mappings.keys():
            if corpus_name in self.corpus_paths:
                try:
                    start_time = datetime.now()
                    result = self.load_corpus(corpus_name)
                    end_time = datetime.now()
                    
                    loading_results[corpus_name] = {
                        'status': 'success',
                        'load_time': (end_time - start_time).total_seconds(),
                        'data_keys': list(result.keys()) if isinstance(result, dict) else [],
                        'timestamp': start_time.isoformat()
                    }
                    self.logger.info(f"Successfully loaded {corpus_name}")
                    
                except Exception as e:
                    loading_results[corpus_name] = {
                        'status': 'error',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    self.logger.error(f"Failed to load {corpus_name}: {e}")
            else:
                loading_results[corpus_name] = {
                    'status': 'not_found',
                    'timestamp': datetime.now().isoformat()
                }
        
        # Build reference collections after loading
        self.build_reference_collections()
        
        return loading_results
    
    def load_corpus(self, corpus_name: str) -> Dict[str, Any]:
        """
        Load a specific corpus by name.
        
        Args:
            corpus_name (str): Name of corpus to load ('verbnet', 'framenet', etc.)
            
        Returns:
            dict: Parsed corpus data with metadata
        """
        if corpus_name not in self.corpus_paths:
            raise FileNotFoundError(f"Corpus {corpus_name} not found in configured paths")
        
        corpus_path = self.corpus_paths[corpus_name]
        
        # Route to appropriate parser
        if corpus_name == 'verbnet':
            data = self.parse_verbnet_files()
        elif corpus_name == 'framenet':
            data = self.parse_framenet_files()
        elif corpus_name == 'propbank':
            data = self.parse_propbank_files()
        elif corpus_name == 'ontonotes':
            data = self.parse_ontonotes_files()
        elif corpus_name == 'wordnet':
            data = self.parse_wordnet_files()
        elif corpus_name == 'bso':
            data = self.parse_bso_mappings()
        elif corpus_name == 'semnet':
            data = self.parse_semnet_data()
        elif corpus_name == 'reference_docs':
            data = self.parse_reference_docs()
        elif corpus_name == 'vn_api':
            data = self.parse_vn_api_files()
        else:
            raise ValueError(f"Unsupported corpus type: {corpus_name}")
        
        self.loaded_data[corpus_name] = data
        self.load_status[corpus_name] = {
            'loaded': True,
            'timestamp': datetime.now().isoformat(),
            'path': str(corpus_path)
        }
        
        return data
    
    def parse_verbnet_files(self) -> Dict[str, Any]:
        """
        Parse all VerbNet XML files and build internal data structures.
        
        Returns:
            dict: Parsed VerbNet data with hierarchy and cross-references
        """
        if 'verbnet' not in self.corpus_paths:
            raise FileNotFoundError("VerbNet corpus path not configured")
        
        verbnet_path = self.corpus_paths['verbnet']
        verbnet_data = {
            'classes': {},
            'hierarchy': {},
            'members': {},
            'statistics': {}
        }
        
        # Find all VerbNet XML files
        xml_files = list(verbnet_path.glob('*.xml'))
        if not xml_files:
            xml_files = list(verbnet_path.glob('**/*.xml'))
        
        xml_files = [f for f in xml_files if not f.name.startswith('.')]
        
        self.logger.info(f"Found {len(xml_files)} VerbNet XML files to process")
        
        parsed_count = 0
        error_count = 0
        
        for xml_file in xml_files:
            try:
                class_data = self._parse_verbnet_class(xml_file)
                if class_data and 'id' in class_data:
                    verbnet_data['classes'][class_data['id']] = class_data
                    
                    # Build member index
                    for member in class_data.get('members', []):
                        member_name = member.get('name', '')
                        if member_name:
                            if member_name not in verbnet_data['members']:
                                verbnet_data['members'][member_name] = []
                            verbnet_data['members'][member_name].append(class_data['id'])
                    
                    parsed_count += 1
                
            except Exception as e:
                error_count += 1
                self.logger.error(f"Error parsing VerbNet file {xml_file}: {e}")
        
        # Build class hierarchy
        verbnet_data['hierarchy'] = self._build_verbnet_hierarchy(verbnet_data['classes'])
        
        verbnet_data['statistics'] = {
            'total_files': len(xml_files),
            'parsed_files': parsed_count,
            'error_files': error_count,
            'total_classes': len(verbnet_data['classes']),
            'total_members': len(verbnet_data['members'])
        }
        
        self.logger.info(f"VerbNet parsing complete: {parsed_count} classes loaded")
        
        return verbnet_data
    
    def _parse_verbnet_class(self, xml_file_path: Path) -> Dict[str, Any]:
        """
        Parse a VerbNet class XML file.
        
        Args:
            xml_file_path (Path): Path to VerbNet XML file
            
        Returns:
            dict: Parsed VerbNet class data
        """
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            if root.tag != 'VNCLASS':
                return {}
            
            class_data = {
                'id': root.get('ID', ''),
                'members': [],
                'themroles': [],
                'frames': [],
                'subclasses': [],
                'source_file': str(xml_file_path)
            }
            
            # Extract members
            for member in root.findall('.//MEMBER'):
                member_data = {
                    'name': member.get('name', ''),
                    'wn': member.get('wn', ''),
                    'grouping': member.get('grouping', '')
                }
                class_data['members'].append(member_data)
            
            # Extract thematic roles
            for themrole in root.findall('.//THEMROLE'):
                role_data = {
                    'type': themrole.get('type', ''),
                    'selrestrs': []
                }
                
                # Extract selectional restrictions
                for selrestr in themrole.findall('.//SELRESTR'):
                    selrestr_data = {
                        'Value': selrestr.get('Value', ''),
                        'type': selrestr.get('type', '')
                    }
                    role_data['selrestrs'].append(selrestr_data)
                
                class_data['themroles'].append(role_data)
            
            # Extract frames
            for frame in root.findall('.//FRAME'):
                frame_data = {
                    'description': self._extract_frame_description(frame),
                    'examples': [],
                    'syntax': [],
                    'semantics': []
                }
                
                # Extract examples
                for example in frame.findall('.//EXAMPLE'):
                    if example.text:
                        frame_data['examples'].append(example.text.strip())
                
                # Extract syntax
                syntax_elements = frame.findall('.//SYNTAX')
                for syntax in syntax_elements:
                    syntax_data = []
                    for element in syntax:
                        if element.tag == 'NP':
                            np_data = {
                                'type': 'NP',
                                'value': element.get('value', ''),
                                'synrestrs': []
                            }
                            for synrestr in element.findall('.//SYNRESTR'):
                                synrestr_data = {
                                    'Value': synrestr.get('Value', ''),
                                    'type': synrestr.get('type', '')
                                }
                                np_data['synrestrs'].append(synrestr_data)
                            syntax_data.append(np_data)
                        elif element.tag == 'VERB':
                            verb_data = {
                                'type': 'VERB'
                            }
                            syntax_data.append(verb_data)
                        elif element.tag in ['PREP', 'ADV', 'ADJ']:
                            element_data = {
                                'type': element.tag,
                                'value': element.get('value', '')
                            }
                            syntax_data.append(element_data)
                    
                    frame_data['syntax'].append(syntax_data)
                
                # Extract semantics
                semantics_elements = frame.findall('.//SEMANTICS')
                for semantics in semantics_elements:
                    semantics_data = []
                    for pred in semantics.findall('.//PRED'):
                        pred_data = {
                            'value': pred.get('value', ''),
                            'args': []
                        }
                        for arg in pred.findall('.//ARG'):
                            arg_data = {
                                'type': arg.get('type', ''),
                                'value': arg.get('value', '')
                            }
                            pred_data['args'].append(arg_data)
                        semantics_data.append(pred_data)
                    
                    frame_data['semantics'].append(semantics_data)
                
                class_data['frames'].append(frame_data)
            
            # Extract subclasses recursively
            for subclass in root.findall('.//VNSUBCLASS'):
                subclass_data = self._parse_verbnet_subclass(subclass)
                if subclass_data:
                    class_data['subclasses'].append(subclass_data)
            
            return class_data
            
        except Exception as e:
            self.logger.error(f"Error parsing VerbNet class file {xml_file_path}: {e}")
            return {}
    
    def _parse_verbnet_subclass(self, subclass_element: ET.Element) -> Dict[str, Any]:
        """
        Parse a VerbNet subclass element recursively.
        
        Args:
            subclass_element (ET.Element): VerbNet subclass XML element
            
        Returns:
            dict: Parsed subclass data
        """
        subclass_data = {
            'id': subclass_element.get('ID', ''),
            'members': [],
            'themroles': [],
            'frames': [],
            'subclasses': []
        }
        
        # Extract members
        for member in subclass_element.findall('MEMBERS/MEMBER'):
            member_data = {
                'name': member.get('name', ''),
                'wn': member.get('wn', ''),
                'grouping': member.get('grouping', '')
            }
            subclass_data['members'].append(member_data)
        
        # Extract frames
        for frame in subclass_element.findall('FRAMES/FRAME'):
            frame_data = {
                'description': self._extract_frame_description(frame),
                'examples': [],
                'syntax': [],
                'semantics': []
            }
            
            # Extract examples
            for example in frame.findall('.//EXAMPLE'):
                if example.text:
                    frame_data['examples'].append(example.text.strip())
            
            subclass_data['frames'].append(frame_data)
        
        # Recursively extract nested subclasses
        for nested_subclass in subclass_element.findall('SUBCLASSES/VNSUBCLASS'):
            nested_data = self._parse_verbnet_subclass(nested_subclass)
            if nested_data:
                subclass_data['subclasses'].append(nested_data)
        
        return subclass_data
    
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
    
    def _build_verbnet_hierarchy(self, classes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build VerbNet class hierarchy from parsed classes.
        
        Args:
            classes (dict): Dictionary of parsed VerbNet classes
            
        Returns:
            dict: Hierarchical organization of classes
        """
        hierarchy = {
            'by_name': {},
            'by_id': {},
            'parent_child': {}
        }
        
        # Group by first letter for name-based hierarchy
        for class_id, class_data in classes.items():
            if class_id:
                first_char = class_id[0].upper()
                if first_char not in hierarchy['by_name']:
                    hierarchy['by_name'][first_char] = []
                hierarchy['by_name'][first_char].append(class_id)
        
        # Group by numeric prefix for ID-based hierarchy
        for class_id in classes.keys():
            if class_id:
                # Extract numeric prefix (e.g., "10.1" from "accept-10.1")
                match = re.search(r'(\d+)', class_id)
                if match:
                    prefix = match.group(1)
                    if prefix not in hierarchy['by_id']:
                        hierarchy['by_id'][prefix] = []
                    hierarchy['by_id'][prefix].append(class_id)
        
        # Build parent-child relationships
        for class_id in classes.keys():
            if class_id and '-' in class_id:
                parts = class_id.split('-')
                if len(parts) > 1:
                    # Find potential parent (e.g., "accept-77" is parent of "accept-77.1")
                    base_id = parts[0]
                    numeric_part = parts[1]
                    if '.' in numeric_part:
                        parent_numeric = numeric_part.split('.')[0]
                        potential_parent = f"{base_id}-{parent_numeric}"
                        if potential_parent in classes:
                            if potential_parent not in hierarchy['parent_child']:
                                hierarchy['parent_child'][potential_parent] = []
                            hierarchy['parent_child'][potential_parent].append(class_id)
        
        return hierarchy
    
    def parse_framenet_files(self) -> Dict[str, Any]:
        """
        Parse FrameNet XML files (frames, lexical units, full-text).
        
        Returns:
            dict: Parsed FrameNet data with frame relationships
        """
        if 'framenet' not in self.corpus_paths:
            raise FileNotFoundError("FrameNet corpus path not configured")
        
        framenet_path = self.corpus_paths['framenet']
        framenet_data = {
            'frames': {},
            'lexical_units': {},
            'frame_relations': {},
            'statistics': {}
        }
        
        # Parse frame index
        frame_index_path = framenet_path / 'frameIndex.xml'
        if frame_index_path.exists():
            framenet_data['frame_index'] = self._parse_framenet_frame_index(frame_index_path)
        
        # Parse individual frame files
        frame_dir = framenet_path / 'frame'
        if frame_dir.exists():
            frame_files = list(frame_dir.glob('*.xml'))
            
            parsed_count = 0
            for frame_file in frame_files:
                try:
                    frame_data = self._parse_framenet_frame(frame_file)
                    if frame_data and 'name' in frame_data:
                        framenet_data['frames'][frame_data['name']] = frame_data
                        parsed_count += 1
                except Exception as e:
                    self.logger.error(f"Error parsing FrameNet frame {frame_file}: {e}")
            
            framenet_data['statistics']['frames_parsed'] = parsed_count
        
        # Parse lexical unit index
        lu_index_path = framenet_path / 'luIndex.xml'
        if lu_index_path.exists():
            framenet_data['lu_index'] = self._parse_framenet_lu_index(lu_index_path)
        
        # Parse frame relations
        fr_relation_path = framenet_path / 'frRelation.xml'
        if fr_relation_path.exists():
            framenet_data['frame_relations'] = self._parse_framenet_relations(fr_relation_path)
        
        self.logger.info(f"FrameNet parsing complete: {len(framenet_data['frames'])} frames loaded")
        
        return framenet_data
    
    def _parse_framenet_frame_index(self, index_path: Path) -> Dict[str, Any]:
        """
        Parse FrameNet frame index file.
        
        Args:
            index_path (Path): Path to frameIndex.xml
            
        Returns:
            dict: Parsed frame index data
        """
        try:
            tree = ET.parse(index_path)
            root = tree.getroot()
            
            frame_index = {}
            for frame in root.findall('.//frame'):
                frame_id = frame.get('ID')
                frame_name = frame.get('name')
                if frame_id and frame_name:
                    frame_index[frame_name] = {
                        'id': frame_id,
                        'name': frame_name,
                        'cdate': frame.get('cDate'),
                        'file': f"{frame_name}.xml"
                    }
            
            return frame_index
            
        except Exception as e:
            self.logger.error(f"Error parsing FrameNet frame index: {e}")
            return {}
    
    def _parse_framenet_frame(self, frame_file: Path) -> Dict[str, Any]:
        """
        Parse a FrameNet frame XML file.
        
        Args:
            frame_file (Path): Path to FrameNet frame XML file
            
        Returns:
            dict: Parsed FrameNet frame data
        """
        try:
            tree = ET.parse(frame_file)
            root = tree.getroot()
            
            frame_data = {
                'name': root.get('name', ''),
                'id': root.get('ID', ''),
                'definition': '',
                'frame_elements': {},
                'lexical_units': {},
                'frame_relations': [],
                'source_file': str(frame_file)
            }
            
            # Extract definition
            definition_elem = root.find('.//definition')
            if definition_elem is not None and definition_elem.text:
                frame_data['definition'] = definition_elem.text.strip()
            
            # Extract frame elements
            for fe in root.findall('.//FE'):
                fe_name = fe.get('name', '')
                if fe_name:
                    fe_data = {
                        'name': fe_name,
                        'id': fe.get('ID', ''),
                        'coreType': fe.get('coreType', ''),
                        'definition': ''
                    }
                    
                    fe_def = fe.find('.//definition')
                    if fe_def is not None and fe_def.text:
                        fe_data['definition'] = fe_def.text.strip()
                    
                    frame_data['frame_elements'][fe_name] = fe_data
            
            # Extract lexical units
            for lu in root.findall('.//lexUnit'):
                lu_name = lu.get('name', '')
                if lu_name:
                    lu_data = {
                        'name': lu_name,
                        'id': lu.get('ID', ''),
                        'pos': lu.get('POS', ''),
                        'lemmaID': lu.get('lemmaID', ''),
                        'definition': ''
                    }
                    
                    lu_def = lu.find('.//definition')
                    if lu_def is not None and lu_def.text:
                        lu_data['definition'] = lu_def.text.strip()
                    
                    frame_data['lexical_units'][lu_name] = lu_data
            
            return frame_data
            
        except Exception as e:
            self.logger.error(f"Error parsing FrameNet frame file {frame_file}: {e}")
            return {}
    
    def _parse_framenet_lu_index(self, index_path: Path) -> Dict[str, Any]:
        """
        Parse FrameNet lexical unit index.
        
        Args:
            index_path (Path): Path to luIndex.xml
            
        Returns:
            dict: Parsed lexical unit index
        """
        try:
            tree = ET.parse(index_path)
            root = tree.getroot()
            
            lu_index = {}
            for lu in root.findall('.//lu'):
                lu_name = lu.get('name')
                if lu_name:
                    lu_index[lu_name] = {
                        'id': lu.get('ID'),
                        'name': lu_name,
                        'pos': lu.get('POS'),
                        'frame': lu.get('frame')
                    }
            
            return lu_index
            
        except Exception as e:
            self.logger.error(f"Error parsing FrameNet LU index: {e}")
            return {}
    
    def _parse_framenet_relations(self, relations_path: Path) -> Dict[str, Any]:
        """
        Parse FrameNet frame relations file.
        
        Args:
            relations_path (Path): Path to frRelation.xml
            
        Returns:
            dict: Parsed frame relations data
        """
        try:
            tree = ET.parse(relations_path)
            root = tree.getroot()
            
            relations_data = {
                'frame_relations': [],
                'fe_relations': []
            }
            
            # Parse frame-to-frame relations
            for relation in root.findall('.//frameRelation'):
                relation_data = {
                    'type': relation.get('type'),
                    'superFrame': relation.get('superFrame'),
                    'subFrame': relation.get('subFrame')
                }
                relations_data['frame_relations'].append(relation_data)
            
            # Parse frame element relations
            for fe_relation in root.findall('.//feRelation'):
                fe_relation_data = {
                    'type': fe_relation.get('type'),
                    'superFE': fe_relation.get('superFE'),
                    'subFE': fe_relation.get('subFE'),
                    'frameRelation': fe_relation.get('frameRelation')
                }
                relations_data['fe_relations'].append(fe_relation_data)
            
            return relations_data
            
        except Exception as e:
            self.logger.error(f"Error parsing FrameNet relations: {e}")
            return {}
    
    def parse_propbank_files(self) -> Dict[str, Any]:
        """
        Parse PropBank XML files and extract predicate structures.
        
        Returns:
            dict: Parsed PropBank data with role mappings
        """
        if 'propbank' not in self.corpus_paths:
            raise FileNotFoundError("PropBank corpus path not configured")
        
        propbank_path = self.corpus_paths['propbank']
        propbank_data = {
            'predicates': {},
            'rolesets': {},
            'statistics': {}
        }
        
        # Find PropBank frame files
        frame_files = []
        for pattern in ['*.xml', 'frames/*.xml', '**/frames/*.xml']:
            frame_files.extend(list(propbank_path.glob(pattern)))
        
        # Filter out non-frame files
        frame_files = [f for f in frame_files if 'frames' in str(f) or '-v.xml' in f.name]
        
        parsed_count = 0
        for frame_file in frame_files:
            try:
                predicate_data = self._parse_propbank_frame(frame_file)
                if predicate_data and 'lemma' in predicate_data:
                    propbank_data['predicates'][predicate_data['lemma']] = predicate_data
                    
                    # Index rolesets
                    for roleset in predicate_data.get('rolesets', []):
                        if 'id' in roleset:
                            propbank_data['rolesets'][roleset['id']] = roleset
                    
                    parsed_count += 1
                    
            except Exception as e:
                self.logger.error(f"Error parsing PropBank frame {frame_file}: {e}")
        
        propbank_data['statistics'] = {
            'files_processed': len(frame_files),
            'predicates_parsed': parsed_count,
            'total_rolesets': len(propbank_data['rolesets'])
        }
        
        self.logger.info(f"PropBank parsing complete: {parsed_count} predicates loaded")
        
        return propbank_data
    
    def _parse_propbank_frame(self, frame_file: Path) -> Dict[str, Any]:
        """
        Parse a PropBank frame XML file.
        
        Args:
            frame_file (Path): Path to PropBank XML file
            
        Returns:
            dict: Parsed PropBank frame data
        """
        try:
            tree = ET.parse(frame_file)
            root = tree.getroot()
            
            predicate_data = {
                'lemma': root.get('lemma', ''),
                'rolesets': [],
                'source_file': str(frame_file)
            }
            
            # Extract rolesets
            for roleset in root.findall('.//roleset'):
                roleset_data = {
                    'id': roleset.get('id', ''),
                    'name': roleset.get('name', ''),
                    'vncls': roleset.get('vncls', ''),
                    'roles': [],
                    'examples': []
                }
                
                # Extract roles
                for role in roleset.findall('.//role'):
                    role_data = {
                        'n': role.get('n', ''),
                        'descr': role.get('descr', ''),
                        'f': role.get('f', ''),
                        'vnrole': role.get('vnrole', '')
                    }
                    roleset_data['roles'].append(role_data)
                
                # Extract examples
                for example in roleset.findall('.//example'):
                    example_data = {
                        'name': example.get('name', ''),
                        'src': example.get('src', ''),
                        'text': '',
                        'args': []
                    }
                    
                    # Extract text
                    text_elem = example.find('text')
                    if text_elem is not None and text_elem.text:
                        example_data['text'] = text_elem.text.strip()
                    
                    # Extract arguments
                    for arg in example.findall('.//arg'):
                        arg_data = {
                            'n': arg.get('n', ''),
                            'f': arg.get('f', ''),
                            'text': arg.text if arg.text else ''
                        }
                        example_data['args'].append(arg_data)
                    
                    roleset_data['examples'].append(example_data)
                
                predicate_data['rolesets'].append(roleset_data)
            
            return predicate_data
            
        except Exception as e:
            self.logger.error(f"Error parsing PropBank frame file {frame_file}: {e}")
            return {}
    
    def parse_ontonotes_files(self) -> Dict[str, Any]:
        """
        Parse OntoNotes XML sense inventory files.
        
        Returns:
            dict: Parsed OntoNotes data with cross-resource mappings
        """
        if 'ontonotes' not in self.corpus_paths:
            raise FileNotFoundError("OntoNotes corpus path not configured")
        
        ontonotes_path = self.corpus_paths['ontonotes']
        ontonotes_data = {
            'sense_inventories': {},
            'statistics': {}
        }
        
        # Find OntoNotes sense files
        sense_files = []
        for pattern in ['*.xml', '**/*.xml', 'sense-inventories/*.xml']:
            sense_files.extend(list(ontonotes_path.glob(pattern)))
        
        parsed_count = 0
        for sense_file in sense_files:
            try:
                sense_data = self._parse_ontonotes_data(sense_file)
                if sense_data and 'lemma' in sense_data:
                    ontonotes_data['sense_inventories'][sense_data['lemma']] = sense_data
                    parsed_count += 1
                    
            except Exception as e:
                self.logger.error(f"Error parsing OntoNotes file {sense_file}: {e}")
        
        ontonotes_data['statistics'] = {
            'files_processed': len(sense_files),
            'sense_inventories_parsed': parsed_count
        }
        
        self.logger.info(f"OntoNotes parsing complete: {parsed_count} sense inventories loaded")
        
        return ontonotes_data
    
    def _parse_ontonotes_data(self, sense_file: Path) -> Dict[str, Any]:
        """
        Parse OntoNotes sense inventory file.
        
        Args:
            sense_file (Path): Path to OntoNotes sense file
            
        Returns:
            dict: Parsed OntoNotes sense data
        """
        try:
            tree = ET.parse(sense_file)
            root = tree.getroot()
            
            sense_data = {
                'lemma': root.get('lemma', ''),
                'senses': [],
                'source_file': str(sense_file)
            }
            
            # Extract senses
            for sense in root.findall('.//sense'):
                sense_info = {
                    'n': sense.get('n', ''),
                    'name': sense.get('name', ''),
                    'group': sense.get('group', ''),
                    'commentary': '',
                    'examples': [],
                    'mappings': {}
                }
                
                # Extract commentary
                commentary = sense.find('commentary')
                if commentary is not None and commentary.text:
                    sense_info['commentary'] = commentary.text.strip()
                
                # Extract examples
                for example in sense.findall('.//example'):
                    if example.text:
                        sense_info['examples'].append(example.text.strip())
                
                # Extract mappings (WordNet, VerbNet, PropBank, etc.)
                mappings_elem = sense.find('mappings')
                if mappings_elem is not None:
                    for mapping in mappings_elem:
                        mapping_type = mapping.tag
                        mapping_value = mapping.get('version', mapping.text)
                        sense_info['mappings'][mapping_type] = mapping_value
                
                sense_data['senses'].append(sense_info)
            
            return sense_data
            
        except Exception as e:
            self.logger.error(f"Error parsing OntoNotes sense file {sense_file}: {e}")
            return {}
    
    def parse_wordnet_files(self) -> Dict[str, Any]:
        """
        Parse WordNet data files, indices, and exception lists.
        
        Returns:
            dict: Parsed WordNet data with synset relationships
        """
        if 'wordnet' not in self.corpus_paths:
            raise FileNotFoundError("WordNet corpus path not configured")
        
        wordnet_path = self.corpus_paths['wordnet']
        wordnet_data = {
            'synsets': {},
            'index': {},
            'exceptions': {},
            'statistics': {}
        }
        
        # Parse data files (data.verb, data.noun, etc.)
        data_files = list(wordnet_path.glob('data.*'))
        for data_file in data_files:
            pos = data_file.name.split('.')[1]
            try:
                synsets = self._parse_wordnet_data_file(data_file)
                wordnet_data['synsets'][pos] = synsets
                self.logger.info(f"Parsed WordNet {pos} data: {len(synsets)} synsets")
            except Exception as e:
                self.logger.error(f"Error parsing WordNet data file {data_file}: {e}")
        
        # Parse index files (index.verb, index.noun, etc.)
        index_files = list(wordnet_path.glob('index.*'))
        for index_file in index_files:
            pos = index_file.name.split('.')[1]
            if pos != 'sense':  # Skip index.sense for now
                try:
                    index_data = self._parse_wordnet_index_file(index_file)
                    wordnet_data['index'][pos] = index_data
                    self.logger.info(f"Parsed WordNet {pos} index: {len(index_data)} entries")
                except Exception as e:
                    self.logger.error(f"Error parsing WordNet index file {index_file}: {e}")
        
        # Parse exception files (verb.exc, noun.exc, etc.)
        exc_files = list(wordnet_path.glob('*.exc'))
        for exc_file in exc_files:
            pos = exc_file.name.split('.')[0]
            try:
                exceptions = self._parse_wordnet_exception_file(exc_file)
                wordnet_data['exceptions'][pos] = exceptions
                self.logger.info(f"Parsed WordNet {pos} exceptions: {len(exceptions)} entries")
            except Exception as e:
                self.logger.error(f"Error parsing WordNet exception file {exc_file}: {e}")
        
        # Calculate statistics
        total_synsets = sum(len(synsets) for synsets in wordnet_data['synsets'].values())
        total_index_entries = sum(len(index) for index in wordnet_data['index'].values())
        
        wordnet_data['statistics'] = {
            'total_synsets': total_synsets,
            'total_index_entries': total_index_entries,
            'synsets_by_pos': {pos: len(synsets) for pos, synsets in wordnet_data['synsets'].items()},
            'index_by_pos': {pos: len(index) for pos, index in wordnet_data['index'].items()}
        }
        
        self.logger.info(f"WordNet parsing complete: {total_synsets} synsets, {total_index_entries} index entries")
        
        return wordnet_data
    
    def _parse_wordnet_data_file(self, data_file: Path) -> Dict[str, Any]:
        """
        Parse WordNet data file (e.g., data.verb).
        
        Args:
            data_file (Path): Path to WordNet data file
            
        Returns:
            dict: Parsed synset data
        """
        synsets = {}
        
        with open(data_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('  '):  # Skip copyright header
                    try:
                        parts = line.split('|')
                        if len(parts) >= 2:
                            synset_info = parts[0].strip().split()
                            if len(synset_info) >= 6:
                                synset_offset = synset_info[0]
                                lex_filenum = synset_info[1]
                                ss_type = synset_info[2]
                                w_cnt = int(synset_info[3], 16)
                                
                                synset_data = {
                                    'offset': synset_offset,
                                    'lex_filenum': lex_filenum,
                                    'ss_type': ss_type,
                                    'words': [],
                                    'pointers': [],
                                    'gloss': parts[1].strip() if len(parts) > 1 else ''
                                }
                                
                                # Parse words
                                word_start = 4
                                for i in range(w_cnt):
                                    if word_start + i*2 < len(synset_info):
                                        word = synset_info[word_start + i*2]
                                        lex_id = synset_info[word_start + i*2 + 1]
                                        synset_data['words'].append({
                                            'word': word,
                                            'lex_id': lex_id
                                        })
                                
                                synsets[synset_offset] = synset_data
                                
                    except (ValueError, IndexError) as e:
                        self.logger.debug(f"Skipping malformed line in {data_file}: {e}")
        
        return synsets
    
    def _parse_wordnet_index_file(self, index_file: Path) -> Dict[str, Any]:
        """
        Parse WordNet index file (e.g., index.verb).
        
        Args:
            index_file (Path): Path to WordNet index file
            
        Returns:
            dict: Parsed index data
        """
        index_data = {}
        
        with open(index_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('  '):  # Skip copyright header
                    try:
                        parts = line.split()
                        if len(parts) >= 4:
                            lemma = parts[0]
                            pos = parts[1]
                            synset_cnt = int(parts[2])
                            p_cnt = int(parts[3])
                            
                            entry_data = {
                                'lemma': lemma,
                                'pos': pos,
                                'synset_cnt': synset_cnt,
                                'p_cnt': p_cnt,
                                'ptr_symbols': [],
                                'sense_cnt': 0,
                                'tagsense_cnt': 0,
                                'synset_offsets': []
                            }
                            
                            # Parse pointer symbols
                            for i in range(4, 4 + p_cnt):
                                if i < len(parts):
                                    entry_data['ptr_symbols'].append(parts[i])
                            
                            # Parse sense and tagsense counts
                            if 4 + p_cnt < len(parts):
                                entry_data['sense_cnt'] = int(parts[4 + p_cnt])
                            if 4 + p_cnt + 1 < len(parts):
                                entry_data['tagsense_cnt'] = int(parts[4 + p_cnt + 1])
                            
                            # Parse synset offsets
                            for i in range(4 + p_cnt + 2, len(parts)):
                                entry_data['synset_offsets'].append(parts[i])
                            
                            index_data[lemma] = entry_data
                            
                    except (ValueError, IndexError) as e:
                        self.logger.debug(f"Skipping malformed line in {index_file}: {e}")
        
        return index_data
    
    def _parse_wordnet_exception_file(self, exc_file: Path) -> Dict[str, List[str]]:
        """
        Parse WordNet exception file (e.g., verb.exc).
        
        Args:
            exc_file (Path): Path to WordNet exception file
            
        Returns:
            dict: Exception mappings
        """
        exceptions = {}
        
        with open(exc_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        inflected_form = parts[0]
                        base_forms = parts[1:]
                        exceptions[inflected_form] = base_forms
        
        return exceptions
    
    def parse_bso_mappings(self) -> Dict[str, Any]:
        """
        Parse BSO CSV mapping files.
        
        Returns:
            dict: BSO category mappings to VerbNet classes
        """
        if 'bso' not in self.corpus_paths:
            raise FileNotFoundError("BSO corpus path not configured")
        
        bso_path = self.corpus_paths['bso']
        bso_data = {
            'vn_to_bso': {},
            'bso_to_vn': {},
            'statistics': {}
        }
        
        # Find BSO mapping CSV files
        csv_files = list(bso_path.glob('*.csv'))
        
        for csv_file in csv_files:
            try:
                mappings = self.load_bso_mappings(csv_file)
                
                if 'VNBSOMapping' in csv_file.name:
                    # VerbNet to BSO mappings
                    for mapping in mappings:
                        vn_class = mapping.get('VN_Class', '')
                        bso_category = mapping.get('BSO_Category', '')
                        if vn_class and bso_category:
                            bso_data['vn_to_bso'][vn_class] = bso_category
                            
                            if bso_category not in bso_data['bso_to_vn']:
                                bso_data['bso_to_vn'][bso_category] = []
                            bso_data['bso_to_vn'][bso_category].append(vn_class)
                
                elif 'BSOVNMapping' in csv_file.name:
                    # BSO to VerbNet mappings (with members)
                    for mapping in mappings:
                        bso_category = mapping.get('BSO_Category', '')
                        vn_class = mapping.get('VN_Class', '')
                        members = mapping.get('Members', '')
                        
                        if bso_category and vn_class:
                            if bso_category not in bso_data['bso_to_vn']:
                                bso_data['bso_to_vn'][bso_category] = []
                            
                            class_info = {
                                'class': vn_class,
                                'members': [m.strip() for m in members.split(',') if m.strip()] if members else []
                            }
                            bso_data['bso_to_vn'][bso_category].append(class_info)
                
                self.logger.info(f"Parsed BSO mapping file: {csv_file.name}")
                
            except Exception as e:
                self.logger.error(f"Error parsing BSO mapping file {csv_file}: {e}")
        
        bso_data['statistics'] = {
            'vn_to_bso_mappings': len(bso_data['vn_to_bso']),
            'bso_categories': len(bso_data['bso_to_vn']),
            'files_processed': len(csv_files)
        }
        
        # Store for later use
        self.bso_mappings = bso_data
        
        self.logger.info(f"BSO parsing complete: {len(bso_data['bso_to_vn'])} BSO categories")
        
        return bso_data
    
    def load_bso_mappings(self, csv_path: Path) -> List[Dict[str, str]]:
        """
        Load BSO (Basic Semantic Ontology) mappings from CSV.
        
        Args:
            csv_path (Path): Path to BSO mapping CSV file
            
        Returns:
            list: BSO mappings by class ID
        """
        mappings = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    mappings.append(row)
            
        except Exception as e:
            self.logger.error(f"Error loading BSO mappings from {csv_path}: {e}")
        
        return mappings
    
    def apply_bso_mappings(self, verbnet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply BSO mappings to VerbNet data.
        
        Args:
            verbnet_data (dict): VerbNet class data
            
        Returns:
            dict: VerbNet data with BSO mappings applied
        """
        if not self.bso_mappings or 'classes' not in verbnet_data:
            return verbnet_data
        
        # Apply BSO categories to VerbNet classes
        for class_id, class_data in verbnet_data['classes'].items():
            if class_id in self.bso_mappings.get('vn_to_bso', {}):
                class_data['bso_category'] = self.bso_mappings['vn_to_bso'][class_id]
        
        return verbnet_data
    
    def parse_semnet_data(self) -> Dict[str, Any]:
        """
        Parse SemNet JSON files for integrated semantic networks.
        
        Returns:
            dict: Parsed SemNet data for verbs and nouns
        """
        if 'semnet' not in self.corpus_paths:
            raise FileNotFoundError("SemNet corpus path not configured")
        
        semnet_path = self.corpus_paths['semnet']
        semnet_data = {
            'verb_network': {},
            'noun_network': {},
            'statistics': {}
        }
        
        # Parse verb semantic network
        verb_semnet_path = semnet_path / 'verb-semnet.json'
        if verb_semnet_path.exists():
            try:
                with open(verb_semnet_path, 'r', encoding='utf-8') as f:
                    verb_data = json.load(f)
                    semnet_data['verb_network'] = verb_data
                    self.logger.info(f"Loaded verb semantic network: {len(verb_data)} entries")
            except Exception as e:
                self.logger.error(f"Error parsing verb SemNet data: {e}")
        
        # Parse noun semantic network
        noun_semnet_path = semnet_path / 'noun-semnet.json'
        if noun_semnet_path.exists():
            try:
                with open(noun_semnet_path, 'r', encoding='utf-8') as f:
                    noun_data = json.load(f)
                    semnet_data['noun_network'] = noun_data
                    self.logger.info(f"Loaded noun semantic network: {len(noun_data)} entries")
            except Exception as e:
                self.logger.error(f"Error parsing noun SemNet data: {e}")
        
        semnet_data['statistics'] = {
            'verb_entries': len(semnet_data['verb_network']),
            'noun_entries': len(semnet_data['noun_network'])
        }
        
        self.logger.info(f"SemNet parsing complete")
        
        return semnet_data
    
    def parse_reference_docs(self) -> Dict[str, Any]:
        """
        Parse reference documentation (JSON/TSV files).
        
        Returns:
            dict: Parsed reference definitions and constants
        """
        if 'reference_docs' not in self.corpus_paths:
            raise FileNotFoundError("Reference docs corpus path not configured")
        
        ref_path = self.corpus_paths['reference_docs']
        ref_data = {
            'predicates': {},
            'themroles': {},
            'constants': {},
            'verb_specific': {},
            'statistics': {}
        }
        
        # Parse predicate definitions
        pred_calc_path = ref_path / 'pred_calc_for_website_final.json'
        if pred_calc_path.exists():
            try:
                with open(pred_calc_path, 'r', encoding='utf-8') as f:
                    pred_data = json.load(f)
                    ref_data['predicates'] = pred_data
                    self.logger.info(f"Loaded predicate definitions: {len(pred_data)} entries")
            except Exception as e:
                self.logger.error(f"Error parsing predicate definitions: {e}")
        
        # Parse thematic role definitions
        themrole_path = ref_path / 'themrole_defs.json'
        if themrole_path.exists():
            try:
                with open(themrole_path, 'r', encoding='utf-8') as f:
                    themrole_data = json.load(f)
                    ref_data['themroles'] = themrole_data
                    self.logger.info(f"Loaded thematic role definitions: {len(themrole_data)} entries")
            except Exception as e:
                self.logger.error(f"Error parsing thematic role definitions: {e}")
        
        # Parse constants
        constants_path = ref_path / 'vn_constants.tsv'
        if constants_path.exists():
            try:
                constants = self._parse_tsv_file(constants_path)
                ref_data['constants'] = constants
                self.logger.info(f"Loaded constants: {len(constants)} entries")
            except Exception as e:
                self.logger.error(f"Error parsing constants: {e}")
        
        # Parse semantic predicates
        sem_pred_path = ref_path / 'vn_semantic_predicates.tsv'
        if sem_pred_path.exists():
            try:
                sem_predicates = self._parse_tsv_file(sem_pred_path)
                ref_data['semantic_predicates'] = sem_predicates
                self.logger.info(f"Loaded semantic predicates: {len(sem_predicates)} entries")
            except Exception as e:
                self.logger.error(f"Error parsing semantic predicates: {e}")
        
        # Parse verb-specific predicates
        vs_pred_path = ref_path / 'vn_verb_specific_predicates.tsv'
        if vs_pred_path.exists():
            try:
                vs_predicates = self._parse_tsv_file(vs_pred_path)
                ref_data['verb_specific'] = vs_predicates
                self.logger.info(f"Loaded verb-specific predicates: {len(vs_predicates)} entries")
            except Exception as e:
                self.logger.error(f"Error parsing verb-specific predicates: {e}")
        
        ref_data['statistics'] = {
            'predicates': len(ref_data.get('predicates', {})),
            'themroles': len(ref_data.get('themroles', {})),
            'constants': len(ref_data.get('constants', {})),
            'verb_specific': len(ref_data.get('verb_specific', {}))
        }
        
        self.logger.info(f"Reference docs parsing complete")
        
        return ref_data
    
    def _parse_tsv_file(self, tsv_path: Path) -> Dict[str, Any]:
        """
        Parse a TSV (Tab-Separated Values) file.
        
        Args:
            tsv_path (Path): Path to TSV file
            
        Returns:
            dict: Parsed TSV data
        """
        data = {}
        
        with open(tsv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for i, row in enumerate(reader):
                # Use first column as key, or row index if no clear key
                key = next(iter(row.values())) if row else str(i)
                data[key] = row
        
        return data
    
    def parse_vn_api_files(self) -> Dict[str, Any]:
        """
        Parse VN API enhanced XML files.
        
        Returns:
            dict: Parsed VN API data with enhanced features
        """
        if 'vn_api' not in self.corpus_paths:
            # VN API might be the same as VerbNet in some configurations
            if 'verbnet' in self.corpus_paths:
                self.logger.info("Using VerbNet path for VN API data")
                return self.parse_verbnet_files()
            else:
                raise FileNotFoundError("VN API corpus path not configured")
        
        vn_api_path = self.corpus_paths['vn_api']
        
        # For now, use same parser as VerbNet but with API enhancements
        # This could be extended to handle API-specific features
        api_data = self.parse_verbnet_files()
        
        # Add API-specific metadata
        api_data['api_version'] = '1.0'
        api_data['enhanced_features'] = True
        
        self.logger.info(f"VN API parsing complete")
        
        return api_data
    
    # Reference data building methods
    
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
    
    # Validation methods
    
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
        
        # Check for empty classes
        for class_id, class_data in classes.items():
            if not class_data.get('members'):
                warnings.append(f"Class {class_id} has no members")
            
            if not class_data.get('frames'):
                warnings.append(f"Class {class_id} has no frames")
            
            # Validate frame structure
            for i, frame in enumerate(class_data.get('frames', [])):
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
        
        # Check for predicates without rolesets
        for lemma, predicate_data in predicates.items():
            if not predicate_data.get('rolesets'):
                warnings.append(f"Predicate {lemma} has no rolesets")
            
            for roleset in predicate_data.get('rolesets', []):
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
    
    # Statistics methods
    
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
            name: len(collection) if isinstance(collection, (list, dict)) else 0
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
            'corpus_paths': self.get_corpus_paths(),
            'timestamp': datetime.now().isoformat()
        }