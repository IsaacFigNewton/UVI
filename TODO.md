# UVI Refactoring Plan: Helper Class Architecture

## Overview
Refactor the monolithic UVI.py (126 methods) into a modular architecture using 7 specialized helper classes while maintaining the unified interface.

## Proposed Helper Classes

### 1. SearchEngine (Enhanced with CorpusCollectionAnalyzer Integration)
**Purpose:** Universal search operations with enhanced analytics via CorpusCollectionAnalyzer
**Methods:**
- `search_lemmas(lemmas, include_resources, logic, sort_behavior)` - Cross-corpus lemma search
- `search_by_semantic_pattern(pattern_type, pattern_value, target_resources)` - Semantic pattern matching
- `search_by_attribute(attribute_type, query_string, target_resources)` - Attribute-based search
- `_search_lemmas_in_corpus(normalized_lemmas, corpus_name, logic)` - Per-corpus lemma search
- `_search_semantic_pattern_in_corpus(pattern_type, pattern_value, corpus_name)` - Per-corpus pattern search
- `_search_attribute_in_corpus(attribute_type, query_string, corpus_name)` - Per-corpus attribute search
- `_sort_search_results(matches, sort_behavior)` - Result sorting
- `_calculate_enhanced_search_statistics(matches)` - **REPLACES UVI lines 4247-4261** with CorpusCollectionAnalyzer integration
- `_calculate_pattern_statistics_with_analytics(matches, pattern_type)` - **REPLACES UVI lines 4444-4459** with collection context
- `_calculate_attribute_statistics_with_coverage(matches, attribute_type)` - **REPLACES UVI lines 4575-4588** with coverage analysis

**Constructor Integration:**
```python
class SearchEngine(BaseHelper):
    def __init__(self, uvi_instance):
        super().__init__(uvi_instance)
        self.analytics = CorpusCollectionAnalyzer(
            loaded_data=uvi_instance.corpora_data,
            load_status=uvi_instance.corpus_loader.load_status,
            build_metadata=uvi_instance.corpus_loader.build_metadata,
            reference_collections=uvi_instance.corpus_loader.reference_collections,
            corpus_paths=uvi_instance.corpus_paths
        )
```

**UVI Code Elimination:**
- **REMOVE 15 lines**: _calculate_search_statistics() method (lines 4247-4261)
- **REMOVE 16 lines**: _calculate_pattern_statistics() method (lines 4444-4459)
- **REMOVE 14 lines**: _calculate_attribute_statistics() method (lines 4575-4588)
- **TOTAL: 45 lines of duplicate statistics code eliminated and enhanced with CorpusCollectionAnalyzer**

**CorpusCollectionAnalyzer Integration for Enhanced Analytics:**
```python
class SearchEngine(BaseHelper):
    def __init__(self, uvi_instance):
        super().__init__(uvi_instance)
        # Access to CorpusCollectionAnalyzer for comprehensive statistics
        self.analytics = CorpusCollectionAnalyzer(
            uvi_instance.corpora_data,
            uvi_instance.corpus_loader.load_status,
            uvi_instance.corpus_loader.build_metadata,
            uvi_instance.corpus_loader.reference_collections,
            uvi_instance.corpus_paths
        )
        
    def _calculate_search_statistics(self, matches: Dict[str, Any]) -> Dict[str, Any]:
        """Replace UVI duplicate with CorpusCollectionAnalyzer-enhanced statistics."""
        # Basic search statistics (keep UVI logic for search-specific metrics)
        basic_stats = {
            'total_corpora_with_matches': len(matches),
            'total_matches_by_corpus': {},
            'total_matches_overall': 0
        }
        
        for corpus_name, corpus_matches in matches.items():
            corpus_total = sum(len(lemma_matches) for lemma_matches in corpus_matches.values())
            basic_stats['total_matches_by_corpus'][corpus_name] = corpus_total
            basic_stats['total_matches_overall'] += corpus_total
        
        # Enhance with CorpusCollectionAnalyzer collection statistics
        collection_stats = self.analytics.get_collection_statistics()
        enhanced_stats = {
            **basic_stats,
            'corpus_collection_sizes': {
                corpus: collection_stats.get(corpus, {})
                for corpus in matches.keys()
            },
            'search_coverage_percentage': self._calculate_coverage_percentage(matches, collection_stats)
        }
        
        return enhanced_stats
        
    def _calculate_coverage_percentage(self, matches: Dict[str, Any], 
                                     collection_stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate search coverage as percentage of total corpus collections."""
        coverage = {}
        for corpus_name, corpus_matches in matches.items():
            corpus_stats = collection_stats.get(corpus_name, {})
            
            # Calculate coverage based on corpus type
            if corpus_name == 'verbnet' and 'classes' in corpus_stats:
                total_classes = corpus_stats['classes']
                matched_classes = len(set(match.get('class_id') for match_list in corpus_matches.values() 
                                        for match in match_list if match.get('class_id')))
                coverage[corpus_name] = (matched_classes / total_classes * 100) if total_classes > 0 else 0
                
            elif corpus_name == 'framenet' and 'frames' in corpus_stats:
                total_frames = corpus_stats['frames']
                matched_frames = len(set(match.get('frame_name') for match_list in corpus_matches.values() 
                                       for match in match_list if match.get('frame_name')))
                coverage[corpus_name] = (matched_frames / total_frames * 100) if total_frames > 0 else 0
                
            elif corpus_name == 'propbank' and 'predicates' in corpus_stats:
                total_predicates = corpus_stats['predicates']
                matched_predicates = len(set(match.get('predicate') for match_list in corpus_matches.values() 
                                           for match in match_list if match.get('predicate')))
                coverage[corpus_name] = (matched_predicates / total_predicates * 100) if total_predicates > 0 else 0
        
        return coverage
        
    def _calculate_pattern_statistics(self, matches: Dict[str, Any], pattern_type: str) -> Dict[str, Any]:
        """Replace UVI duplicate with CorpusCollectionAnalyzer-enhanced pattern statistics."""
        # Basic pattern statistics (keep UVI logic)
        basic_stats = {
            'pattern_type': pattern_type,
            'total_corpora_with_matches': len(matches),
            'total_matches_by_corpus': {},
            'total_matches_overall': 0
        }
        
        for corpus_name, corpus_matches in matches.items():
            total_matches = len(corpus_matches)
            basic_stats['total_matches_by_corpus'][corpus_name] = total_matches
            basic_stats['total_matches_overall'] += total_matches
        
        # Enhance with collection context from CorpusCollectionAnalyzer
        collection_stats = self.analytics.get_collection_statistics()
        return {
            **basic_stats,
            'collection_context': {
                corpus: collection_stats.get(corpus, {})
                for corpus in matches.keys()
            },
            'pattern_density': self._calculate_pattern_density(matches, collection_stats, pattern_type)
        }
        
    def _calculate_attribute_statistics(self, matches: Dict[str, Any], attribute_type: str) -> Dict[str, Any]:
        """Replace UVI duplicate with CorpusCollectionAnalyzer-enhanced attribute statistics."""
        # Basic attribute statistics (keep UVI logic)
        basic_stats = {
            'attribute_type': attribute_type,
            'total_corpora_with_matches': len(matches),
            'total_matches_by_corpus': {},
            'total_matches_overall': 0
        }
        
        for corpus_name, corpus_matches in matches.items():
            total_matches = len(corpus_matches)
            basic_stats['total_matches_by_corpus'][corpus_name] = total_matches
            basic_stats['total_matches_overall'] += total_matches
        
        # Enhance with CorpusCollectionAnalyzer metadata
        build_metadata = self.analytics.get_build_metadata()
        return {
            **basic_stats,
            'corpus_metadata': build_metadata,
            'attribute_distribution': self._analyze_attribute_distribution(matches, attribute_type)
        }
```

**UVI Method Replacements with CorpusCollectionAnalyzer:**
- **REPLACE** UVI method `_calculate_search_statistics()` (lines 4247-4260) with CorpusCollectionAnalyzer delegation
- **REPLACE** UVI method `_calculate_pattern_statistics()` (lines 4444-4458) with CorpusCollectionAnalyzer delegation  
- **REPLACE** UVI method `_calculate_attribute_statistics()` (lines 4575-4589) with CorpusCollectionAnalyzer delegation
- **Constructor Changes:**
  ```python
  def __init__(self, uvi_instance):
      super().__init__(uvi_instance)
      # Initialize CorpusCollectionAnalyzer for enhanced analytics
      self.analytics = CorpusCollectionAnalyzer(
          uvi_instance.corpora_data,
          uvi_instance.corpus_loader.load_status,
          uvi_instance.corpus_loader.build_metadata,
          uvi_instance.corpus_loader.reference_collections,
          uvi_instance.corpus_paths
      )
  ```

**CorpusCollectionBuilder Integration for Enhanced Search:**
```python
class SearchEngine(BaseHelper):
    def __init__(self, uvi_instance):
        super().__init__(uvi_instance)
        # Access to CorpusCollectionBuilder for reference-based search enhancement
        self.collection_builder = uvi_instance.reference_data_provider.collection_builder
        
    def search_by_reference_type(self, reference_type: str, query: str, fuzzy_match: bool = False) -> Dict[str, Any]:
        """Search within CorpusCollectionBuilder reference collections."""
        if not self.collection_builder.reference_collections:
            self.collection_builder.build_reference_collections()
            
        collections = self.collection_builder.reference_collections
        results = []
        
        if reference_type == 'themroles' and 'themroles' in collections:
            results = self._search_reference_collection(
                collections['themroles'], query, fuzzy_match, 'themrole'
            )
        elif reference_type == 'predicates' and 'predicates' in collections:
            results = self._search_reference_collection(
                collections['predicates'], query, fuzzy_match, 'predicate'
            )
        elif reference_type == 'features' and 'verb_specific_features' in collections:
            results = self._search_feature_list(
                collections['verb_specific_features'], query, fuzzy_match
            )
        elif reference_type == 'syntactic_restrictions' and 'syntactic_restrictions' in collections:
            results = self._search_restriction_list(
                collections['syntactic_restrictions'], query, fuzzy_match, 'syntactic'
            )
        elif reference_type == 'selectional_restrictions' and 'selectional_restrictions' in collections:
            results = self._search_restriction_list(
                collections['selectional_restrictions'], query, fuzzy_match, 'selectional'
            )
            
        return {
            'reference_type': reference_type,
            'query': query,
            'fuzzy_match': fuzzy_match,
            'total_matches': len(results),
            'matches': results
        }
        
    def search_by_semantic_pattern(self, pattern_type: str, pattern_value: str, target_resources: List[str] = None) -> Dict[str, Any]:
        """Enhanced semantic pattern search using CorpusCollectionBuilder reference data."""
        # Standard corpus search
        corpus_matches = self._search_corpus_semantic_patterns(pattern_type, pattern_value, target_resources)
        
        # Enhanced search using reference collections
        reference_matches = []
        if self.collection_builder.reference_collections:
            # Search predicates for semantic patterns
            if pattern_type in ['predicate', 'semantic'] and 'predicates' in self.collection_builder.reference_collections:
                pred_matches = self._search_reference_collection(
                    self.collection_builder.reference_collections['predicates'], 
                    pattern_value, fuzzy_match=True, result_type='semantic_predicate'
                )
                reference_matches.extend(pred_matches)
                
            # Search themroles for semantic patterns  
            if pattern_type in ['themrole', 'role'] and 'themroles' in self.collection_builder.reference_collections:
                role_matches = self._search_reference_collection(
                    self.collection_builder.reference_collections['themroles'],
                    pattern_value, fuzzy_match=True, result_type='semantic_themrole'
                )
                reference_matches.extend(role_matches)
        
        return {
            'pattern_type': pattern_type,
            'pattern_value': pattern_value,
            'corpus_matches': corpus_matches,
            'reference_matches': reference_matches,
            'total_matches': len(corpus_matches.get('matches', [])) + len(reference_matches),
            'enhanced_by_references': len(reference_matches) > 0
        }
        
    def _search_reference_collection(self, collection: Dict, query: str, fuzzy_match: bool, result_type: str) -> List[Dict]:
        """Search within a CorpusCollectionBuilder reference collection."""
        results = []
        query_lower = query.lower()
        
        for item_name, item_data in collection.items():
            match_score = 0
            match_fields = []
            
            # Exact name match
            if query_lower == item_name.lower():
                match_score += 100
                match_fields.append('name_exact')
                
            # Fuzzy name match
            elif fuzzy_match and query_lower in item_name.lower():
                match_score += 75
                match_fields.append('name_fuzzy')
                
            # Description/definition match
            if isinstance(item_data, dict):
                for field in ['description', 'definition']:
                    if field in item_data and isinstance(item_data[field], str):
                        field_text = item_data[field].lower()
                        if query_lower == field_text:
                            match_score += 90
                            match_fields.append(f'{field}_exact')
                        elif fuzzy_match and query_lower in field_text:
                            match_score += 60
                            match_fields.append(f'{field}_fuzzy')
            
            if match_score > 0:
                results.append({
                    'name': item_name,
                    'data': item_data,
                    'match_score': match_score,
                    'match_fields': match_fields,
                    'result_type': result_type,
                    'source': 'corpus_collection_builder'
                })
        
        # Sort by match score descending
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results
```

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

**CorpusCollectionBuilder Integration for Reference Data Access:**
```python
class CorpusRetriever(BaseHelper):
    def __init__(self, uvi_instance):
        super().__init__(uvi_instance)
        self.corpus_parser = uvi_instance.corpus_parser
        # Access to CorpusCollectionBuilder for enriched data
        self.collection_builder = uvi_instance.reference_data_provider.collection_builder
        
    def get_verbnet_class(self, class_id, include_subclasses=True, include_mappings=True):
        """Enhanced VerbNet class retrieval with CorpusCollectionBuilder reference data."""
        # Use CorpusParser-generated data
        verbnet_data = self.uvi.corpora_data.get('verbnet', {})
        classes = verbnet_data.get('classes', {})
        
        if class_id not in classes:
            return {}
            
        class_data = classes[class_id].copy()
        
        # Enrich with CorpusCollectionBuilder reference collections
        if self.collection_builder.reference_collections:
            class_data['available_themroles'] = self.collection_builder.reference_collections.get('themroles', {}).keys()
            class_data['available_predicates'] = self.collection_builder.reference_collections.get('predicates', {}).keys()
            class_data['global_syntactic_restrictions'] = self.collection_builder.reference_collections.get('syntactic_restrictions', [])
            class_data['global_selectional_restrictions'] = self.collection_builder.reference_collections.get('selectional_restrictions', [])
        
        if include_subclasses:
            class_data['subclasses'] = self._get_subclass_data(class_id, classes)
            
        if include_mappings:
            class_data['mappings'] = self._get_class_mappings(class_id)
            
        return class_data
```

**CorpusParser Integration:**
```python
class CorpusRetriever(BaseHelper):
    def __init__(self, uvi_instance):
        super().__init__(uvi_instance)
        self.corpus_parser = uvi_instance.corpus_parser
        
    def get_verbnet_class(self, class_id, include_subclasses=True, include_mappings=True):
        """Use CorpusParser-generated data instead of UVI duplicate parsing."""
        # Access pre-parsed VerbNet data from CorpusParser
        verbnet_data = self.uvi.corpora_data.get('verbnet', {})
        classes = verbnet_data.get('classes', {})
        
        if class_id not in classes:
            return {}
            
        class_data = classes[class_id].copy()
        
        # Include subclasses if requested
        if include_subclasses:
            class_data['subclasses'] = self._get_subclass_data(class_id, classes)
            
        # Include cross-corpus mappings if requested
        if include_mappings:
            class_data['mappings'] = self._get_class_mappings(class_id)
            
        return class_data
        
    def get_framenet_frame(self, frame_name, include_lexical_units=True, include_mappings=True):
        """Use CorpusParser-generated FrameNet data."""
        framenet_data = self.uvi.corpora_data.get('framenet', {})
        frames = framenet_data.get('frames', {})
        
        if frame_name not in frames:
            return {}
            
        frame_data = frames[frame_name].copy()
        
        if not include_lexical_units:
            frame_data.pop('lexical_units', None)
            
        if include_mappings:
            frame_data['mappings'] = self._get_frame_mappings(frame_name)
            
        return frame_data
        
    def get_propbank_frame(self, lemma, include_examples=True, include_mappings=True):
        """Use CorpusParser-generated PropBank data."""
        propbank_data = self.uvi.corpora_data.get('propbank', {})
        predicates = propbank_data.get('predicates', {})
        
        if lemma not in predicates:
            return {}
            
        predicate_data = predicates[lemma].copy()
        
        if not include_examples:
            # Remove examples from rolesets
            for roleset in predicate_data.get('rolesets', []):
                roleset.pop('examples', None)
                
        if include_mappings:
            predicate_data['mappings'] = self._get_predicate_mappings(lemma)
            
        return predicate_data
```

**UVI Integration Changes - CorpusParser Delegation:**
- **REPLACE** UVI method `_load_verbnet()` (lines 3781-3838) with CorpusParser delegation
- **REPLACE** UVI method `_parse_verbnet_class()` (lines 3840-3958) with CorpusParser delegation  
- **REPLACE** UVI method `_build_class_hierarchy()` (lines 3960-3988) with CorpusParser delegation
- **Constructor Changes:**
  ```python
  def __init__(self, corpora_path='corpora/', load_all=True):
      # Initialize CorpusParser first
      self.corpus_parser = CorpusParser(self._get_corpus_paths(corpora_path), logger)
      
      # Use CorpusParser for all corpus loading instead of UVI methods
      if load_all:
          self._load_via_corpus_parser()
      
      # Initialize helper with parser access
      self.corpus_retriever = CorpusRetriever(self)
  ```
- **Method Delegation Pattern:**
  ```python
  def _load_verbnet(self, verbnet_path):
      """Delegate VerbNet loading to CorpusParser."""
      verbnet_data = self.corpus_parser.parse_verbnet_files()
      self.corpora_data['verbnet'] = verbnet_data
      self.loaded_corpora.add('verbnet')
  ```

### 3. CrossReferenceManager (Enhanced with CorpusCollectionValidator Integration)
**Purpose:** Cross-corpus integration with validation-aware relationship mapping
**Methods:**
- `search_by_cross_reference(source_id, source_corpus, target_corpus)` - Cross-corpus navigation
- `find_semantic_relationships(entry_id, corpus, relationship_types)` - **ENHANCED** with CorpusCollectionValidator validation
- `validate_cross_references(entry_id, source_corpus)` - **REPLACES UVI lines 1274-1337** with CorpusCollectionValidator delegation
- `find_related_entries(entry_id, source_corpus, max_depth)` - **ENHANCES UVI lines 1349-1400** with validation-aware discovery
- `trace_semantic_path(start_entry, end_entry, max_hops)` - Semantic path tracing
- `get_complete_semantic_profile(lemma)` - Comprehensive semantic profiling
- `_initialize_cross_reference_system_with_validator()` - **REPLACES UVI lines 2298-2397** with validator-based initialization
- `_build_validated_cross_references(valid_corpora)` - **NEW** - Build cross-references from validated data only
- `_build_semantic_graph()` - Semantic network construction
- `_find_indirect_mappings(entry_id, source_corpus, target_corpus)` - Indirect mapping discovery

**Constructor Integration:**
```python
class CrossReferenceManager(BaseHelper):
    def __init__(self, uvi_instance):
        super().__init__(uvi_instance)
        self.corpus_validator = CorpusCollectionValidator(
            loaded_data=uvi_instance.corpora_data,
            logger=uvi_instance.logger
        )
        self.cross_reference_index = {}
```

**UVI Code Elimination:**
- **REMOVE 64 lines**: validate_cross_references() method (lines 1274-1337)
- **REMOVE 100 lines**: Cross-reference system methods (lines 2298-2397)
- **TOTAL: 164 lines replaced with CorpusCollectionValidator integration**

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

**CorpusCollectionBuilder Integration:**
```python
class ReferenceDataProvider(BaseHelper):
    def __init__(self, uvi_instance):
        super().__init__(uvi_instance)
        self.corpus_loader = uvi_instance.corpus_loader
        # Initialize CorpusCollectionBuilder for reference data building
        self.collection_builder = CorpusCollectionBuilder(
            loaded_data=uvi_instance.corpora_data,
            logger=uvi_instance.logger
        )
        
    def get_references(self):
        """Delegate to CorpusCollectionBuilder instead of duplicate logic."""
        # Ensure reference collections are built via CorpusCollectionBuilder
        if not self.collection_builder.reference_collections:
            self.collection_builder.build_reference_collections()
        
        return {
            'gen_themroles': self.get_themrole_references(),
            'predicates': self.get_predicate_references(),  
            'vs_features': self.get_verb_specific_features(),
            'syn_res': self.get_syntactic_restrictions(),
            'sel_res': self.get_selectional_restrictions(),
            'metadata': {
                'total_collections': 5,
                'generated_at': self._get_timestamp()
            }
        }
        
    def get_themrole_references(self):
        """Use CorpusCollectionBuilder's built reference collections."""
        self._ensure_references_built()
        themroles = self.collection_builder.reference_collections.get('themroles', {})
        return [{'name': name, **data} for name, data in themroles.items()]
        
    def get_predicate_references(self):
        """Use CorpusCollectionBuilder's built reference collections."""  
        self._ensure_references_built()
        predicates = self.collection_builder.reference_collections.get('predicates', {})
        return [{'name': name, **data} for name, data in predicates.items()]
        
    def get_verb_specific_features(self):
        """Use CorpusCollectionBuilder's extracted features."""
        self._ensure_references_built()
        return self.collection_builder.reference_collections.get('verb_specific_features', [])
        
    def get_syntactic_restrictions(self):
        """Use CorpusCollectionBuilder's extracted restrictions."""
        self._ensure_references_built()
        return self.collection_builder.reference_collections.get('syntactic_restrictions', [])
        
    def get_selectional_restrictions(self):
        """Use CorpusCollectionBuilder's extracted restrictions."""
        self._ensure_references_built()
        return self.collection_builder.reference_collections.get('selectional_restrictions', [])
        
    def _ensure_references_built(self):
        """Ensure CorpusCollectionBuilder reference collections are built."""
        if not self.collection_builder.reference_collections:
            self.collection_builder.build_reference_collections()
```

**Specific UVI Method Replacements with CorpusCollectionBuilder:**

**1. get_references() Method (Lines 1459-1500):**
```python
# REMOVE UVI duplicate logic:
def get_references(self) -> Dict[str, Any]:
    # Remove lines 1466-1500: Manual reference building
    # REPLACE with CorpusCollectionBuilder delegation:
    return self.reference_data_provider.get_references()
```

**2. get_themrole_references() Method (Lines 1502-1563):**
```python
# REMOVE UVI duplicate extraction (lines 1512-1563):
def get_themrole_references(self) -> List[Dict[str, Any]]:
    # Remove manual corpus_loader.reference_collections access
    # Remove VerbNet corpus extraction logic (lines 1533-1558)
    # REPLACE with CorpusCollectionBuilder delegation:
    return self.reference_data_provider.get_themrole_references()
```

**3. get_predicate_references() Method (Lines 1565-1626):**
```python
# REMOVE UVI duplicate extraction (lines 1574-1626):
def get_predicate_references(self) -> List[Dict[str, Any]]:
    # Remove manual corpus_loader.reference_collections access
    # Remove VerbNet corpus extraction logic (lines 1597-1621)
    # REPLACE with CorpusCollectionBuilder delegation:
    return self.reference_data_provider.get_predicate_references()
```

**4. get_verb_specific_features() Method (Lines 1628-1662):**
```python
# REMOVE UVI duplicate extraction (lines 1635-1661):
def get_verb_specific_features(self) -> List[str]:
    # Remove manual VerbNet class iteration (lines 1644-1658)
    # Remove duplicate feature extraction logic
    # REPLACE with CorpusCollectionBuilder delegation:
    return self.reference_data_provider.get_verb_specific_features()
```

**5. get_syntactic_restrictions() Method (Lines 1664-1704):**
```python
# REMOVE UVI duplicate extraction (lines 1671-1703):
def get_syntactic_restrictions(self) -> List[str]:
    # Remove manual VerbNet frame iteration (lines 1680-1701)
    # Remove duplicate synrestrs extraction logic
    # REPLACE with CorpusCollectionBuilder delegation:
    return self.reference_data_provider.get_syntactic_restrictions()
```

**6. get_selectional_restrictions() Method (Lines 1706-1762):**
```python
# REMOVE UVI duplicate extraction (lines 1713-1761):
def get_selectional_restrictions(self) -> List[str]:
    # Remove manual VerbNet frame iteration (lines 1722-1759)
    # Remove duplicate selrestrs extraction logic
    # REPLACE with CorpusCollectionBuilder delegation:
    return self.reference_data_provider.get_selectional_restrictions()
```

**Constructor Integration Changes:**
```python
class UVI:
    def __init__(self, corpora_path='corpora/', load_all=True):
        # Initialize corpus loader first
        self.corpus_loader = CorpusLoader(corpora_path)
        
        # Initialize helper with CorpusCollectionBuilder integration
        self.reference_data_provider = ReferenceDataProvider(self)
        
        if load_all:
            self.corpus_loader.load_all_corpora()
            # Build reference collections via CorpusCollectionBuilder
            self.reference_data_provider.collection_builder.build_reference_collections()
```

**Internal Method Call Updates:**
```python
# Update all internal references from:
# self.get_references() → self.reference_data_provider.get_references()
# self.get_themrole_references() → self.reference_data_provider.get_themrole_references()
# self.get_predicate_references() → self.reference_data_provider.get_predicate_references()
# self.get_verb_specific_features() → self.reference_data_provider.get_verb_specific_features()
# self.get_syntactic_restrictions() → self.reference_data_provider.get_syntactic_restrictions()
# self.get_selectional_restrictions() → self.reference_data_provider.get_selectional_restrictions()
```

**Code Elimination Summary:**
- **REMOVE 167 lines** of duplicate collection building code (lines 1459-1626 + 1628-1762)
- **ELIMINATE** manual VerbNet corpus iteration in 6 different methods
- **REPLACE** with 6 single-line delegation calls to CorpusCollectionBuilder
- **MAINTAIN** exact same method signatures and return value formats
- **GAIN** centralized, optimized collection building via CorpusCollectionBuilder's template methods

### 5. ValidationManager (Enhanced with CorpusCollectionValidator Integration)
**Purpose:** Comprehensive validation using CorpusCollectionValidator to eliminate duplicate UVI code
**Methods:**
- `validate_corpus_schemas(corpus_names)` - **REPLACES UVI lines 1887-1954** with CorpusCollectionValidator delegation
- `validate_xml_corpus(corpus_name)` - **REPLACES UVI lines 1956-1982** with CorpusCollectionValidator delegation
- `check_data_integrity()` - **ENHANCES UVI lines 1984-2036** with CorpusCollectionValidator integration
- `_validate_entry_schema_with_validator(entry_id, corpus)` - **REPLACES UVI lines 3083-3151** with CorpusCollectionValidator logic

**Constructor Integration:**
```python
class ValidationManager(BaseHelper):
    def __init__(self, uvi_instance):
        super().__init__(uvi_instance)
        self.corpus_validator = CorpusCollectionValidator(
            loaded_data=uvi_instance.corpora_data,
            logger=uvi_instance.logger
        )
```

**UVI Code Elimination:**
- **REMOVE 68 lines**: validate_corpus_schemas() method (lines 1887-1954)
- **REMOVE 27 lines**: validate_xml_corpus() method (lines 1956-1982)  
- **REMOVE 69 lines**: Internal validation methods (lines 3083-3151)
- **REMOVE 133 lines**: Corpus integrity methods (lines 3233-3366)
- **TOTAL: 297 lines of duplicate validation code eliminated**

**CorpusCollectionBuilder Integration for Reference Validation:**
```python
class ValidationManager(BaseHelper):
    def __init__(self, uvi_instance):
        super().__init__(uvi_instance)
        self.corpus_parser = uvi_instance.corpus_parser
        self.corpus_loader = uvi_instance.corpus_loader
        # Access to CorpusCollectionBuilder for reference validation
        self.collection_builder = uvi_instance.reference_data_provider.collection_builder
        
    def validate_reference_collections(self) -> Dict[str, bool]:
        """Validate that CorpusCollectionBuilder collections are properly built."""
        validation_results = {}
        
        # Ensure collections are built
        if not self.collection_builder.reference_collections:
            build_results = self.collection_builder.build_reference_collections()
            validation_results.update(build_results)
        
        # Validate individual collections
        collections = self.collection_builder.reference_collections
        validation_results.update({
            'themroles_valid': self._validate_themrole_collection(collections.get('themroles', {})),
            'predicates_valid': self._validate_predicate_collection(collections.get('predicates', {})),
            'vs_features_valid': self._validate_feature_collection(collections.get('verb_specific_features', [])),
            'syn_restrictions_valid': self._validate_restriction_collection(collections.get('syntactic_restrictions', [])),
            'sel_restrictions_valid': self._validate_restriction_collection(collections.get('selectional_restrictions', []))
        })
        
        return validation_results
        
    def _validate_themrole_collection(self, themroles: Dict) -> bool:
        """Validate themrole collection from CorpusCollectionBuilder."""
        if not themroles:
            return False
            
        required_fields = ['description', 'definition']
        for role_name, role_data in themroles.items():
            if not isinstance(role_data, dict):
                return False
            # Validate against CorpusCollectionBuilder's expected format
            for field in required_fields:
                if field not in role_data:
                    self.logger.warning(f"Themrole {role_name} missing required field: {field}")
                    
        return True
        
    def _validate_predicate_collection(self, predicates: Dict) -> bool:
        """Validate predicate collection from CorpusCollectionBuilder."""
        if not predicates:
            return False
            
        for pred_name, pred_data in predicates.items():
            if not isinstance(pred_data, dict):
                return False
            # Validate against CorpusCollectionBuilder's expected format
            if 'definition' not in pred_data:
                self.logger.warning(f"Predicate {pred_name} missing definition")
                
        return True
        
    def check_reference_consistency(self) -> Dict[str, Any]:
        """Check consistency between CorpusCollectionBuilder collections and corpus data."""
        consistency_report = {
            'themrole_consistency': self._check_themrole_consistency(),
            'predicate_consistency': self._check_predicate_consistency(),
            'feature_consistency': self._check_feature_consistency(),
            'restriction_consistency': self._check_restriction_consistency()
        }
        
        return consistency_report
        
    def _check_themrole_consistency(self) -> Dict[str, Any]:
        """Check if CorpusCollectionBuilder themroles match actual corpus usage."""
        if not self.collection_builder.reference_collections:
            return {'error': 'Reference collections not built'}
            
        collection_themroles = set(self.collection_builder.reference_collections.get('themroles', {}).keys())
        corpus_themroles = set()
        
        # Extract actual themroles used in VerbNet corpus
        if 'verbnet' in self.uvi.corpora_data:
            verbnet_data = self.uvi.corpora_data['verbnet']
            classes = verbnet_data.get('classes', {})
            
            for class_data in classes.values():
                for themrole in class_data.get('themroles', []):
                    if isinstance(themrole, dict) and 'type' in themrole:
                        corpus_themroles.add(themrole['type'])
        
        return {
            'collection_count': len(collection_themroles),
            'corpus_count': len(corpus_themroles),
            'missing_in_collection': list(corpus_themroles - collection_themroles),
            'unused_in_corpus': list(collection_themroles - corpus_themroles),
            'consistency_score': len(collection_themroles.intersection(corpus_themroles)) / max(len(collection_themroles.union(corpus_themroles)), 1)
        }
```

**CorpusParser Integration:**
```python
class ValidationManager(BaseHelper):
    def __init__(self, uvi_instance):
        super().__init__(uvi_instance)
        self.corpus_parser = uvi_instance.corpus_parser
        self.corpus_loader = uvi_instance.corpus_loader
        
    def validate_corpus_schemas(self, corpus_names=None):
        """Delegate to CorpusLoader validation with CorpusParser integration."""
        if corpus_names is None:
            corpus_names = list(self.uvi.loaded_corpora)
            
        validation_results = {
            'validation_timestamp': self._get_timestamp(),
            'total_corpora': len(corpus_names),
            'validated_corpora': 0,
            'failed_corpora': 0,
            'corpus_results': {}
        }
        
        for corpus_name in corpus_names:
            try:
                # Use CorpusParser's built-in validation via error handlers
                if corpus_name == 'verbnet':
                    result = self._validate_parser_data('verbnet', 
                                                      self.corpus_parser.parse_verbnet_files)
                elif corpus_name == 'framenet':
                    result = self._validate_parser_data('framenet', 
                                                      self.corpus_parser.parse_framenet_files)
                elif corpus_name == 'propbank':
                    result = self._validate_parser_data('propbank', 
                                                      self.corpus_parser.parse_propbank_files)
                elif corpus_name == 'ontonotes':
                    result = self._validate_parser_data('ontonotes', 
                                                      self.corpus_parser.parse_ontonotes_files)
                elif corpus_name == 'wordnet':
                    result = self._validate_parser_data('wordnet', 
                                                      self.corpus_parser.parse_wordnet_files)
                else:
                    # Fallback to CorpusLoader validation
                    result = self.corpus_loader.validate_collections()
                    
                validation_results['corpus_results'][corpus_name] = result
                
                if result.get('status') == 'valid' or result.get('error_count', 0) == 0:
                    validation_results['validated_corpora'] += 1
                else:
                    validation_results['failed_corpora'] += 1
                    
            except Exception as e:
                validation_results['corpus_results'][corpus_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                validation_results['failed_corpora'] += 1
                
        return validation_results
        
    def _validate_parser_data(self, corpus_name, parser_method):
        """Validate corpus using CorpusParser methods with error tracking."""
        try:
            parsed_data = parser_method()
            statistics = parsed_data.get('statistics', {})
            
            return {
                'status': 'valid',
                'files_processed': statistics.get('total_files', 0),
                'parsed_files': statistics.get('parsed_files', 0),
                'error_files': statistics.get('error_files', 0),
                'validation_method': 'corpus_parser'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'validation_method': 'corpus_parser'
            }
        
    def validate_xml_corpus(self, corpus_name):
        """Enhanced XML validation using CorpusParser error handling."""
        if corpus_name not in ['verbnet', 'framenet', 'propbank', 'ontonotes', 'vn_api']:
            return {
                'valid': False,
                'error': f'Corpus {corpus_name} is not XML-based'
            }
            
        # Use CorpusParser's XML parsing with built-in validation
        parser_methods = {
            'verbnet': self.corpus_parser.parse_verbnet_files,
            'framenet': self.corpus_parser.parse_framenet_files,
            'propbank': self.corpus_parser.parse_propbank_files,
            'ontonotes': self.corpus_parser.parse_ontonotes_files,
            'vn_api': self.corpus_parser.parse_vn_api_files
        }
        
        if corpus_name in parser_methods:
            return self._validate_xml_via_parser(corpus_name, parser_methods[corpus_name])
        else:
            return {'valid': False, 'error': f'No validation method for {corpus_name}'}
            
    def _validate_xml_via_parser(self, corpus_name, parser_method):
        """Validate XML files using CorpusParser's error handling decorators."""
        try:
            # CorpusParser methods use @error_handler decorators that catch XML errors
            parsed_data = parser_method()
            statistics = parsed_data.get('statistics', {})
            
            total_files = statistics.get('total_files', 0)
            error_files = statistics.get('error_files', 0)
            valid_files = total_files - error_files
            
            return {
                'valid': error_files == 0,
                'total_files': total_files,
                'valid_files': valid_files,
                'error_files': error_files,
                'validation_details': statistics
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'validation_method': 'corpus_parser_xml'
            }
```

**Duplicate Method Elimination:**
- **REMOVE** UVI method `validate_corpus_schemas()` (lines 1887-1954) - replace with CorpusParser integration
- **REMOVE** UVI method `validate_xml_corpus()` (lines 1956-1982) - replace with CorpusParser XML validation
- **REMOVE** UVI methods: `_validate_xml_corpus_files()`, `_validate_json_corpus_files()`, `_validate_csv_corpus_files()`, `_validate_wordnet_files()`
- **USE** CorpusParser's `@error_handler` decorators for automatic validation during parsing
- **USE** CorpusParser's built-in statistics tracking (`error_files`, `parsed_files`) for validation metrics
- Constructor: `self.validation_manager = ValidationManager(self)`

### 6. ExportManager (Enhanced with CorpusCollectionAnalyzer Integration)
**Purpose:** Data export with comprehensive analytics metadata via CorpusCollectionAnalyzer
**Methods:**
- `export_resources(include_resources, format, output_path)` - **ENHANCED UVI lines 2043-2106** with collection statistics and build metadata
- `export_cross_corpus_mappings()` - **ENHANCED UVI lines 2107-2137** with mapping coverage analysis and validation status
- `export_semantic_profile(lemma, format)` - **ENHANCED UVI lines 2139-2174** with profile completeness scoring and collection context
- `export_collection_analytics(collection_types, format, output_path)` - **NEW** - Export CorpusCollectionAnalyzer statistics
- `export_build_metadata(format, output_path)` - **NEW** - Export build and load metadata
- `export_corpus_health_report(format, output_path)` - **NEW** - Export comprehensive corpus health analysis
- `_dict_to_xml(data, root_tag)` - XML formatting
- `_dict_to_csv(data)` - CSV formatting  
- `_flatten_profile_to_csv(profile, lemma)` - Profile CSV formatting
- `_enrich_export_with_analytics(export_data, export_type)` - **NEW** - Add analytics metadata to exports

**Constructor Integration:**
```python
class ExportManager(BaseHelper):
    def __init__(self, uvi_instance):
        super().__init__(uvi_instance)
        self.analytics = CorpusCollectionAnalyzer(
            loaded_data=uvi_instance.corpora_data,
            load_status=uvi_instance.corpus_loader.load_status,
            build_metadata=uvi_instance.corpus_loader.build_metadata,
            reference_collections=uvi_instance.corpus_loader.reference_collections,
            corpus_paths=uvi_instance.corpus_paths
        )
```

**UVI Code Enhancement:**
- **ENHANCE 64 lines**: export_resources() method (lines 2043-2106) with collection statistics
- **ENHANCE 31 lines**: export_cross_corpus_mappings() (lines 2107-2137) with validation metrics
- **ENHANCE 36 lines**: export_semantic_profile() (lines 2139-2174) with completeness analysis
- **TOTAL: 131 lines of export functionality enhanced with comprehensive CorpusCollectionAnalyzer metadata**

**CorpusCollectionAnalyzer Integration for Enhanced Export Metadata:**
```python
class ExportManager(BaseHelper):
    def __init__(self, uvi_instance):
        super().__init__(uvi_instance)
        # Access to CorpusCollectionAnalyzer for comprehensive export metadata
        self.analytics = CorpusCollectionAnalyzer(
            uvi_instance.corpora_data,
            uvi_instance.corpus_loader.load_status,
            uvi_instance.corpus_loader.build_metadata,
            uvi_instance.corpus_loader.reference_collections,
            uvi_instance.corpus_paths
        )
        
    def export_resources(self, include_resources: Optional[List[str]] = None, 
                        format: str = 'json', include_mappings: bool = True) -> str:
        """Enhanced export with CorpusCollectionAnalyzer metadata integration."""
        # Default to all loaded resources if none specified
        if include_resources is None:
            include_resources = list(self.uvi.loaded_corpora)
        
        # Get comprehensive metadata from CorpusCollectionAnalyzer
        build_metadata = self.analytics.get_build_metadata()
        collection_stats = self.analytics.get_collection_statistics()
        
        export_data = {
            'export_metadata': {
                'format': format,
                'include_mappings': include_mappings,
                'export_timestamp': build_metadata['timestamp'],
                'included_resources': include_resources,
                'corpus_build_metadata': build_metadata['build_metadata'],
                'corpus_load_status': build_metadata['load_status'],
                'corpus_paths': build_metadata['corpus_paths'],
                'collection_statistics': {
                    resource: collection_stats.get(resource, {})
                    for resource in include_resources
                },
                'export_summary': {
                    'total_resources': len(include_resources),
                    'total_loaded_corpora': len(self.uvi.loaded_corpora),
                    'export_completeness': len(include_resources) / len(self.uvi.loaded_corpora) * 100
                }
            },
            'resources': {}
        }
        
        # Export each requested resource with enhanced metadata
        for resource in include_resources:
            full_name = self._get_full_corpus_name(resource)
            if full_name in self.uvi.corpora_data:
                resource_data = self.uvi.corpora_data[full_name].copy()
                
                # Add CorpusCollectionAnalyzer statistics to each resource
                resource_stats = collection_stats.get(full_name, {})
                if resource_stats:
                    resource_data['analytics_metadata'] = resource_stats
                
                # Add cross-corpus mappings if requested
                if include_mappings:
                    mappings = self._extract_resource_mappings(full_name)
                    if mappings:
                        resource_data['cross_corpus_mappings'] = mappings
                
                export_data['resources'][resource] = resource_data
        
        # Format export according to requested format
        if format == 'json':
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        elif format == 'xml':
            return self._dict_to_xml(export_data, 'uvi_export')
        elif format == 'csv':
            return self._dict_to_csv_with_analytics(export_data)
        else:
            return json.dumps(export_data, indent=2, ensure_ascii=False)
            
    def export_cross_corpus_mappings(self) -> Dict[str, Any]:
        """Enhanced cross-corpus mappings with analytics metadata."""
        build_metadata = self.analytics.get_build_metadata()
        collection_stats = self.analytics.get_collection_statistics()
        
        mappings_data = {
            'export_metadata': {
                'export_type': 'cross_corpus_mappings',
                'export_timestamp': build_metadata['timestamp'],
                'corpus_collection_statistics': collection_stats,
                'mapping_coverage': self._calculate_mapping_coverage(collection_stats)
            },
            'mappings': self._extract_all_cross_corpus_mappings()
        }
        
        return mappings_data
        
    def export_semantic_profile(self, lemma: str, format: str = 'json') -> str:
        """Enhanced semantic profile export with comprehensive analytics."""
        profile = self._build_complete_semantic_profile(lemma)
        
        # Get analytics context for the semantic profile
        build_metadata = self.analytics.get_build_metadata()
        collection_stats = self.analytics.get_collection_statistics()
        
        export_data = {
            'export_metadata': {
                'export_type': 'semantic_profile',
                'target_lemma': lemma,
                'export_timestamp': build_metadata['timestamp'],
                'corpus_coverage': {
                    corpus: profile.get(corpus, {}) is not None
                    for corpus in collection_stats.keys()
                    if corpus != 'reference_collections'
                },
                'collection_sizes': collection_stats,
                'profile_completeness': self._calculate_profile_completeness(profile, collection_stats)
            },
            'semantic_profile': profile
        }
        
        if format == 'json':
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        elif format == 'xml':
            return self._dict_to_xml(export_data, 'semantic_profile_export')
        elif format == 'csv':
            return self._flatten_profile_to_csv_with_analytics(export_data, lemma)
        else:
            return json.dumps(export_data, indent=2, ensure_ascii=False)
            
    def _calculate_mapping_coverage(self, collection_stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate cross-corpus mapping coverage percentages."""
        coverage = {}
        total_mappings = 0
        
        for corpus, stats in collection_stats.items():
            if corpus == 'reference_collections':
                continue
                
            # Count mappings for this corpus
            corpus_mappings = self._count_corpus_mappings(corpus)
            total_items = self._get_total_corpus_items(corpus, stats)
            
            if total_items > 0:
                coverage[corpus] = (corpus_mappings / total_items) * 100
                total_mappings += corpus_mappings
        
        coverage['overall'] = total_mappings
        return coverage
        
    def _calculate_profile_completeness(self, profile: Dict[str, Any], 
                                      collection_stats: Dict[str, Any]) -> Dict[str, float]:
        """Calculate completeness percentage of semantic profile across corpora."""
        completeness = {}
        
        for corpus in collection_stats.keys():
            if corpus == 'reference_collections':
                continue
                
            corpus_profile = profile.get(corpus, {})
            if corpus_profile:
                # Score based on depth and breadth of profile data
                completeness[corpus] = self._score_profile_depth(corpus_profile)
            else:
                completeness[corpus] = 0.0
        
        # Overall completeness as average
        if completeness:
            completeness['overall'] = sum(completeness.values()) / len(completeness)
        
        return completeness
```

**UVI Method Replacements with CorpusCollectionAnalyzer:**
- **ENHANCE** UVI method `export_resources()` (lines 2043-2105) with CorpusCollectionAnalyzer metadata
- **ENHANCE** UVI method `export_cross_corpus_mappings()` (lines 2107-2137) with analytics integration
- **ENHANCE** UVI method `export_semantic_profile()` (lines 2139-2172) with collection statistics
- **Constructor Changes:**
  ```python
  def __init__(self, uvi_instance):
      super().__init__(uvi_instance)
      # Initialize CorpusCollectionAnalyzer for comprehensive export metadata
      self.analytics = CorpusCollectionAnalyzer(
          uvi_instance.corpora_data,
          uvi_instance.corpus_loader.load_status,
          uvi_instance.corpus_loader.build_metadata,
          uvi_instance.corpus_loader.reference_collections,
          uvi_instance.corpus_paths
      )
  ```

### 7. AnalyticsManager
**Purpose:** Centralized analytics and corpus collection information management
**Methods:**
- `get_corpus_info()` - Comprehensive corpus information with analytics
- `get_collection_statistics()` - Collection-wide statistics and metrics
- `get_build_metadata()` - Build and load metadata information
- `analyze_corpus_coverage(lemma)` - Analyze lemma coverage across corpora
- `generate_analytics_report()` - Comprehensive analytics report
- `compare_collection_sizes()` - Compare sizes across different collections
- `track_collection_growth()` - Track collection growth over time

**CorpusCollectionAnalyzer Integration for Centralized Analytics:**
```python
class AnalyticsManager(BaseHelper):
    def __init__(self, uvi_instance):
        super().__init__(uvi_instance)
        # Direct integration with CorpusCollectionAnalyzer for all analytics operations
        self.analyzer = CorpusCollectionAnalyzer(
            uvi_instance.corpora_data,
            uvi_instance.corpus_loader.load_status,
            uvi_instance.corpus_loader.build_metadata,
            uvi_instance.corpus_loader.reference_collections,
            uvi_instance.corpus_paths
        )
        
    def get_corpus_info(self) -> Dict[str, Dict[str, Any]]:
        """Enhanced corpus info with CorpusCollectionAnalyzer statistics integration."""
        # Get base corpus information
        corpus_info = {}
        for corpus_name in self.uvi.supported_corpora:
            corpus_info[corpus_name] = {
                'path': str(self.uvi.corpus_paths.get(corpus_name, 'Not found')),
                'loaded': corpus_name in self.uvi.loaded_corpora,
                'data_available': corpus_name in self.uvi.corpora_data
            }
        
        # Enhance with CorpusCollectionAnalyzer statistics
        collection_stats = self.analyzer.get_collection_statistics()
        build_metadata = self.analyzer.get_build_metadata()
        
        for corpus_name in corpus_info.keys():
            if corpus_name in collection_stats:
                corpus_info[corpus_name].update({
                    'collection_statistics': collection_stats[corpus_name],
                    'load_status': build_metadata['load_status'].get(corpus_name, 'unknown'),
                    'last_build_time': build_metadata['build_metadata'].get(f'{corpus_name}_last_build', 'unknown')
                })
                
                # Add corpus-specific metrics
                if corpus_name == 'verbnet' and 'classes' in collection_stats[corpus_name]:
                    corpus_info[corpus_name]['metrics'] = {
                        'total_classes': collection_stats[corpus_name]['classes'],
                        'total_members': collection_stats[corpus_name].get('members', 0),
                        'average_members_per_class': self._calculate_average_members_per_class(corpus_name)
                    }
                elif corpus_name == 'framenet' and 'frames' in collection_stats[corpus_name]:
                    corpus_info[corpus_name]['metrics'] = {
                        'total_frames': collection_stats[corpus_name]['frames'],
                        'total_lexical_units': collection_stats[corpus_name].get('lexical_units', 0),
                        'average_units_per_frame': self._calculate_average_units_per_frame(corpus_name)
                    }
                elif corpus_name == 'propbank' and 'predicates' in collection_stats[corpus_name]:
                    corpus_info[corpus_name]['metrics'] = {
                        'total_predicates': collection_stats[corpus_name]['predicates'],
                        'total_rolesets': collection_stats[corpus_name].get('rolesets', 0),
                        'average_rolesets_per_predicate': self._calculate_average_rolesets_per_predicate(corpus_name)
                    }
        
        # Add overall collection summary
        corpus_info['_collection_summary'] = {
            'total_supported_corpora': len(self.uvi.supported_corpora),
            'total_loaded_corpora': len(self.uvi.loaded_corpora),
            'load_completion_percentage': len(self.uvi.loaded_corpora) / len(self.uvi.supported_corpora) * 100,
            'reference_collections': collection_stats.get('reference_collections', {}),
            'total_collection_items': sum(
                self.analyzer._get_collection_size(stats) 
                for stats in collection_stats.values() 
                if isinstance(stats, dict)
            )
        }
        
        return corpus_info
        
    def get_collection_statistics(self) -> Dict[str, Any]:
        """Delegate to CorpusCollectionAnalyzer with additional context."""
        base_stats = self.analyzer.get_collection_statistics()
        
        # Add contextual information
        enhanced_stats = {
            **base_stats,
            'statistics_metadata': {
                'generated_at': self.analyzer.get_build_metadata()['timestamp'],
                'analysis_version': '1.0',
                'total_collections_analyzed': len([k for k in base_stats.keys() if k != 'reference_collections'])
            }
        }
        
        return enhanced_stats
        
    def get_build_metadata(self) -> Dict[str, Any]:
        """Enhanced build metadata with additional analytics context."""
        base_metadata = self.analyzer.get_build_metadata()
        
        # Add analytics-specific metadata
        enhanced_metadata = {
            **base_metadata,
            'analytics_context': {
                'available_analytics_methods': [
                    'get_corpus_info', 'get_collection_statistics', 'analyze_corpus_coverage',
                    'generate_analytics_report', 'compare_collection_sizes', 'track_collection_growth'
                ],
                'supported_corpus_types': list(self.analyzer._CORPUS_COLLECTION_FIELDS.keys()),
                'analysis_capabilities': {
                    'collection_size_calculation': True,
                    'corpus_statistics_extraction': True,
                    'build_metadata_tracking': True,
                    'reference_collection_analysis': True,
                    'error_handling': True
                }
            }
        }
        
        return enhanced_metadata
        
    def analyze_corpus_coverage(self, lemma: str) -> Dict[str, Any]:
        """Analyze lemma coverage across all corpora using CorpusCollectionAnalyzer context."""
        coverage_analysis = {
            'target_lemma': lemma,
            'analysis_timestamp': self.analyzer.get_build_metadata()['timestamp'],
            'corpus_coverage': {},
            'coverage_summary': {}
        }
        
        collection_stats = self.analyzer.get_collection_statistics()
        
        for corpus_name in self.uvi.loaded_corpora:
            if corpus_name in self.uvi.corpora_data:
                # Check lemma presence in corpus
                lemma_found = self._check_lemma_in_corpus(lemma, corpus_name)
                corpus_stats = collection_stats.get(corpus_name, {})
                
                coverage_analysis['corpus_coverage'][corpus_name] = {
                    'lemma_present': lemma_found,
                    'corpus_size': self.analyzer._get_collection_size(corpus_stats),
                    'corpus_statistics': corpus_stats
                }
        
        # Calculate overall coverage summary
        total_corpora = len(coverage_analysis['corpus_coverage'])
        corpora_with_lemma = sum(1 for info in coverage_analysis['corpus_coverage'].values() if info['lemma_present'])
        
        coverage_analysis['coverage_summary'] = {
            'total_corpora_checked': total_corpora,
            'corpora_containing_lemma': corpora_with_lemma,
            'coverage_percentage': (corpora_with_lemma / total_corpora * 100) if total_corpora > 0 else 0,
            'collection_context': collection_stats
        }
        
        return coverage_analysis
        
    def generate_analytics_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report using CorpusCollectionAnalyzer."""
        collection_stats = self.analyzer.get_collection_statistics()
        build_metadata = self.analyzer.get_build_metadata()
        
        return {
            'report_metadata': {
                'generated_at': build_metadata['timestamp'],
                'report_type': 'comprehensive_analytics',
                'analyzer_version': 'CorpusCollectionAnalyzer 1.0'
            },
            'collection_statistics': collection_stats,
            'build_and_load_metadata': build_metadata,
            'corpus_health_analysis': self._analyze_corpus_health(collection_stats),
            'collection_size_comparisons': self._compare_collection_sizes(collection_stats),
            'reference_collection_analysis': self._analyze_reference_collections(collection_stats),
            'recommendations': self._generate_analytics_recommendations(collection_stats, build_metadata)
        }
```

**UVI Method Replacements with CorpusCollectionAnalyzer:**
- **REPLACE** UVI method `get_corpus_info()` (lines 178-192) with CorpusCollectionAnalyzer-enhanced analytics
- **ADD** centralized analytics capabilities not available in base UVI
- **ELIMINATE** duplicate statistics calculation scattered across UVI methods
- **Constructor Integration:**
  ```python
  def __init__(self, uvi_instance):
      super().__init__(uvi_instance)
      # Direct CorpusCollectionAnalyzer integration for all analytics
      self.analyzer = CorpusCollectionAnalyzer(
          uvi_instance.corpora_data,
          uvi_instance.corpus_loader.load_status,
          uvi_instance.corpus_loader.build_metadata,
          uvi_instance.corpus_loader.reference_collections,
          uvi_instance.corpus_paths
      )
  ```

### 8. ParsingEngine
**Purpose:** Centralized parsing operations using CorpusParser
**Methods:**
- `parse_corpus_files(corpus_name)` - Parse all files for a specific corpus
- `parse_all_corpora()` - Parse all available corpora
- `reparse_corpus(corpus_name)` - Re-parse specific corpus with fresh data
- `get_parsing_statistics()` - Get parsing statistics across all corpora
- `validate_parsed_data(corpus_name)` - Validate parsed corpus data
- `_setup_parser()` - Initialize CorpusParser with paths and logger
- `_handle_parsing_errors(corpus_name, error_info)` - Handle parsing errors

**CorpusParser Integration:**
```python
class ParsingEngine(BaseHelper):
    def __init__(self, uvi_instance):
        super().__init__(uvi_instance)
        self.corpus_parser = uvi_instance.corpus_parser
        self.parsing_cache = {}
        
    def parse_corpus_files(self, corpus_name):
        """Parse all files for specific corpus using CorpusParser."""
        if corpus_name in self.parsing_cache:
            return self.parsing_cache[corpus_name]
            
        parser_methods = {
            'verbnet': self.corpus_parser.parse_verbnet_files,
            'framenet': self.corpus_parser.parse_framenet_files,
            'propbank': self.corpus_parser.parse_propbank_files,
            'ontonotes': self.corpus_parser.parse_ontonotes_files,
            'wordnet': self.corpus_parser.parse_wordnet_files,
            'bso': self.corpus_parser.parse_bso_mappings,
            'semnet': self.corpus_parser.parse_semnet_data,
            'reference_docs': self.corpus_parser.parse_reference_docs,
            'vn_api': self.corpus_parser.parse_vn_api_files
        }
        
        if corpus_name not in parser_methods:
            raise ValueError(f"No parser method for corpus: {corpus_name}")
            
        try:
            parsed_data = parser_methods[corpus_name]()
            self.parsing_cache[corpus_name] = parsed_data
            self.uvi.corpora_data[corpus_name] = parsed_data
            self.uvi.loaded_corpora.add(corpus_name)
            return parsed_data
        except Exception as e:
            error_info = {
                'corpus': corpus_name,
                'error': str(e),
                'method': parser_methods[corpus_name].__name__
            }
            return self._handle_parsing_errors(corpus_name, error_info)
            
    def parse_all_corpora(self):
        """Parse all available corpora using CorpusParser methods."""
        results = {}
        for corpus_name in self.uvi.supported_corpora:
            if corpus_name in self.uvi.corpus_paths:
                try:
                    results[corpus_name] = self.parse_corpus_files(corpus_name)
                except Exception as e:
                    results[corpus_name] = {'error': str(e)}
        return results
        
    def get_parsing_statistics(self):
        """Get comprehensive parsing statistics from CorpusParser results."""
        stats = {
            'total_corpora': len(self.uvi.supported_corpora),
            'parsed_corpora': len(self.uvi.loaded_corpora),
            'failed_corpora': 0,
            'corpus_details': {}
        }
        
        for corpus_name in self.uvi.loaded_corpora:
            if corpus_name in self.uvi.corpora_data:
                corpus_stats = self.uvi.corpora_data[corpus_name].get('statistics', {})
                stats['corpus_details'][corpus_name] = corpus_stats
                
        stats['failed_corpora'] = stats['total_corpora'] - stats['parsed_corpora']
        return stats
```

**UVI Integration Changes - ParsingEngine Centralization:**
- **CENTRALIZE** all UVI parsing methods into ParsingEngine helper
- **REMOVE** UVI duplicate parsing methods: `_load_verbnet()`, `_parse_verbnet_class()`, `_build_class_hierarchy()`
- **REPLACE** UVI corpus loading with ParsingEngine delegation:
  ```python
  def _load_corpus(self, corpus_name):
      """Delegate to ParsingEngine instead of duplicate parsing."""
      return self.parsing_engine.parse_corpus_files(corpus_name)
      
  def _load_all_corpora(self):
      """Delegate to ParsingEngine for all corpus loading."""
      return self.parsing_engine.parse_all_corpora()
  ```
- **Constructor Integration:**
  ```python
  def __init__(self, corpora_path='corpora/', load_all=True):
      # Initialize CorpusParser with paths and logger
      self.corpus_parser = CorpusParser(self._get_corpus_paths(corpora_path), 
                                       self._get_logger())
      
      # Initialize ParsingEngine to handle all parsing operations
      self.parsing_engine = ParsingEngine(self)
      
      if load_all:
          self.parsing_engine.parse_all_corpora()
  ```

### 8. HierarchyNavigator
**Purpose:** Class hierarchy and structural navigation
**Methods:**
- `get_class_hierarchy_by_name()` - Name-based hierarchy
- `get_class_hierarchy_by_id()` - ID-based hierarchy
- `get_subclass_ids(parent_class_id)` - Subclass identification
- `get_full_class_hierarchy(class_id)` - Complete hierarchy tree
- `get_top_parent_id(class_id)` - Root parent identification
- `get_member_classes(member_name)` - Member class lookup
- `_build_class_hierarchy(class_id, verbnet_data)` - Hierarchy construction

**Constructor Integration:**
```python
class AnalyticsManager(BaseHelper):
    def __init__(self, uvi_instance):
        super().__init__(uvi_instance)
        self.collection_analyzer = CorpusCollectionAnalyzer(
            loaded_data=uvi_instance.corpora_data,
            load_status=uvi_instance.corpus_loader.load_status,
            build_metadata=uvi_instance.corpus_loader.build_metadata,
            reference_collections=uvi_instance.corpus_loader.reference_collections,
            corpus_paths=uvi_instance.corpus_paths
        )
```

**UVI Integration:**
- **ENHANCE**: get_corpus_info() method with comprehensive CorpusCollectionAnalyzer statistics
- **EXPOSE**: Previously hidden CorpusCollectionAnalyzer capabilities through public UVI interface
- **CENTRALIZE**: All analytics operations through AnalyticsManager
- **ELIMINATE**: Scattered statistics calculations throughout UVI methods

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

**Enhanced Helper Integration with CorpusLoader Components:**
- `self.corpus_parser = CorpusParser(corpus_paths, logger)`
- `self.parsing_engine = ParsingEngine(self)`
- `self.analytics_manager = AnalyticsManager(self)` - **NEW**
- `self.search_engine = SearchEngine(self)`
- `self.corpus_retriever = CorpusRetriever(self)`
- `self.cross_reference_manager = CrossReferenceManager(self)`
- `self.reference_data_provider = ReferenceDataProvider(self)`
- `self.validation_manager = ValidationManager(self)`
- `self.export_manager = ExportManager(self)`
- `self.hierarchy_navigator = HierarchyNavigator(self)`

### Method Delegation Pattern with CorpusParser
**Public Interface Preservation:**
```python
def search_lemmas(self, *args, **kwargs):
    return self.search_engine.search_lemmas(*args, **kwargs)

def get_verbnet_class(self, *args, **kwargs):
    return self.corpus_retriever.get_verbnet_class(*args, **kwargs)

def validate_corpus_schemas(self, *args, **kwargs):
    return self.validation_manager.validate_corpus_schemas(*args, **kwargs)

# New parsing-specific methods
def parse_corpus_files(self, *args, **kwargs):
    return self.parsing_engine.parse_corpus_files(*args, **kwargs)

def get_parsing_statistics(self):
    return self.parsing_engine.get_parsing_statistics()
```

### Shared Dependencies with CorpusParser
**Helper Class Constructor:**
```python
class BaseHelper:
    def __init__(self, uvi_instance):
        self.uvi = uvi_instance
        self.corpora_data = uvi_instance.corpora_data
        self.loaded_corpora = uvi_instance.loaded_corpora
        self.corpus_loader = uvi_instance.corpus_loader
        self.corpus_parser = uvi_instance.corpus_parser  # Access to CorpusParser
        self.logger = uvi_instance.logger
```

## CorpusLoader Integration Architecture

### Core Principle: Eliminate Duplication
The CorpusLoader package already provides comprehensive functionality that UVI duplicates:

**CorpusLoader Capabilities:**
- `load_corpus(corpus_name)` - Individual corpus loading
- `load_all_corpora()` - Batch corpus loading  
- `build_reference_collections()` - Reference data building
- `validate_collections()` - Collection validation
- `validate_cross_references()` - Cross-reference validation
- `get_collection_statistics()` - Data analysis

**UVI Duplicate Methods to Replace:**
- Lines 1459-1500: `get_references()` → Use `corpus_loader.reference_collections` 
- Lines 1502-1563: `get_themrole_references()` → Use `corpus_loader.reference_collections['themroles']`
- Lines 1565-1626: `get_predicate_references()` → Use `corpus_loader.reference_collections['predicates']`
- Lines 1887-1954: `validate_corpus_schemas()` → Use `corpus_loader.validate_collections()`
- Lines 1956-1979: `validate_xml_corpus()` → Use `corpus_loader.validator.validate_xml_corpus()`

### Integration Methodology

**Phase 1: Constructor Modifications**
```python
class UVI:
    def __init__(self, corpora_path='corpora/', load_all=True):
        # Initialize CorpusLoader first
        self.corpus_loader = CorpusLoader(corpora_path)
        
        # Use CorpusLoader data instead of separate storage
        self.corpora_data = self.corpus_loader.loaded_data  # Direct reference
        self.loaded_corpora = set(self.corpus_loader.load_status.keys())
        self.corpus_paths = self.corpus_loader.corpus_paths
        
        # Load corpora via CorpusLoader
        if load_all:
            self.corpus_loader.load_all_corpora()
            self._update_loaded_corpora_set()
```

**Phase 2: Method Delegation Pattern**
```python
def get_references(self):
    """Delegate to CorpusLoader reference collections."""
    return self.reference_data_provider.get_references()
    
def validate_corpus_schemas(self, corpus_names=None):
    """Delegate to ValidationManager using CorpusLoader."""
    return self.validation_manager.validate_corpus_schemas(corpus_names)
    
def get_verbnet_class(self, class_id, include_subclasses=True, include_mappings=True):
    """Delegate to CorpusRetriever using CorpusLoader data."""
    return self.corpus_retriever.get_verbnet_class(class_id, include_subclasses, include_mappings)
```

**Phase 3: Internal Method Updates**
```python  
# Replace direct data access with CorpusLoader data
# OLD: self.corpora_data['verbnet'] = parsed_data
# NEW: self.corpora_data = self.corpus_loader.loaded_data  # Direct reference

# Replace manual reference building with CorpusLoader
# OLD: Manual parsing and collection building  
# NEW: self.corpus_loader.build_reference_collections()
```

## CorpusCollectionAnalyzer Integration Summary

### Overall Strategy: Eliminate Analytics/Statistics Duplication

The CorpusCollectionAnalyzer class provides specialized functionality for analyzing corpus collection data that UVI currently duplicates across multiple methods. This integration eliminates duplication while centralizing and optimizing analytics operations.

**Key Analytics Method Replacements:**
- **SearchEngine**: Replace 3 UVI statistics methods (`_calculate_search_statistics`, `_calculate_pattern_statistics`, `_calculate_attribute_statistics`)
- **ExportManager**: Enhance 3 UVI export methods with comprehensive metadata from CorpusCollectionAnalyzer
- **AnalyticsManager**: Replace UVI `get_corpus_info` method and add centralized analytics capabilities

### Specific CorpusCollectionAnalyzer Method Utilizations

**Primary Analytics Methods:**
- `get_collection_statistics()` → Replaces manual collection size calculations in UVI methods
- `get_build_metadata()` → Replaces scattered build metadata access across UVI export methods
- `_get_collection_size()` → Standardizes collection size calculation across all helper classes
- `_build_corpus_statistics()` → Provides consistent corpus statistics format
- `_get_corpus_statistics_with_error_handling()` → Adds robust error handling for statistics

**Template Method Advantages:**
- `_build_reference_collection_statistics()` → Standardized reference collection analysis
- `_calculate_collection_sizes()` → Optimized collection size calculation using field mappings
- `_CORPUS_COLLECTION_FIELDS` → Centralized field mappings for VerbNet, FrameNet, PropBank

### Helper Class Integration Points

**SearchEngine (Statistics Enhancement):**
```python
# Constructor integration:
self.analytics = CorpusCollectionAnalyzer(uvi_instance.corpora_data, ...)

# Method replacements:
def _calculate_search_statistics(self, matches): 
    return enhanced_stats_with_collection_context()
def _calculate_pattern_statistics(self, matches, pattern_type): 
    return pattern_stats_with_collection_sizes()
def _calculate_attribute_statistics(self, matches, attribute_type): 
    return attribute_stats_with_build_metadata()
```

**ExportManager (Metadata Enhancement):**
```python
# Enhanced export methods with CorpusCollectionAnalyzer metadata:
def export_resources(self): return export_with_collection_statistics()
def export_cross_corpus_mappings(self): return mappings_with_analytics_metadata()
def export_semantic_profile(self): return profile_with_completeness_analysis()
```

**AnalyticsManager (Centralized Analytics):**
```python
# Direct CorpusCollectionAnalyzer delegation:
self.analyzer = CorpusCollectionAnalyzer(...)
def get_corpus_info(self): return analyzer_enhanced_corpus_info()
def get_collection_statistics(self): return analyzer.get_collection_statistics()
def generate_analytics_report(self): return comprehensive_report_with_analyzer()
```

### Integration Implementation Plan

**Phase 1: CorpusCollectionAnalyzer Integration**
```python
class UVI:
    def __init__(self, corpora_path='corpora/', load_all=True):
        # Step 1: Initialize corpus loader first
        self.corpus_loader = CorpusLoader(corpora_path)
        
        # Step 2: Initialize helpers with CorpusCollectionAnalyzer access
        self.search_engine = SearchEngine(self)        # Analytics-enhanced search
        self.export_manager = ExportManager(self)      # Analytics-enhanced export
        self.analytics_manager = AnalyticsManager(self) # Centralized analytics
```

**Phase 2: Method Replacement**
```python
# OLD UVI analytics methods (REMOVE):
def _calculate_search_statistics(self, matches):        # Lines 4247-4260
def _calculate_pattern_statistics(self, matches, type): # Lines 4444-4458  
def _calculate_attribute_statistics(self, matches, type): # Lines 4575-4589
def get_corpus_info(self):                             # Lines 178-192

# NEW delegation methods (ADD):
def _calculate_search_statistics(self, matches):
    return self.search_engine._calculate_search_statistics(matches)
def get_corpus_info(self):
    return self.analytics_manager.get_corpus_info()
```

**Phase 3: Analytics Enhancement**
```python
# Enhanced capabilities not available in original UVI:
def analyze_corpus_coverage(self, lemma):
    return self.analytics_manager.analyze_corpus_coverage(lemma)
def generate_analytics_report(self):
    return self.analytics_manager.generate_analytics_report()
def get_enhanced_collection_statistics(self):
    return self.analytics_manager.get_collection_statistics()
```

## Implementation Strategy

### Phase 1: Infrastructure
- Create `BaseHelper` abstract class with CorpusLoader integration
- Create empty helper class files with CorpusLoader-aware constructors
- Add helper instantiation to UVI.__init__() after CorpusLoader initialization

### Phase 2: CorpusCollectionAnalyzer Integration (Priority Order)
1. **AnalyticsManager** - Create centralized analytics hub with CorpusCollectionAnalyzer
2. **SearchEngine** - Replace UVI statistics methods with analytics-enhanced versions
3. **ExportManager** - Enhance export methods with comprehensive metadata
4. **ReferenceDataProvider** - Remove UVI duplicate reference methods
5. **ValidationManager** - Remove UVI duplicate validation methods  
6. **CorpusRetriever** - Update UVI retrieval methods to use CorpusLoader data

### Phase 3: Method Migration (by helper class)
- Move methods from UVI to appropriate helper classes
- Add delegation methods to UVI for backward compatibility
- Update internal method calls to use helper instances

### Phase 4: Optimization
- Remove delegation methods after confirming functionality
- Optimize cross-helper communication  
- Add helper-specific optimizations

### Phase 5: Testing & Documentation
- Update test files to reflect new architecture
- Update documentation and examples
- Performance benchmarking

## Specific Method Elimination Plan

### UVI Methods to Remove/Replace with CorpusLoader Integration

**ReferenceDataProvider Elimination:**
```python
# REMOVE these UVI methods entirely (lines 1459-1626):
def get_references(self) -> Dict[str, Any]              # Lines 1459-1500
def get_themrole_references(self) -> List[Dict]         # Lines 1502-1563  
def get_predicate_references(self) -> List[Dict]        # Lines 1565-1626
def get_verb_specific_features(self) -> List[str]       # Lines 1628-1662
def get_syntactic_restrictions(self) -> List[str]       # Lines 1664-1704
def get_selectional_restrictions(self) -> List[str]     # Lines 1706-1748

# REPLACE with delegation:
def get_references(self):
    return self.reference_data_provider.get_references()
```

**ValidationManager Elimination:**
```python
# REMOVE these UVI methods entirely (lines 1887-1979):
def validate_corpus_schemas(self, corpus_names=None)    # Lines 1887-1954
def validate_xml_corpus(self, corpus_name)              # Lines 1956-1979

# REPLACE with delegation:
def validate_corpus_schemas(self, corpus_names=None):
    return self.validation_manager.validate_corpus_schemas(corpus_names)
```

**CorpusRetriever Integration:**
```python
# UPDATE these UVI methods to use CorpusLoader data:
def get_verbnet_class(self, class_id, ...)             # Lines 545-613
def get_framenet_frame(self, frame_name, ...)          # Lines 615-693  
def get_propbank_frame(self, lemma, ...)               # Lines 695-766

# Change from: direct corpora_data access
# To: self.corpus_loader.loaded_data access
# Maintain existing logic, just change data source
```

## CorpusCollectionBuilder Integration Summary

### Overall Strategy: Eliminate Collection Building Duplication

The CorpusCollectionBuilder class (292 lines) provides specialized functionality for building reference collections that UVI currently duplicates across multiple methods (304+ lines total). This integration eliminates duplication while centralizing and optimizing collection building operations.

### Specific CorpusCollectionBuilder Method Utilizations

**Primary Collection Building Methods:**
- `build_reference_collections()` → Replaces all manual UVI reference building
- `build_predicate_definitions()` → Replaces UVI predicate extraction logic
- `build_themrole_definitions()` → Replaces UVI themrole extraction logic
- `build_verb_specific_features()` → Replaces UVI verb feature extraction
- `build_syntactic_restrictions()` → Replaces UVI syntactic restriction extraction
- `build_selectional_restrictions()` → Replaces UVI selectional restriction extraction

**Template Method Advantages:**
- `_build_from_reference_docs()` → Standardized reference document processing
- `_extract_from_verbnet_classes()` → Optimized VerbNet class iteration
- `_extract_verb_features_from_class()` → Specialized feature extraction
- `_extract_syntactic_restrictions_from_class()` → Specialized restriction extraction
- `_extract_selectional_restrictions_from_class()` → Specialized restriction extraction

### Helper Class Integration Points

**ReferenceDataProvider (Primary Integration):**
```python
# Constructor modification:
self.collection_builder = CorpusCollectionBuilder(uvi_instance.corpora_data, logger)

# Method delegation pattern:
def get_references(self): return self.collection_builder.reference_collections
def get_themrole_references(self): return self._format_themroles()
def get_predicate_references(self): return self._format_predicates()
# ... (all 6 reference methods)
```

**SearchEngine (Enhanced Capabilities):**
```python  
# New search methods leveraging CorpusCollectionBuilder:
def search_by_reference_type(self, reference_type, query, fuzzy_match=False)
def search_by_semantic_pattern(self, pattern_type, pattern_value, target_resources=None)

# Integration pattern:
self.collection_builder = uvi_instance.reference_data_provider.collection_builder
collections = self.collection_builder.reference_collections
```

**ValidationManager (Reference Validation):**
```python
# New validation methods for CorpusCollectionBuilder data:
def validate_reference_collections(self) -> Dict[str, bool]
def check_reference_consistency(self) -> Dict[str, Any]
def _check_themrole_consistency(self) -> Dict[str, Any]

# Integration pattern:
self.collection_builder = uvi_instance.reference_data_provider.collection_builder
build_results = self.collection_builder.build_reference_collections()
```

**CorpusRetriever (Enhanced Retrieval):**
```python
# Enhanced retrieval with reference data enrichment:
def get_verbnet_class(self, class_id, include_subclasses=True, include_mappings=True)

# Integration pattern:
self.collection_builder = uvi_instance.reference_data_provider.collection_builder
class_data['available_themroles'] = self.collection_builder.reference_collections.get('themroles', {}).keys()
```

## CorpusParser Integration Summary

### Duplicate UVI Methods Eliminated by CorpusParser

**VerbNet Parsing Duplication (Lines 3781-3988):**
- `_load_verbnet(verbnet_path)` → Replace with `parsing_engine.parse_corpus_files('verbnet')`
- `_parse_verbnet_class(root)` → Replace with `corpus_parser.parse_verbnet_files()`
- `_build_class_hierarchy(class_id, verbnet_data)` → Use `corpus_parser._build_verbnet_hierarchy()`

**Reference Data Duplication (Lines 1459-1626):**
- `get_references()` → Delegate to `corpus_loader.reference_collections`
- `get_themrole_references()` → Use `corpus_loader.reference_collections['themroles']`
- `get_predicate_references()` → Use `corpus_loader.reference_collections['predicates']`

**Validation Duplication (Lines 1887-1982):**
- `validate_corpus_schemas()` → Use CorpusParser `@error_handler` decorators
- `validate_xml_corpus()` → Use CorpusParser XML parsing with error tracking
- Manual validation helpers → Replace with CorpusParser built-in validation

### Integration Implementation Plan

**Phase 1: CorpusParser Integration**
```python
class UVI:
    def __init__(self, corpora_path='corpora/', load_all=True):
        # Step 1: Initialize CorpusParser with paths and logging
        corpus_paths = self._get_corpus_paths(corpora_path)
        logger = self._setup_logger()
        self.corpus_parser = CorpusParser(corpus_paths, logger)
        
        # Step 2: Initialize ParsingEngine for centralized parsing
        self.parsing_engine = ParsingEngine(self)
        
        # Step 3: Replace direct corpus loading with parser delegation
        if load_all:
            self.parsing_engine.parse_all_corpora()  # Instead of self._load_all_corpora()
```

**Phase 2: Method Replacement**
```python
# OLD UVI parsing methods (REMOVE):
def _load_verbnet(self, verbnet_path):          # Lines 3781-3838
def _parse_verbnet_class(self, root):           # Lines 3840-3958  
def _build_class_hierarchy(self, class_id, data): # Lines 3960-3988

# NEW delegation methods (ADD):
def _load_verbnet(self, verbnet_path):
    """Delegate VerbNet loading to CorpusParser."""
    return self.parsing_engine.parse_corpus_files('verbnet')

def get_verbnet_class(self, class_id, include_subclasses=True, include_mappings=True):
    """Delegate to CorpusRetriever using CorpusParser data."""
    return self.corpus_retriever.get_verbnet_class(class_id, include_subclasses, include_mappings)
```

**Phase 3: Helper Class Integration**
```python
# CorpusRetriever uses CorpusParser-generated data
class CorpusRetriever(BaseHelper):
    def get_verbnet_class(self, class_id, include_subclasses=True, include_mappings=True):
        # Access CorpusParser-generated VerbNet data
        verbnet_data = self.corpus_parser.parse_verbnet_files()
        classes = verbnet_data.get('classes', {})
        return self._format_class_data(classes.get(class_id, {}), include_subclasses, include_mappings)

# ValidationManager uses CorpusParser error handling
class ValidationManager(BaseHelper):
    def validate_corpus_schemas(self, corpus_names=None):
        # Use CorpusParser's @error_handler decorators for validation
        for corpus_name in corpus_names:
            parser_method = getattr(self.corpus_parser, f'parse_{corpus_name}_files')
            validation_result = self._validate_via_parser(parser_method)
            # CorpusParser automatically tracks parsing errors via decorators
        return validation_results

# ParsingEngine centralizes all parsing operations  
class ParsingEngine(BaseHelper):
    def parse_corpus_files(self, corpus_name):
        # Map corpus names to CorpusParser methods
        parser_methods = {
            'verbnet': self.corpus_parser.parse_verbnet_files,
            'framenet': self.corpus_parser.parse_framenet_files,
            'propbank': self.corpus_parser.parse_propbank_files,
            # ... all corpus types
        }
        return parser_methods[corpus_name]()
```

### CorpusParser Method Utilization

**VerbNet Integration:**
- `corpus_parser.parse_verbnet_files()` → Replaces UVI `_load_verbnet()` + `_parse_verbnet_class()`
- `corpus_parser._build_verbnet_hierarchy()` → Replaces UVI `_build_class_hierarchy()`
- `corpus_parser._extract_members()` → Replaces UVI member extraction logic

**FrameNet Integration:**
- `corpus_parser.parse_framenet_files()` → Provides FrameNet data for `get_framenet_frame()`
- `corpus_parser._parse_framenet_frame()` → Handles individual frame parsing
- `corpus_parser._parse_framenet_relations()` → Manages frame relationships

**PropBank Integration:**
- `corpus_parser.parse_propbank_files()` → Provides PropBank data for `get_propbank_frame()`
- `corpus_parser._parse_propbank_frame()` → Handles predicate parsing
- `corpus_parser._index_rolesets()` → Manages roleset indexing

**Universal Corpus Integration:**
- `corpus_parser.parse_ontonotes_files()` → OntoNotes sense inventories
- `corpus_parser.parse_wordnet_files()` → WordNet synsets and indices  
- `corpus_parser.parse_bso_mappings()` → BSO category mappings
- `corpus_parser.parse_semnet_data()` → SemNet semantic networks
- `corpus_parser.parse_reference_docs()` → Reference definitions
- `corpus_parser.parse_vn_api_files()` → VN API enhanced data

### Error Handling & Validation Integration

**CorpusParser Error Handling:**
- `@error_handler` decorators automatically catch and log parsing errors
- Built-in statistics tracking: `error_files`, `parsed_files`, `total_files`
- Graceful degradation: Returns empty dict on parsing failure instead of crashing

**ValidationManager Integration:**
```python
def validate_xml_corpus(self, corpus_name):
    # CorpusParser XML methods automatically validate during parsing
    parsed_data = self.corpus_parser.parse_verbnet_files()  # Example
    statistics = parsed_data.get('statistics', {})
    
    return {
        'valid': statistics.get('error_files', 0) == 0,
        'total_files': statistics.get('total_files', 0),
        'error_files': statistics.get('error_files', 0),
        'validation_method': 'corpus_parser_automatic'
    }
```


## Backward Compatibility
- **Interface preservation:** All existing public methods remain accessible
- **Parameter compatibility:** Method signatures unchanged
- **Return value compatibility:** Output formats preserved
- **Import compatibility:** `from uvi import UVI` continues to work
- **CorpusParser transparency:** Users don't need to know about internal CorpusParser usage