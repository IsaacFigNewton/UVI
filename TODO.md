# UVI Refactoring Plan: Helper Class Architecture

## Overview
Refactor the monolithic UVI.py (126 methods) into a modular architecture using 7 specialized helper classes while maintaining the unified interface.

## Proposed Helper Classes

### 1. SearchEngine
**Purpose:** Universal and semantic search operations
**Methods:**
- `search_lemmas(lemmas, include_resources, logic, sort_behavior)` - Cross-corpus lemma search
- `search_by_semantic_pattern(pattern_type, pattern_value, target_resources)` - Semantic pattern matching
- `search_by_attribute(attribute_type, query_string, target_resources)` - Attribute-based search
- `_search_lemmas_in_corpus(normalized_lemmas, corpus_name, logic)` - Per-corpus lemma search
- `_search_semantic_pattern_in_corpus(pattern_type, pattern_value, corpus_name)` - Per-corpus pattern search
- `_search_attribute_in_corpus(attribute_type, query_string, corpus_name)` - Per-corpus attribute search
- `_sort_search_results(matches, sort_behavior)` - Result sorting
- `_calculate_search_statistics(matches)` - Search metrics

### 2. CorpusRetriever
**Purpose:** Corpus-specific data retrieval and access
**Methods:**
- `get_verbnet_class(class_id, include_subclasses, include_mappings)` - VerbNet class data
- `get_framenet_frame(frame_name, include_lexical_units, include_mappings)` - FrameNet frame data
- `get_propbank_frame(lemma, include_examples, include_mappings)` - PropBank frame data
- `get_ontonotes_entry(lemma, include_mappings)` - OntoNotes entry data
- `get_wordnet_synsets(word, pos, include_relations)` - WordNet synset data
- `get_bso_categories(verb_class, include_mappings)` - BSO category data
- `get_semnet_data(lemma, pos)` - SemNet semantic data
- `_get_corpus_entry(entry_id, corpus_name)` - Generic corpus entry retrieval

### 3. CrossReferenceManager
**Purpose:** Cross-corpus integration and relationship mapping
**Methods:**
- `search_by_cross_reference(source_id, source_corpus, target_corpus)` - Cross-corpus navigation
- `find_semantic_relationships(entry_id, corpus, relationship_types)` - Semantic relationship discovery
- `validate_cross_references(entry_id, source_corpus)` - Cross-reference validation
- `find_related_entries(entry_id, source_corpus, max_depth)` - Related entry discovery
- `trace_semantic_path(start_entry, end_entry, max_hops)` - Semantic path tracing
- `get_complete_semantic_profile(lemma)` - Comprehensive semantic profiling
- `_build_semantic_graph()` - Semantic network construction
- `_find_indirect_mappings(entry_id, source_corpus, target_corpus)` - Indirect mapping discovery

### 4. ReferenceDataProvider
**Purpose:** Reference data and field information access
**Methods:**
- `get_references()` - All reference data
- `get_themrole_references()` - Thematic role references
- `get_predicate_references()` - Predicate references  
- `get_verb_specific_features()` - Verb-specific feature list
- `get_syntactic_restrictions()` - Syntactic restriction list
- `get_selectional_restrictions()` - Selectional restriction list
- `get_themrole_fields(class_id, frame_desc_primary, syntax_num)` - Thematic role field info
- `get_predicate_fields(pred_name)` - Predicate field info
- `get_constant_fields(constant_name)` - Constant field info
- `get_verb_specific_fields(feature_name)` - Verb-specific field info

### 5. ValidationManager
**Purpose:** Schema validation and data integrity checks
**Methods:**
- `validate_corpus_schemas(corpus_names)` - Schema validation across corpora
- `validate_xml_corpus(corpus_name)` - XML corpus validation
- `check_data_integrity()` - Comprehensive integrity check
- `_validate_entry_schema(entry_id, corpus)` - Individual entry validation
- `_check_corpus_integrity(corpus_name)` - Per-corpus integrity check
- `_check_cross_reference_integrity()` - Cross-reference integrity check
- `_generate_integrity_recommendations(integrity_report)` - Improvement recommendations

### 6. ExportManager
**Purpose:** Data export and formatting operations
**Methods:**
- `export_resources(include_resources, format, output_path)` - Multi-resource export
- `export_cross_corpus_mappings()` - Cross-corpus mapping export
- `export_semantic_profile(lemma, format)` - Semantic profile export
- `_dict_to_xml(data, root_tag)` - XML formatting
- `_dict_to_csv(data)` - CSV formatting
- `_flatten_profile_to_csv(profile, lemma)` - Profile CSV formatting

### 7. HierarchyNavigator
**Purpose:** Class hierarchy and structural navigation
**Methods:**
- `get_class_hierarchy_by_name()` - Name-based hierarchy
- `get_class_hierarchy_by_id()` - ID-based hierarchy
- `get_subclass_ids(parent_class_id)` - Subclass identification
- `get_full_class_hierarchy(class_id)` - Complete hierarchy tree
- `get_top_parent_id(class_id)` - Root parent identification
- `get_member_classes(member_name)` - Member class lookup
- `_build_class_hierarchy(class_id, verbnet_data)` - Hierarchy construction

## Integration Architecture

### Core UVI Class (Reduced)
**Retained Methods:**
- `__init__(corpora_path, load_all)` - Initialization and setup
- `_load_corpus(corpus_name)` - Corpus loading
- `_setup_corpus_paths()` - Path configuration
- `_load_all_corpora()` - Bulk corpus loading
- `get_loaded_corpora()` - Status queries
- `is_corpus_loaded(corpus_name)` - Status queries
- `get_corpus_info()` - Metadata access
- `get_corpus_paths()` - Path information

**Helper Integration:**
- `self.search_engine = SearchEngine(self)`
- `self.corpus_retriever = CorpusRetriever(self)`
- `self.cross_reference_manager = CrossReferenceManager(self)`
- `self.reference_data_provider = ReferenceDataProvider(self)`
- `self.validation_manager = ValidationManager(self)`
- `self.export_manager = ExportManager(self)`
- `self.hierarchy_navigator = HierarchyNavigator(self)`

### Method Delegation Pattern
**Public Interface Preservation:**
```python
def search_lemmas(self, *args, **kwargs):
    return self.search_engine.search_lemmas(*args, **kwargs)

def get_verbnet_class(self, *args, **kwargs):
    return self.corpus_retriever.get_verbnet_class(*args, **kwargs)

def validate_corpus_schemas(self, *args, **kwargs):
    return self.validation_manager.validate_corpus_schemas(*args, **kwargs)
```

### Shared Dependencies
**Helper Class Constructor:**
```python
class BaseHelper:
    def __init__(self, uvi_instance):
        self.uvi = uvi_instance
        self.corpora_data = uvi_instance.corpora_data
        self.loaded_corpora = uvi_instance.loaded_corpora
        self.corpus_loader = uvi_instance.corpus_loader
```

## Implementation Strategy

### Phase 1: Infrastructure
- Create `BaseHelper` abstract class
- Create empty helper class files with constructors
- Add helper instantiation to UVI.__init__()

### Phase 2: Method Migration (by helper class)
- Move methods from UVI to appropriate helper classes
- Add delegation methods to UVI for backward compatibility
- Update internal method calls to use helper instances

### Phase 3: Optimization
- Remove delegation methods after confirming functionality
- Optimize cross-helper communication
- Add helper-specific optimizations

### Phase 4: Testing & Documentation
- Update test files to reflect new architecture
- Update documentation and examples
- Performance benchmarking

## Benefits

### Code Organization
- **Reduced complexity:** Main UVI class drops from 126 to ~15 core methods
- **Logical grouping:** Related functionality clustered in focused classes
- **Maintainability:** Easier to locate and modify specific functionality

### Performance
- **Lazy loading:** Helper classes can implement lazy initialization
- **Caching:** Helper-specific caching strategies
- **Parallelization:** Independent helpers can run operations concurrently

### Extensibility
- **Plugin architecture:** New helpers can be added without modifying core
- **Corpus-specific optimizations:** Helpers can implement corpus-specific logic
- **Testing isolation:** Each helper can be unit tested independently

## Backward Compatibility
- **Interface preservation:** All existing public methods remain accessible
- **Parameter compatibility:** Method signatures unchanged
- **Return value compatibility:** Output formats preserved
- **Import compatibility:** `from uvi import UVI` continues to work