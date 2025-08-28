# CorpusLoader Refactoring Plan

## Overview
Refactor the monolithic CorpusLoader class (1863 lines) into 5 specialized classes:
1. **CorpusLoader** - Main orchestrator class
2. **CorpusParser** - Parsing methods for all corpus types
3. **CorpusCollectionBuilder** - Reference data building methods
4. **CorpusCollectionValidator** - Validation methods
5. **CorpusCollectionAnalyzer** - Statistics and metadata methods

## File Structure
```
src/uvi/
├── CorpusLoader.py (main class)
├── CorpusParser.py
├── CorpusCollectionBuilder.py
├── CorpusCollectionValidator.py
└── CorpusCollectionAnalyzer.py
```

## Detailed Refactoring Plan

### 1. Create CorpusParser.py
**Purpose**: Extract all parsing methods into a dedicated parser class

**Methods to Move** (lines 187-1452):
- `parse_verbnet_files()` (187-250)
- `_parse_verbnet_class()` (252-381)
- `_parse_verbnet_subclass()` (383-432)
- `_extract_frame_description()` (434-450)
- `_build_verbnet_hierarchy()` (452-503)
- `parse_framenet_files()` (505-557)
- `_parse_framenet_frame_index()` (559-589)
- `_parse_framenet_frame()` (591-659)
- `_parse_framenet_lu_index()` (661-690)
- `_parse_framenet_relations()` (692-734)
- `parse_propbank_files()` (736-786)
- `_parse_propbank_frame()` (788-859)
- `parse_ontonotes_files()` (861-900)
- `_parse_ontonotes_data()` (902-957)
- `parse_wordnet_files()` (959-1024)
- `_parse_wordnet_data_file()` (1026-1077)
- `_parse_wordnet_index_file()` (1079-1134)
- `_parse_wordnet_exception_file()` (1136-1158)
- `parse_bso_mappings()` (1160-1229)
- `load_bso_mappings()` (1231-1252)
- `apply_bso_mappings()` (1254-1272)
- `parse_semnet_data()` (1274-1320)
- `parse_reference_docs()` (1322-1402)
- `_parse_tsv_file()` (1404-1423)
- `parse_vn_api_files()` (1425-1452)

**Required Changes**:
- Create class with `__init__` that accepts corpus_paths and logger
- All methods remain the same but reference `self.corpus_paths` and `self.logger`
- Return parsed data to CorpusLoader

### 2. Create CorpusCollectionBuilder.py
**Purpose**: Extract reference collection building methods

**Methods to Move** (lines 1454-1613):
- `build_reference_collections()` (1456-1473)
- `build_predicate_definitions()` (1475-1495)
- `build_themrole_definitions()` (1497-1517)
- `build_verb_specific_features()` (1519-1553)
- `build_syntactic_restrictions()` (1555-1584)
- `build_selectional_restrictions()` (1586-1613)

**Required Changes**:
- Create class with `__init__` that accepts loaded_data and logger
- Methods access data through `self.loaded_data`
- Store results in `self.reference_collections` dict
- Return reference_collections to CorpusLoader

### 3. Create CorpusCollectionValidator.py
**Purpose**: Extract validation methods

**Methods to Move** (lines 1615-1798):
- `validate_collections()` (1617-1643)
- `_validate_verbnet_collection()` (1645-1682)
- `_validate_framenet_collection()` (1684-1716)
- `_validate_propbank_collection()` (1718-1751)
- `validate_cross_references()` (1753-1773)
- `_validate_vn_pb_mappings()` (1775-1798)

**Required Changes**:
- Create class with `__init__` that accepts loaded_data and logger
- Methods validate data from `self.loaded_data`
- Return validation results to CorpusLoader

### 4. Create CorpusCollectionAnalyzer.py
**Purpose**: Extract statistics and metadata methods

**Methods to Move** (lines 1800-1863):
- `get_collection_statistics()` (1802-1849)
- `get_build_metadata()` (1851-1863)

**Required Changes**:
- Create class with `__init__` that accepts loaded_data, load_status, build_metadata, reference_collections, corpus_paths
- Methods analyze data and return statistics
- Return analysis results to CorpusLoader

### 5. Update CorpusLoader.py
**Purpose**: Main orchestrator that uses helper classes

**Retained Methods**:
- `__init__()` (30-64) - Initialize and create helper class instances
- `_detect_corpus_paths()` (66-86)
- `get_corpus_paths()` (88-95)
- `load_all_corpora()` (97-139) - Modified to use parser
- `load_corpus()` (141-185) - Modified to delegate to parser

**New Structure**:
```python
class CorpusLoader:
    def __init__(self, corpora_path: str = 'corpora/'):
        # ... existing initialization ...
        
        # Initialize helper classes
        self.parser = CorpusParser(self.corpus_paths, self.logger)
        self.builder = None  # Initialized after data is loaded
        self.validator = None  # Initialized after data is loaded
        self.analyzer = None  # Initialized after data is loaded
    
    def load_corpus(self, corpus_name: str):
        # Route to parser methods
        if corpus_name == 'verbnet':
            data = self.parser.parse_verbnet_files()
        # ... etc for each corpus type
        
        self.loaded_data[corpus_name] = data
        # Initialize helpers if not done
        self._init_helpers()
        return data
    
    def _init_helpers(self):
        if not self.builder:
            self.builder = CorpusCollectionBuilder(self.loaded_data, self.logger)
        if not self.validator:
            self.validator = CorpusCollectionValidator(self.loaded_data, self.logger)
        if not self.analyzer:
            self.analyzer = CorpusCollectionAnalyzer(
                self.loaded_data, self.load_status, 
                self.build_metadata, self.reference_collections,
                self.corpus_paths
            )
    
    def build_reference_collections(self):
        if not self.builder:
            self._init_helpers()
        results = self.builder.build_reference_collections()
        self.reference_collections = self.builder.reference_collections
        return results
    
    def validate_collections(self):
        if not self.validator:
            self._init_helpers()
        return self.validator.validate_collections()
    
    def get_collection_statistics(self):
        if not self.analyzer:
            self._init_helpers()
        return self.analyzer.get_collection_statistics()
```

## Implementation Steps

1. **Create CorpusParser.py**
   - Copy all parsing methods (lines 187-1452)
   - Add class definition with `__init__(corpus_paths, logger)`
   - Update method signatures to use self references
   - Remove these methods from CorpusLoader.py

2. **Create CorpusCollectionBuilder.py**
   - Copy all building methods (lines 1454-1613)
   - Add class definition with `__init__(loaded_data, logger)`
   - Update to store results in `self.reference_collections`
   - Remove these methods from CorpusLoader.py

3. **Create CorpusCollectionValidator.py**
   - Copy all validation methods (lines 1615-1798)
   - Add class definition with `__init__(loaded_data, logger)`
   - Keep method signatures the same
   - Remove these methods from CorpusLoader.py

4. **Create CorpusCollectionAnalyzer.py**
   - Copy statistics methods (lines 1800-1863)
   - Add class definition with required parameters
   - Keep method signatures the same
   - Remove these methods from CorpusLoader.py

5. **Update CorpusLoader.py**
   - Add imports for new classes
   - Initialize helper classes in `__init__()`
   - Update `load_corpus()` to delegate to parser
   - Add proxy methods that delegate to helper classes
   - Ensure backward compatibility

## Testing Requirements

After refactoring:
1. All existing functionality must work exactly as before
2. The public API of CorpusLoader must remain unchanged
3. All tests should pass without modification
4. Performance should not degrade

## Benefits of Refactoring

1. **Separation of Concerns**: Each class has a single responsibility
2. **Maintainability**: Easier to find and modify specific functionality
3. **Testability**: Each component can be tested independently
4. **Reusability**: Helper classes can be used independently if needed
5. **Readability**: Smaller files are easier to understand
6. **Extensibility**: Easier to add new corpus types or validation rules

## Notes

- The BSO mapping methods (`load_bso_mappings`, `apply_bso_mappings`) logically belong with parsing
- The `_detect_corpus_paths` and `get_corpus_paths` methods stay in CorpusLoader as they're core functionality
- All private methods (starting with `_`) move with their corresponding public methods
- The logger should be shared across all classes for consistent logging
- Consider making helper classes inherit from a common base class in future iterations