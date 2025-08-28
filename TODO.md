# UVI Refactoring Plan

## Overview
This document outlines the refactoring plan to extract app-independent functionality from `uvi_web/uvi_flask.py` into a standalone `UVI` class in `src/uvi/UVI.py`. The goal is to create a reusable, non-web library that provides local functionality while maintaining the existing Flask application structure.

## 1. API Documentation for UVI Class

### Class: `UVI`

```python
class UVI:
    """
    A standalone class providing VerbNet, FrameNet, PropBank, and OntoNotes 
    unified interface functionality without web dependencies.
    """
    
    def __init__(self, db_name='new_corpora', mongo_uri='mongodb://localhost:27017/'):
        """
        Initialize UVI with MongoDB connection.
        
        Args:
            db_name (str): Name of the MongoDB database
            mongo_uri (str): MongoDB connection URI
        """
```

### Core Methods

#### Search and Query Methods

```python
def search_lemmas(self, lemmas, incl_vn=True, incl_fn=True, incl_pb=True, 
                  incl_on=True, logic='or', sort_behavior='alpha'):
    """
    Search for lemmas across multiple linguistic resources.
    
    Args:
        lemmas (list): List of lemmas to search
        incl_vn (bool): Include VerbNet results
        incl_fn (bool): Include FrameNet results  
        incl_pb (bool): Include PropBank results
        incl_on (bool): Include OntoNotes results
        logic (str): 'and' or 'or' logic for multi-lemma search
        sort_behavior (str): 'alpha' or 'num' sorting
        
    Returns:
        dict: Matched IDs by resource type
    """

def search_by_attribute(self, attribute_type, query_string):
    """
    Search VerbNet by specific attribute.
    
    Args:
        attribute_type (str): Type of attribute ('themrole', 'predicate', 
                             'vs_feature', 'selrestr', 'synrestr')
        query_string (str): Attribute value to search
        
    Returns:
        dict: Matched VerbNet class IDs
    """

def get_verbnet_class(self, class_id):
    """
    Retrieve VerbNet class information.
    
    Args:
        class_id (str): VerbNet class identifier
        
    Returns:
        dict: VerbNet class data
    """

def get_framenet_frame(self, frame_name):
    """
    Retrieve FrameNet frame information.
    
    Args:
        frame_name (str): FrameNet frame name
        
    Returns:
        dict: FrameNet frame data
    """

def get_propbank_frame(self, lemma):
    """
    Retrieve PropBank frame information.
    
    Args:
        lemma (str): PropBank lemma
        
    Returns:
        dict: PropBank frame data
    """

def get_ontonotes_entry(self, lemma):
    """
    Retrieve OntoNotes entry information.
    
    Args:
        lemma (str): OntoNotes lemma
        
    Returns:
        dict: OntoNotes entry data
    """
```

#### Reference Data Methods

```python
def get_references(self):
    """
    Get all reference data for UI elements.
    
    Returns:
        dict: Contains gen_themroles, predicates, vs_features, syn_res, sel_res
    """

def get_themrole_references(self):
    """
    Get all thematic role references.
    
    Returns:
        list: Sorted list of thematic roles with descriptions
    """

def get_predicate_references(self):
    """
    Get all predicate references.
    
    Returns:
        list: Sorted list of predicates with descriptions
    """

def get_verb_specific_features(self):
    """
    Get all verb-specific features.
    
    Returns:
        list: Sorted list of verb-specific features
    """

def get_syntactic_restrictions(self):
    """
    Get all syntactic restrictions.
    
    Returns:
        list: Sorted list of syntactic restrictions
    """

def get_selectional_restrictions(self):
    """
    Get all selectional restrictions.
    
    Returns:
        list: Sorted list of selectional restrictions
    """
```

#### Data Export Methods

```python
def export_resources(self, include_vn=False, include_fn=False, 
                    include_pb=False, include_on=False):
    """
    Export selected linguistic resources as JSON.
    
    Args:
        include_vn (bool): Include VerbNet data
        include_fn (bool): Include FrameNet data
        include_pb (bool): Include PropBank data
        include_on (bool): Include OntoNotes data
        
    Returns:
        str: JSON string of exported data
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

## 2. Refactoring Implementation Plan

### Phase 1: Create UVI Class Structure
1. **Create class initialization**
   - Set up MongoDB connection
   - Initialize database reference
   - Create connection management methods

2. **Import necessary dependencies**
   - pymongo for database operations
   - bson.json_util for JSON serialization
   - re for regex operations
   - operator for sorting functions

### Phase 2: Migrate Core Methods from methods.py
1. **Move database query methods**
   - `find_matching_ids` → `search_lemmas`
   - `find_matching_elements` → internal helper method
   - `get_subclass_ids` → `get_subclass_ids`
   - `full_class_hierarchy_tree` → `get_full_class_hierarchy`

2. **Move utility methods**
   - `top_parent_id` → `get_top_parent_id`
   - `unique_id` → internal helper method
   - `mongo_to_json` → internal helper method
   - `remove_object_ids` → internal helper method

3. **Move sorting methods**
   - `sort_by_char` → `get_class_hierarchy_by_name`
   - `sort_by_id` → `get_class_hierarchy_by_id`
   - `sort_key` → internal helper method

4. **Move field retrieval methods**
   - `get_themrole_fields` → `get_themrole_fields`
   - `get_pred_fields` → `get_predicate_fields`
   - `get_constant_fields` → `get_constant_fields`
   - `get_verb_specific_fields` → `get_verb_specific_fields`

### Phase 3: Extract Business Logic from uvi_flask.py
1. **Extract search logic from routes**
   - Move lemma search logic from `process_query`
   - Move attribute search logic (themrole, predicate, vs_feature, etc.)
   - Move search result processing and filtering

2. **Extract reference data retrieval**
   - Move reference data queries to `get_references` method
   - Create individual methods for each reference type

3. **Extract data export logic**
   - Move export logic from `download_json` route
   - Create `export_resources` method

4. **Extract VerbNet class processing**
   - Move class retrieval logic from `display_element` and `render_vn_class`
   - Move member filtering logic

### Phase 4: Update uvi_flask.py Imports
1. **Add UVI import**
   ```python
   from src.uvi.UVI import UVI
   ```

2. **Initialize UVI instance**
   ```python
   uvi = UVI(db_name=app.config['MONGO_DBNAME'])
   ```

3. **Update route handlers to use UVI methods**
   - Replace direct MongoDB queries with UVI method calls
   - Maintain all Flask-specific rendering and template logic

### Phase 5: Maintain Backwards Compatibility
1. **Keep all Flask routes unchanged**
   - Routes remain at same URLs
   - Request/response formats unchanged
   - Template rendering unchanged

2. **Keep methods.py imports for Flask-specific functions**
   - Functions used in templates (via context_processor)
   - HTML formatting functions (`formatted_def`, `colored_pb_example`)
   - Keep these in methods.py as they are presentation-layer specific

## 3. Testing Strategy

### Unit Tests for UVI Class
1. Test database connection initialization
2. Test each search method with various parameters
3. Test data retrieval methods
4. Test export functionality
5. Test utility methods

### Integration Tests
1. Verify Flask app continues to work with UVI class
2. Test all routes produce same results as before refactoring
3. Verify template rendering still functions correctly

## 4. Migration Steps

### Step 1: Create UVI.py with basic structure
- Define class with __init__ method
- Set up MongoDB connection

### Step 2: Migrate and adapt methods one category at a time
- Start with utility methods (least dependencies)
- Then reference data methods
- Then search methods
- Finally complex query methods

### Step 3: Update uvi_flask.py incrementally
- Add UVI import and initialization
- Update one route at a time
- Test each route after updating

### Step 4: Clean up
- Remove redundant MongoDB queries from uvi_flask.py
- Keep only presentation-layer logic in routes
- Document any methods that remain in methods.py

## 5. Benefits of Refactoring

1. **Separation of Concerns**: Business logic separated from web framework
2. **Reusability**: UVI class can be used in non-web contexts (CLI, scripts, other applications)
3. **Testing**: Easier to unit test business logic without Flask context
4. **Maintainability**: Clear distinction between data layer and presentation layer
5. **Flexibility**: Can easily swap web frameworks or create multiple interfaces

## 6. Considerations

1. **MongoDB Connection Management**: UVI class should handle connection lifecycle properly
2. **Error Handling**: Add appropriate error handling for database operations
3. **Configuration**: Allow flexible configuration without hardcoding values
4. **Documentation**: Comprehensive docstrings for all public methods
5. **Type Hints**: Consider adding type hints for better IDE support

## 7. Future Enhancements

1. **Caching**: Add caching layer for frequently accessed data
2. **Async Support**: Consider async/await for database operations
3. **Query Optimization**: Optimize complex MongoDB queries
4. **API Versioning**: Prepare for potential API changes
5. **Plugin System**: Allow extensions for additional linguistic resources

## 8. API Documentation for DataBuilder Class

### Class: `DataBuilder`

```python
class DataBuilder:
    """
    A standalone class for building and maintaining MongoDB collections 
    from corpus data sources (VerbNet, FrameNet, PropBank, OntoNotes).
    """
    
    def __init__(self, db_name='new_corpora', mongo_uri='mongodb://localhost:27017/'):
        """
        Initialize DataBuilder with MongoDB connection and corpus paths.
        
        Args:
            db_name (str): Name of the MongoDB database
            mongo_uri (str): MongoDB connection URI
        """
```

### Configuration Methods

```python
def set_corpus_paths(self, verbnet_path=None, framenet_path=None, 
                     propbank_path=None, ontonotes_url=None, wordnet_path=None,
                     bso_path=None, reference_docs_path=None):
    """
    Set paths to corpus data sources.
    
    Args:
        verbnet_path (str): Path to VerbNet corpus directory
        framenet_path (str): Path to FrameNet corpus directory
        propbank_path (str): Path to PropBank frames directory
        ontonotes_url (str): URL for OntoNotes data
        wordnet_path (str): Path to WordNet directory
        bso_path (str): Path to BSO mapping file
        reference_docs_path (str): Path to reference documents
    """
```

### Collection Building Methods

```python
def build_all_collections(self):
    """
    Build all collections (VerbNet, FrameNet, PropBank, OntoNotes).
    
    Returns:
        dict: Status of each collection build
    """

def build_verbnet_collection(self):
    """
    Build VerbNet collection from corpus files.
    
    Returns:
        bool: Success status
    """

def build_framenet_collection(self):
    """
    Build FrameNet collection from corpus files.
    
    Returns:
        bool: Success status
    """

def build_propbank_collection(self):
    """
    Build PropBank collection from corpus files.
    
    Returns:
        bool: Success status
    """

def build_ontonotes_collection(self):
    """
    Build OntoNotes collection from web resource.
    
    Returns:
        bool: Success status
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
def generate_class_hierarchy_html(self, class_id, db_connection):
    """
    Generate HTML representation of class hierarchy.
    
    Args:
        class_id (str): VerbNet class ID
        db_connection: Database connection
        
    Returns:
        str: HTML string for class hierarchy
    """

def generate_sanitized_class_html(self, vn_class_id, db_connection):
    """
    Generate sanitized VerbNet class HTML.
    
    Args:
        vn_class_id (str): VerbNet class ID
        db_connection: Database connection
        
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
    Convert MongoDB elements to display-ready JSON.
    
    Args:
        elements: MongoDB cursor or list
        
    Returns:
        str: JSON string for display
    """

def strip_object_ids(self, data):
    """
    Remove MongoDB ObjectIds from data for clean display.
    
    Args:
        data (dict/list): Data containing ObjectIds
        
    Returns:
        dict/list: Data without ObjectIds
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
        Initialize CorpusMonitor with DataBuilder instance.
        
        Args:
            data_builder (DataBuilder): Instance of DataBuilder for rebuilds
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

### Phase 1: Create DataBuilder Class
1. **Extract corpus building logic from build_mongo_collections.py**
   - Move all parse functions (parse_sense, parse_on_frame, etc.)
   - Move collection building functions
   - Move reference data building functions

2. **Create configurable paths**
   - Remove hardcoded paths
   - Add configuration methods
   - Support environment variables

3. **Add error handling and logging**
   - Wrap database operations
   - Add detailed logging
   - Implement rollback on failure

### Phase 2: Create Presentation Class
1. **Extract presentation methods from methods.py**
   - Move HTML generation functions
   - Move formatting functions
   - Keep Flask-independent logic

2. **Separate concerns**
   - Pure formatting logic
   - No database dependencies in formatting
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

### Phase 4: Update Existing Files
1. **Update build_mongo_collections.py**
   ```python
   from src.uvi.DataBuilder import DataBuilder
   
   if __name__ == "__main__":
       builder = DataBuilder()
       builder.build_all_collections()
   ```

2. **Update monitor_corpora.py**
   ```python
   from src.uvi.DataBuilder import DataBuilder
   from src.uvi.CorpusMonitor import CorpusMonitor
   
   builder = DataBuilder()
   monitor = CorpusMonitor(builder)
   monitor.start_monitoring()
   ```

3. **Update methods.py**
   ```python
   from src.uvi.Presentation import Presentation
   
   presenter = Presentation()
   # Keep only Flask-specific template helpers
   ```

## 12. Benefits of Additional Refactoring

1. **DataBuilder Class Benefits**:
   - Reusable corpus building logic
   - Testable parsing functions
   - Configurable paths and settings
   - Better error handling

2. **Presentation Class Benefits**:
   - Separation of formatting from business logic
   - Reusable across different UI frameworks
   - Easier to test display logic
   - Consistent formatting rules

3. **CorpusMonitor Class Benefits**:
   - Decoupled monitoring from building
   - Flexible monitoring strategies
   - Better error recovery
   - Comprehensive logging

## 13. Testing Strategy for New Classes

### DataBuilder Tests
1. Test XML/HTML parsing functions
2. Test collection building with sample data
3. Test error handling for corrupt files
4. Test BSO mapping integration
5. Test reference data extraction

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
- Days 1-2: Create DataBuilder class
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
   - Implement incremental builds for DataBuilder
   - Add caching for Presentation formatting
   - Optimize file watching in CorpusMonitor

2. **Extensibility**:
   - Plugin system for new corpus types
   - Custom formatters for Presentation
   - Webhook support in CorpusMonitor

3. **Scalability**:
   - Support for distributed building
   - Parallel processing for large corpora
   - Cloud storage integration