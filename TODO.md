# UVI Unified Corpus Package Development Plan

## Overview
This document outlines the development plan for a comprehensive standalone UVI (Unified Verb Index) package in `src/uvi/` that provides unified access to all nine linguistic corpora with cross-resource integration capabilities. The package leverages the shared semantic frameworks, universal interface patterns, and cross-corpus validation systems documented in `corpora/OVERVIEW.md`. 

**Important**: This package is designed as a standalone library and will NOT be integrated with the existing Flask web application. The `uvi_web/` directory and all web application files remain unchanged and independent.

## 1. API Documentation for UVI Class

### Class: `UVI`

```python
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
    
    def __init__(self, corpora_path='corpora/', load_all=True):
        """
        Initialize UVI with corpus file paths for standalone operation.
        
        Args:
            corpora_path (str): Path to the corpora directory containing all corpus files
            load_all (bool): Load all corpora on initialization
        """
```

### Core Methods

#### Universal Search and Query Methods

```python
def search_lemmas(self, lemmas, include_resources=None, logic='or', sort_behavior='alpha'):
    """
    Search for lemmas across all linguistic resources with cross-corpus integration.
    
    Args:
        lemmas (list): List of lemmas to search
        include_resources (list): Resources to include ['vn', 'fn', 'pb', 'on', 'wn', 'bso', 'semnet', 'ref', 'vn_api']
                                 If None, includes all available resources
        logic (str): 'and' or 'or' logic for multi-lemma search
        sort_behavior (str): 'alpha' or 'num' sorting
        
    Returns:
        dict: Comprehensive cross-resource results with mappings
    """

def search_by_semantic_pattern(self, pattern_type, pattern_value, target_resources=None):
    """
    Search across corpora using shared semantic patterns (thematic roles, predicates, etc.).
    
    Args:
        pattern_type (str): Type of pattern ('themrole', 'predicate', 'syntactic_frame', 
                           'selectional_restriction', 'semantic_type', 'frame_element')
        pattern_value (str): Pattern value to search
        target_resources (list): Resources to search in (default: all)
        
    Returns:
        dict: Cross-corpus matches with semantic relationships
    """

def search_by_cross_reference(self, source_id, source_corpus, target_corpus):
    """
    Navigate between corpora using cross-reference mappings.
    
    Args:
        source_id (str): Entry ID in source corpus
        source_corpus (str): Source corpus name
        target_corpus (str): Target corpus name
        
    Returns:
        list: Related entries in target corpus with mapping confidence
    """

def search_by_attribute(self, attribute_type, query_string, corpus_filter=None):
    """
    Search by specific linguistic attributes across multiple corpora.
    
    Args:
        attribute_type (str): Type of attribute ('themrole', 'predicate', 'vs_feature', 
                             'selrestr', 'synrestr', 'frame_element', 'semantic_type')
        query_string (str): Attribute value to search
        corpus_filter (list): Limit search to specific corpora
        
    Returns:
        dict: Matched entries grouped by corpus with cross-references
    """

def find_semantic_relationships(self, entry_id, corpus, relationship_types=None, depth=2):
    """
    Discover semantic relationships across the corpus collection.
    
    Args:
        entry_id (str): Starting entry ID
        corpus (str): Starting corpus
        relationship_types (list): Types of relationships to explore
        depth (int): Maximum relationship depth to explore
        
    Returns:
        dict: Semantic relationship graph with paths and distances
    """

#### Corpus-Specific Retrieval Methods

```python
def get_verbnet_class(self, class_id, include_subclasses=True, include_mappings=True):
    """
    Retrieve comprehensive VerbNet class information with cross-corpus integration.
    
    Args:
        class_id (str): VerbNet class identifier
        include_subclasses (bool): Include hierarchical subclass information
        include_mappings (bool): Include cross-corpus mappings
        
    Returns:
        dict: VerbNet class data with integrated cross-references
    """

def get_framenet_frame(self, frame_name, include_lexical_units=True, include_relations=True):
    """
    Retrieve comprehensive FrameNet frame information.
    
    Args:
        frame_name (str): FrameNet frame name
        include_lexical_units (bool): Include all lexical units
        include_relations (bool): Include frame-to-frame relations
        
    Returns:
        dict: FrameNet frame data with semantic relations
    """

def get_propbank_frame(self, lemma, include_examples=True, include_mappings=True):
    """
    Retrieve PropBank frame information with cross-corpus integration.
    
    Args:
        lemma (str): PropBank lemma
        include_examples (bool): Include annotated examples
        include_mappings (bool): Include VerbNet/FrameNet mappings
        
    Returns:
        dict: PropBank frame data with cross-references
    """

def get_ontonotes_entry(self, lemma, include_mappings=True):
    """
    Retrieve OntoNotes sense inventory with cross-resource mappings.
    
    Args:
        lemma (str): OntoNotes lemma
        include_mappings (bool): Include all cross-resource mappings
        
    Returns:
        dict: OntoNotes entry data with integrated references
    """

def get_wordnet_synsets(self, word, pos=None, include_relations=True):
    """
    Retrieve WordNet synset information with semantic relations.
    
    Args:
        word (str): Word to look up
        pos (str): Part of speech filter (optional)
        include_relations (bool): Include hypernyms, hyponyms, etc.
        
    Returns:
        list: WordNet synsets with relation hierarchies
    """

def get_bso_categories(self, verb_class=None, semantic_category=None):
    """
    Retrieve BSO broad semantic organization mappings.
    
    Args:
        verb_class (str): VerbNet class to get BSO categories for
        semantic_category (str): BSO category to get verb classes for
        
    Returns:
        dict: BSO mappings with member verb information
    """

def get_semnet_data(self, lemma, pos='verb'):
    """
    Retrieve SemNet integrated semantic network data.
    
    Args:
        lemma (str): Lemma to look up
        pos (str): Part of speech ('verb' or 'noun')
        
    Returns:
        dict: Integrated semantic network information
    """

def get_reference_definitions(self, reference_type, name=None):
    """
    Retrieve reference documentation (predicates, themroles, constants).
    
    Args:
        reference_type (str): Type of reference ('predicate', 'themrole', 'constant', 'verb_specific')
        name (str): Specific reference name (optional)
        
    Returns:
        dict: Reference definitions and usage information
    """
```

#### Cross-Corpus Integration Methods

```python
def get_complete_semantic_profile(self, lemma):
    """
    Get comprehensive semantic information from all loaded corpora.
    
    Args:
        lemma (str): Lemma to analyze
        
    Returns:
        dict: Integrated semantic profile across all resources
    """

def validate_cross_references(self, entry_id, source_corpus):
    """
    Validate cross-references between corpora for data integrity.
    
    Args:
        entry_id (str): Entry ID to validate
        source_corpus (str): Source corpus name
        
    Returns:
        dict: Validation results for all cross-references
    """

def find_related_entries(self, entry_id, source_corpus, target_corpus):
    """
    Find related entries in target corpus using cross-reference mappings.
    
    Args:
        entry_id (str): Source entry ID
        source_corpus (str): Source corpus name
        target_corpus (str): Target corpus name
        
    Returns:
        list: Related entries with mapping confidence scores
    """

def trace_semantic_path(self, start_entry, end_entry, max_depth=3):
    """
    Find semantic relationship path between entries across corpora.
    
    Args:
        start_entry (tuple): (corpus, entry_id) for starting point
        end_entry (tuple): (corpus, entry_id) for target
        max_depth (int): Maximum path length to explore
        
    Returns:
        list: Semantic relationship paths with confidence scores
    """

#### Reference Data Methods

```python
def get_references(self):
    """
    Get all reference data extracted from corpus files.
    
    Returns:
        dict: Contains gen_themroles, predicates, vs_features, syn_res, sel_res
    """

def get_themrole_references(self):
    """
    Get all thematic role references from corpora files.
    
    Returns:
        list: Sorted list of thematic roles with descriptions
    """

def get_predicate_references(self):
    """
    Get all predicate references from reference documentation.
    
    Returns:
        list: Sorted list of predicates with definitions and usage
    """

def get_verb_specific_features(self):
    """
    Get all verb-specific features from VerbNet corpus files.
    
    Returns:
        list: Sorted list of verb-specific features
    """

def get_syntactic_restrictions(self):
    """
    Get all syntactic restrictions from VerbNet corpus files.
    
    Returns:
        list: Sorted list of syntactic restrictions
    """

def get_selectional_restrictions(self):
    """
    Get all selectional restrictions from VerbNet corpus files.
    
    Returns:
        list: Sorted list of selectional restrictions
    """
```

#### Schema Validation Methods

```python
def validate_corpus_schemas(self, corpus_names=None):
    """
    Validate corpus files against their schemas (DTD/XSD/custom).
    
    Args:
        corpus_names (list): Corpora to validate (default: all loaded)
        
    Returns:
        dict: Validation results for each corpus
    """

def validate_xml_corpus(self, corpus_name):
    """
    Validate XML corpus files against DTD/XSD schemas.
    
    Args:
        corpus_name (str): Name of XML-based corpus to validate
        
    Returns:
        dict: Detailed validation results with error locations
    """

def check_data_integrity(self):
    """
    Check internal consistency and completeness of all loaded corpora.
    
    Returns:
        dict: Comprehensive data integrity report
    """
```

#### Data Export Methods

```python
def export_resources(self, include_resources=None, format='json', include_mappings=True):
    """
    Export selected linguistic resources in specified format.
    
    Args:
        include_resources (list): Resources to include ['vn', 'fn', 'pb', 'on', 'wn', 'bso', 'semnet', 'ref']
        format (str): Export format ('json', 'xml', 'csv')
        include_mappings (bool): Include cross-corpus mappings
        
    Returns:
        str: Exported data in specified format
    """

def export_cross_corpus_mappings(self):
    """
    Export comprehensive cross-corpus mapping data.
    
    Returns:
        dict: Complete mapping relationships between all corpora
    """

def export_semantic_profile(self, lemma, format='json'):
    """
    Export complete semantic profile for a lemma across all corpora.
    
    Args:
        lemma (str): Lemma to export profile for
        format (str): Export format
        
    Returns:
        str: Comprehensive semantic profile
    """
```

#### Class Hierarchy Methods

```python
def get_class_hierarchy_by_name(self):
    """
    Get VerbNet class hierarchy organized alphabetically.
    
    Returns:
        dict: Class hierarchy organized by first letter
    """

def get_class_hierarchy_by_id(self):
    """
    Get VerbNet class hierarchy organized by numerical ID.
    
    Returns:
        dict: Class hierarchy organized by numerical prefix
    """

def get_subclass_ids(self, parent_class_id):
    """
    Get subclass IDs for a parent VerbNet class.
    
    Args:
        parent_class_id (str): Parent class ID
        
    Returns:
        list: List of subclass IDs or None
    """

def get_full_class_hierarchy(self, class_id):
    """
    Get complete class hierarchy for a given class.
    
    Args:
        class_id (str): VerbNet class ID
        
    Returns:
        dict: Hierarchical structure of the class
    """
```

#### Utility Methods

```python
def get_top_parent_id(self, class_id):
    """
    Extract top-level parent ID from a class ID.
    
    Args:
        class_id (str): VerbNet class ID
        
    Returns:
        str: Top parent ID
    """

def get_member_classes(self, member_name):
    """
    Get all VerbNet classes containing a specific member.
    
    Args:
        member_name (str): Member verb name
        
    Returns:
        list: Sorted list of class IDs containing the member
    """
```

#### Field Information Methods

```python
def get_themrole_fields(self, class_id, frame_desc_primary, 
                        frame_desc_secondary, themrole_name):
    """
    Get detailed themrole field information.
    
    Args:
        class_id (str): VerbNet class ID
        frame_desc_primary (str): Primary frame description
        frame_desc_secondary (str): Secondary frame description
        themrole_name (str): Thematic role name
        
    Returns:
        dict: Themrole field details
    """

def get_predicate_fields(self, pred_name):
    """
    Get predicate field information.
    
    Args:
        pred_name (str): Predicate name
        
    Returns:
        dict: Predicate field details
    """

def get_constant_fields(self, constant_name):
    """
    Get constant field information.
    
    Args:
        constant_name (str): Constant name
        
    Returns:
        dict: Constant field details
    """

def get_verb_specific_fields(self, feature_name):
    """
    Get verb-specific field information.
    
    Args:
        feature_name (str): Feature name
        
    Returns:
        dict: Verb-specific field details
    """
```

## 2. File-Based Implementation Plan

### Phase 1: Create UVI Class Structure
1. **Create class initialization**
   - Set up corpus file path configuration
   - Initialize corpus data loaders for all 9 corpora
   - Create file system navigation methods
   - Load corpus schemas for validation

2. **Import necessary dependencies**
   - xml.etree.ElementTree for XML parsing
   - json for JSON corpus data
   - csv for CSV corpus data
   - lxml for XML schema validation
   - re for regex operations
   - pathlib for cross-platform file operations

### Phase 2: Create Corpus File Parsers
1. **XML-based corpus parsers**
   - VerbNet XML parser (classes, members, frames, semantics)
   - FrameNet XML parser (frames, lexical units, full-text annotations)
   - PropBank XML parser (predicates, rolesets, examples)
   - OntoNotes XML parser (sense inventories, mappings)
   - VN API XML parser (enhanced VerbNet with API features)

2. **JSON-based corpus parsers**
   - SemNet JSON parser (verb and noun semantic networks)
   - Reference documentation JSON parser (predicates, constants, definitions)

3. **CSV-based corpus parsers** 
   - BSO mapping CSV parser (VerbNet-BSO category mappings)

4. **Custom format parsers**
   - WordNet custom text format parser (data files, indices, exceptions)

### Phase 3: Implement Core Search Methods (File-Based)
1. **Convert existing query methods to file parsing**
   - `find_matching_ids` → `search_lemmas` (search across parsed corpus data)
   - `find_matching_elements` → internal file search helper
   - `get_subclass_ids` → parse VerbNet hierarchy from XML
   - `full_class_hierarchy_tree` → build from parsed VerbNet files

2. **Convert utility methods to file operations**
   - `top_parent_id` → extract from VerbNet file structures
   - `unique_id` → generate for file-based entries
   - Remove all external data dependency methods

3. **Convert sorting methods to file-based data**
   - `sort_by_char` → `get_class_hierarchy_by_name` (from parsed files)
   - `sort_by_id` → `get_class_hierarchy_by_id` (from parsed files)
   - `sort_key` → internal helper for file data

4. **Convert field retrieval to file parsing**
   - `get_themrole_fields` → extract from reference docs files
   - `get_pred_fields` → parse from reference documentation
   - `get_constant_fields` → extract from reference TSV files
   - `get_verb_specific_fields` → parse from VerbNet XML structures

### Phase 4: Implement Cross-Corpus Integration
1. **Build cross-reference mapping system**
   - Parse all cross-corpus mappings from files (WordNet keys, PropBank groupings, FrameNet mappings, etc.)
   - Create unified cross-reference index
   - Implement validation for mapping integrity

2. **Implement semantic relationship discovery**
   - Build semantic relationship graphs from parsed data
   - Create path-finding algorithms for cross-corpus navigation
   - Implement confidence scoring for relationships

3. **Add schema validation capabilities**
   - Load DTD/XSD schemas for XML corpora
   - Implement validation methods for all corpus types
   - Create data integrity checking

### Phase 5: Extract and Convert Web-Independent Logic
1. **Convert search logic to file-based operations**
   - Extract lemma search logic from Flask routes but make file-based
   - Convert attribute search to work with parsed corpus data
   - Remove all external data dependencies from search logic

2. **Convert reference data retrieval to file parsing**
   - Extract reference data logic but parse from corpus files
   - Create file-based methods for each reference type
   - Parse themroles, predicates, constants from reference docs

3. **Convert data export to file-based sources**
   - Export logic works with parsed file data from corpus files
   - Support multiple export formats (JSON, XML, CSV)
   - Include cross-corpus mappings in exports

4. **Convert VerbNet processing to file operations**
   - Parse class information directly from XML files
   - Build hierarchies from file system and XML structure
   - Eliminate any external data dependencies

## 3. Testing Strategy

### Unit Tests for UVI Class
1. Test file-based corpus loading and parsing for all 9 corpora
2. Test each search method with various parameters
3. Test data retrieval methods from parsed files
4. Test export functionality with file-based data
5. Test utility methods for file operations
6. Test schema validation against DTD/XSD files
7. Test cross-corpus reference resolution
8. Test error handling for missing or corrupt files
9. Test semantic relationship discovery across corpora

### Integration Tests
1. Test complete semantic profile generation across all 9 corpora
2. Test cross-corpus navigation and relationship discovery
3. Test file system monitoring and reloading capabilities
4. Test memory management with large corpus files

## 4. Migration Steps

### Step 1: Create UVI.py with basic structure
- Define class with __init__ method
- Set up corpus file path configuration and parsers for all 9 corpora

### Step 2: Migrate and adapt methods one category at a time
- Start with utility methods (least dependencies)
- Then reference data methods
- Then search methods
- Finally complex query methods

### Step 3: Create supporting classes
- Implement CorpusLoader for parsing all 9 corpus formats
- Create Presentation class for web-independent formatting
- Build CorpusMonitor for file system change detection

### Step 4: Validate and test
- Test file parsing against all corpus schemas
- Validate cross-corpus reference integrity
- Test standalone package functionality
- Create example usage scripts and documentation

## 5. Benefits of File-Based UVI Package

1. **Complete Independence**: No external dependencies - works entirely with corpus files
2. **Cross-Corpus Integration**: Unified access to all 9 linguistic corpora with semantic relationship discovery
3. **Schema Validation**: Built-in validation against DTD/XSD schemas for data integrity
4. **Reusability**: UVI package works in any Python environment (CLI, Jupyter, desktop apps, other web frameworks)
5. **Comprehensive Coverage**: Single interface to VerbNet, FrameNet, PropBank, OntoNotes, WordNet, BSO, SemNet, and reference documentation
6. **Testing**: Easy to unit test with file-based data sources
7. **Portability**: Self-contained package that can be distributed with corpus files
8. **Performance**: Direct file access eliminates external data access overhead
9. **Maintainability**: Clear separation between corpus parsing logic and any specific application use

## 6. Considerations

1. **File System Management**: UVI class should handle file access and caching efficiently
2. **Error Handling**: Robust error handling for file parsing, schema validation, and missing files
3. **Memory Management**: Efficient loading and caching of large corpus files 
4. **Configuration**: Flexible corpus path configuration and format detection
5. **Documentation**: Comprehensive docstrings for all public methods with examples
6. **Type Hints**: Full type annotation support for better IDE integration
7. **Cross-Platform Compatibility**: Ensure file path handling works across operating systems
8. **Schema Compatibility**: Handle different versions of corpus formats gracefully
9. **Performance**: Lazy loading and indexing strategies for large corpora

## 7. Future Enhancements

1. **Advanced Caching**: Intelligent caching of parsed data with invalidation strategies
2. **Async Support**: Asynchronous file I/O for better performance with large corpora
3. **Query Optimization**: Optimize cross-corpus searches with indexing and caching
4. **Corpus Versioning**: Support for multiple versions of corpus formats
5. **Plugin Architecture**: Extensible system for adding new corpus types
6. **Export Formats**: Additional export formats (RDF, XML, custom schemas)
7. **Visualization**: Generate corpus relationship graphs and statistics
8. **CLI Interface**: Command-line tools for corpus analysis and validation
9. **Integration APIs**: Easy integration with NLP frameworks (spaCy, NLTK, etc.)

## 8. API Documentation for CorpusLoader Class

### Class: `CorpusLoader`

```python
class CorpusLoader:
    """
    A standalone class for loading, parsing, and organizing all corpus data
    from file sources (VerbNet, FrameNet, PropBank, OntoNotes, WordNet, BSO, 
    SemNet, Reference Docs, VN API) with cross-corpus integration.
    """
    
    def __init__(self, corpora_path='corpora/'):
        """
        Initialize CorpusLoader with corpus file paths.
        
        Args:
            corpora_path (str): Path to the corpora directory
        """
```

### Corpus Loading Methods

```python
def load_all_corpora(self):
    """
    Load and parse all available corpus files.
    
    Returns:
        dict: Loading status and statistics for each corpus
    """

def load_corpus(self, corpus_name):
    """
    Load a specific corpus by name.
    
    Args:
        corpus_name (str): Name of corpus to load ('verbnet', 'framenet', etc.)
        
    Returns:
        dict: Parsed corpus data with metadata
    """

def get_corpus_paths(self):
    """
    Get automatically detected corpus paths.
    
    Returns:
        dict: Paths to all detected corpus directories and files
    """
```

### Parsing Methods

```python
def parse_verbnet_files(self):
    """
    Parse all VerbNet XML files and build internal data structures.
    
    Returns:
        dict: Parsed VerbNet data with hierarchy and cross-references
    """

def parse_framenet_files(self):
    """
    Parse FrameNet XML files (frames, lexical units, full-text).
    
    Returns:
        dict: Parsed FrameNet data with frame relationships
    """

def parse_propbank_files(self):
    """
    Parse PropBank XML files and extract predicate structures.
    
    Returns:
        dict: Parsed PropBank data with role mappings
    """

def parse_ontonotes_files(self):
    """
    Parse OntoNotes XML sense inventory files.
    
    Returns:
        dict: Parsed OntoNotes data with cross-resource mappings
    """

def parse_wordnet_files(self):
    """
    Parse WordNet data files, indices, and exception lists.
    
    Returns:
        dict: Parsed WordNet data with synset relationships
    """

def parse_bso_mappings(self):
    """
    Parse BSO CSV mapping files.
    
    Returns:
        dict: BSO category mappings to VerbNet classes
    """

def parse_semnet_data(self):
    """
    Parse SemNet JSON files for integrated semantic networks.
    
    Returns:
        dict: Parsed SemNet data for verbs and nouns
    """

def parse_reference_docs(self):
    """
    Parse reference documentation (JSON/TSV files).
    
    Returns:
        dict: Parsed reference definitions and constants
    """
```

### Reference Data Methods

```python
def build_reference_collections(self):
    """
    Build all reference collections for VerbNet components.
    
    Returns:
        dict: Status of reference collection builds
    """

def build_predicate_definitions(self):
    """
    Build predicate definitions collection.
    
    Returns:
        bool: Success status
    """

def build_themrole_definitions(self):
    """
    Build thematic role definitions collection.
    
    Returns:
        bool: Success status
    """

def build_verb_specific_features(self):
    """
    Build verb-specific features collection.
    
    Returns:
        bool: Success status
    """

def build_syntactic_restrictions(self):
    """
    Build syntactic restrictions collection.
    
    Returns:
        bool: Success status
    """

def build_selectional_restrictions(self):
    """
    Build selectional restrictions collection.
    
    Returns:
        bool: Success status
    """
```

### Parser Methods (Internal)

```python
def _parse_verbnet_class(self, xml_file_path):
    """
    Parse a VerbNet class XML file.
    
    Args:
        xml_file_path (str): Path to VerbNet XML file
        
    Returns:
        dict: Parsed VerbNet class data
    """

def _parse_framenet_frame(self, xml_file_path):
    """
    Parse a FrameNet frame XML file.
    
    Args:
        xml_file_path (str): Path to FrameNet XML file
        
    Returns:
        dict: Parsed FrameNet frame data
    """

def _parse_propbank_frame(self, xml_file_path):
    """
    Parse a PropBank frame XML file.
    
    Args:
        xml_file_path (str): Path to PropBank XML file
        
    Returns:
        dict: Parsed PropBank frame data
    """

def _parse_ontonotes_data(self, html_content):
    """
    Parse OntoNotes HTML data.
    
    Args:
        html_content (str): HTML content from OntoNotes
        
    Returns:
        list: Parsed OntoNotes entries
    """
```

### BSO Integration Methods

```python
def load_bso_mappings(self, csv_path):
    """
    Load BSO (Basic Semantic Ontology) mappings from CSV.
    
    Args:
        csv_path (str): Path to BSO mapping CSV file
        
    Returns:
        dict: BSO mappings by class ID
    """

def apply_bso_mappings(self, verbnet_data):
    """
    Apply BSO mappings to VerbNet data.
    
    Args:
        verbnet_data (dict): VerbNet class data
        
    Returns:
        dict: VerbNet data with BSO mappings applied
    """
```

### Validation Methods

```python
def validate_collections(self):
    """
    Validate integrity of all collections.
    
    Returns:
        dict: Validation results for each collection
    """

def validate_cross_references(self):
    """
    Validate cross-references between collections.
    
    Returns:
        dict: Cross-reference validation results
    """
```

### Statistics Methods

```python
def get_collection_statistics(self):
    """
    Get statistics for all collections.
    
    Returns:
        dict: Statistics for each collection
    """

def get_build_metadata(self):
    """
    Get metadata about last build times and versions.
    
    Returns:
        dict: Build metadata
    """
```

## 9. API Documentation for Presentation Class

### Class: `Presentation`

```python
class Presentation:
    """
    A standalone class for presentation-layer formatting and HTML generation
    functions that are used in templates but not tied to Flask.
    """
    
    def __init__(self):
        """
        Initialize Presentation formatter.
        """
```

### HTML Generation Methods

```python
def generate_class_hierarchy_html(self, class_id, uvi_instance):
    """
    Generate HTML representation of class hierarchy.
    
    Args:
        class_id (str): VerbNet class ID
        uvi_instance: UVI instance for data access
        
    Returns:
        str: HTML string for class hierarchy
    """

def generate_sanitized_class_html(self, vn_class_id, uvi_instance):
    """
    Generate sanitized VerbNet class HTML.
    
    Args:
        vn_class_id (str): VerbNet class ID
        uvi_instance: UVI instance for data access
        
    Returns:
        str: Sanitized HTML representation
    """
```

### Formatting Methods

```python
def format_framenet_definition(self, frame, markup, popover=False):
    """
    Format FrameNet frame definition with HTML markup.
    
    Args:
        frame (dict): FrameNet frame data
        markup (str): Definition markup
        popover (bool): Include popover functionality
        
    Returns:
        str: Formatted HTML definition
    """

def format_propbank_example(self, example):
    """
    Format PropBank example with colored arguments.
    
    Args:
        example (dict): PropBank example data
        
    Returns:
        dict: Example with colored HTML markup
    """
```

### Field Display Methods

```python
def format_themrole_display(self, themrole_data):
    """
    Format thematic role for display.
    
    Args:
        themrole_data (dict): Thematic role data
        
    Returns:
        str: Formatted display string
    """

def format_predicate_display(self, predicate_data):
    """
    Format predicate for display.
    
    Args:
        predicate_data (dict): Predicate data
        
    Returns:
        str: Formatted display string
    """

def format_restriction_display(self, restriction_data, restriction_type):
    """
    Format selectional or syntactic restriction for display.
    
    Args:
        restriction_data (dict): Restriction data
        restriction_type (str): 'selectional' or 'syntactic'
        
    Returns:
        str: Formatted display string
    """
```

### Utility Display Methods

```python
def generate_unique_id(self):
    """
    Generate unique identifier for HTML elements.
    
    Returns:
        str: Unique 16-character hex string
    """

def json_to_display(self, elements):
    """
    Convert parsed corpus elements to display-ready JSON.
    
    Args:
        elements: Parsed corpus data list or dict
        
    Returns:
        str: JSON string for display
    """

def strip_object_ids(self, data):
    """
    Remove internal IDs and metadata from data for clean display.
    
    Args:
        data (dict/list): Data containing internal identifiers
        
    Returns:
        dict/list: Data without internal identifiers
    """
```

### Color Generation Methods

```python
def generate_element_colors(self, elements, seed=None):
    """
    Generate consistent colors for elements.
    
    Args:
        elements (list): List of elements needing colors
        seed: Seed for consistent color generation
        
    Returns:
        dict: Element to color mapping
    """
```

## 10. API Documentation for CorpusMonitor Class

### Class: `CorpusMonitor`

```python
class CorpusMonitor:
    """
    A standalone class for monitoring corpus directories and triggering
    rebuilds when files change.
    """
    
    def __init__(self, data_builder):
        """
        Initialize CorpusMonitor with CorpusLoader instance.
        
        Args:
            corpus_loader (CorpusLoader): Instance of CorpusLoader for rebuilds
        """
```

### Configuration Methods

```python
def set_watch_paths(self, verbnet_path=None, framenet_path=None,
                    propbank_path=None, reference_docs_path=None):
    """
    Set paths to monitor for changes.
    
    Args:
        verbnet_path (str): Path to VerbNet corpus
        framenet_path (str): Path to FrameNet corpus
        propbank_path (str): Path to PropBank corpus
        reference_docs_path (str): Path to reference documents
        
    Returns:
        dict: Configured watch paths
    """

def set_rebuild_strategy(self, strategy='immediate', batch_timeout=60):
    """
    Set rebuild strategy for detected changes.
    
    Args:
        strategy (str): 'immediate' or 'batch'
        batch_timeout (int): Seconds to wait before batch rebuild
        
    Returns:
        dict: Current strategy configuration
    """
```

### Monitoring Methods

```python
def start_monitoring(self):
    """
    Start monitoring configured paths for changes.
    
    Returns:
        bool: Success status
    """

def stop_monitoring(self):
    """
    Stop monitoring file changes.
    
    Returns:
        bool: Success status
    """

def is_monitoring(self):
    """
    Check if monitoring is active.
    
    Returns:
        bool: Monitoring status
    """
```

### Event Handler Methods

```python
def handle_file_change(self, file_path, change_type):
    """
    Handle detected file change event.
    
    Args:
        file_path (str): Path to changed file
        change_type (str): Type of change (create/modify/delete)
        
    Returns:
        dict: Action taken
    """

def handle_verbnet_change(self, file_path, change_type):
    """
    Handle VerbNet corpus file change.
    
    Args:
        file_path (str): Changed file path
        change_type (str): Type of change
        
    Returns:
        bool: Rebuild success status
    """

def handle_framenet_change(self, file_path, change_type):
    """
    Handle FrameNet corpus file change.
    
    Args:
        file_path (str): Changed file path
        change_type (str): Type of change
        
    Returns:
        bool: Rebuild success status
    """

def handle_propbank_change(self, file_path, change_type):
    """
    Handle PropBank corpus file change.
    
    Args:
        file_path (str): Changed file path
        change_type (str): Type of change
        
    Returns:
        bool: Rebuild success status
    """
```

### Rebuild Methods

```python
def trigger_rebuild(self, corpus_type, reason=None):
    """
    Trigger rebuild of specific corpus collection.
    
    Args:
        corpus_type (str): Type of corpus to rebuild
        reason (str): Optional reason for rebuild
        
    Returns:
        dict: Rebuild result with timing
    """

def batch_rebuild(self, corpus_types):
    """
    Perform batch rebuild of multiple corpora.
    
    Args:
        corpus_types (list): List of corpus types to rebuild
        
    Returns:
        dict: Results for each corpus rebuild
    """
```

### Logging Methods

```python
def get_change_log(self, limit=100):
    """
    Get recent file change log.
    
    Args:
        limit (int): Maximum entries to return
        
    Returns:
        list: Recent change entries
    """

def get_rebuild_history(self, limit=50):
    """
    Get rebuild history.
    
    Args:
        limit (int): Maximum entries to return
        
    Returns:
        list: Recent rebuild entries
    """

def log_event(self, event_type, details):
    """
    Log monitoring event.
    
    Args:
        event_type (str): Type of event
        details (dict): Event details
        
    Returns:
        bool: Success status
    """
```

### Error Handling Methods

```python
def handle_rebuild_error(self, error, corpus_type):
    """
    Handle errors during rebuild process.
    
    Args:
        error (Exception): The error that occurred
        corpus_type (str): Corpus being rebuilt
        
    Returns:
        dict: Error handling result
    """

def set_error_recovery_strategy(self, max_retries=3, retry_delay=30):
    """
    Configure error recovery strategy.
    
    Args:
        max_retries (int): Maximum rebuild retry attempts
        retry_delay (int): Seconds between retries
        
    Returns:
        dict: Current error recovery configuration
    """
```

## 11. Refactoring Implementation Plan for New Classes

### Phase 1: Create CorpusLoader Class
1. **Create file-based corpus parsers**
   - XML parsers for VerbNet, FrameNet, PropBank, OntoNotes, VN API
   - JSON parsers for SemNet and Reference documentation  
   - CSV parser for BSO mappings
   - Custom parser for WordNet text formats

2. **Create dynamic path detection**
   - Auto-detect corpus directory structures
   - Support flexible corpus organization
   - Handle missing corpora gracefully

3. **Add comprehensive error handling**
   - File access error handling
   - XML/JSON parsing error recovery
   - Schema validation error reporting

### Phase 2: Create Presentation Class
1. **Extract presentation methods from methods.py**
   - Move HTML generation functions
   - Move formatting functions
   - Keep Flask-independent logic

2. **Separate concerns**
   - Pure formatting logic
   - No external data dependencies in formatting
   - Reusable across different view layers

### Phase 3: Create CorpusMonitor Class
1. **Extract monitoring logic from monitor_corpora.py**
   - Move EventHandler class logic
   - Move file watching setup
   - Make monitoring configurable

2. **Add flexibility**
   - Support different monitoring strategies
   - Add batch processing option
   - Implement proper error recovery

### Phase 4: Create Standalone Package Structure
1. **Create src/uvi/ package structure**
   ```
   src/uvi/
   ├── __init__.py           # Package initialization
   ├── UVI.py               # Main UVI class
   ├── CorpusLoader.py      # File-based corpus loading
   ├── Presentation.py      # Display formatting (web-independent)
   ├── CorpusMonitor.py     # File system monitoring
   ├── parsers/             # Individual corpus parsers
   │   ├── __init__.py
   │   ├── verbnet_parser.py
   │   ├── framenet_parser.py
   │   ├── propbank_parser.py
   │   ├── ontonotes_parser.py
   │   ├── wordnet_parser.py
   │   ├── bso_parser.py
   │   ├── semnet_parser.py
   │   └── reference_parser.py
   └── utils/               # Utility functions
       ├── __init__.py
       ├── validation.py    # Schema validation
       ├── cross_refs.py    # Cross-corpus references
       └── file_utils.py    # File system utilities
   ```

2. **Create example usage scripts**
   ```python
   # examples/basic_usage.py
   from src.uvi.UVI import UVI
   
   uvi = UVI(corpora_path='corpora/')
   profile = uvi.get_complete_semantic_profile('run')
   ```

3. **Update existing scripts to use UVI package**
   ```python
   # Use UVI package for file-based corpus access
   # Maintain same functionality but file-based
   ```

## 12. Benefits of File-Based Class Architecture

1. **CorpusLoader Class Benefits**:
   - Direct file parsing eliminates all external dependencies
   - Comprehensive support for all 9 corpus formats
   - Built-in schema validation and error recovery
   - Cross-corpus integration and relationship discovery

2. **Presentation Class Benefits**:
   - Web-framework independent formatting logic
   - Reusable across different applications
   - Consistent semantic data display
   - Easy testing without web dependencies

3. **CorpusMonitor Class Benefits**:
   - Real-time file system monitoring
   - Automatic corpus reloading on changes
   - Flexible monitoring strategies for development
   - Comprehensive change logging and error recovery

## 13. Testing Strategy for New Classes

### CorpusLoader Tests
1. Test XML parsing for all corpus types (VerbNet, FrameNet, PropBank, OntoNotes, VN API)
2. Test JSON parsing (SemNet, Reference Docs) 
3. Test CSV parsing (BSO mappings)
4. Test WordNet custom format parsing
5. Test schema validation against DTD/XSD files
6. Test cross-corpus reference resolution
7. Test error handling for missing/corrupt files
8. Test semantic relationship discovery
9. Test memory management with large corpora

### Presentation Tests
1. Test HTML generation functions
2. Test color generation consistency
3. Test formatting edge cases
4. Test sanitization functions
5. Test JSON conversion

### CorpusMonitor Tests
1. Test file change detection
2. Test rebuild triggering
3. Test batch processing
4. Test error recovery
5. Test logging functionality

## 14. Migration Timeline

### Week 1: Core Class Development
- Days 1-2: Create CorpusLoader class with file-based parsers
- Days 3-4: Create Presentation class
- Day 5: Create CorpusMonitor class

### Week 2: Integration and Testing
- Days 1-2: Update existing files to use new classes
- Days 3-4: Write comprehensive tests
- Day 5: Integration testing

### Week 3: Documentation and Deployment
- Days 1-2: Complete documentation
- Days 3-4: Performance optimization
- Day 5: Deployment preparation

## 15. Future Considerations

1. **Performance Optimization**:
   - Implement incremental parsing for CorpusLoader
   - Add intelligent caching for parsed corpus data
   - Optimize file watching and change detection in CorpusMonitor

2. **Extensibility**:
   - Plugin system for new corpus types
   - Custom formatters for Presentation
   - Webhook support in CorpusMonitor

3. **Scalability**:
   - Support for parallel corpus parsing
   - Streaming processing for very large corpus files
   - Memory-efficient lazy loading strategies