# UVI Package Comprehensive Debugging and Fixing Strategy

## Current Test Status
- **Total tests**: 295
- **Failed**: 47 tests
- **Passed**: 241 tests  
- **Skipped**: 7 tests

## Key Issues Identified

### 1. Import Structure Issues (Critical Priority)
- Tests expect parsers directly from UVI module but they're in separate submodules
- Pattern: `from src.uvi.UVI import VerbNetParser` but VerbNetParser is in `src.uvi.parsers.verbnet_parser`
- Mock/patch statements reference non-existent module paths

### 2. Constructor/API Mismatch (Critical Priority)
- `CrossReferenceManager.__init__()` takes 1 argument but tests pass 2
- Tests assume different API than implemented

### 3. XML Namespace Issues (High Priority)
- FrameNet parser: "Unexpected root element {http://framenet.icsi.berkeley.edu}frame"
- XML parsing doesn't handle namespaces properly

### 4. Placeholder Tests (Medium Priority)
- Many methods end with "_placeholder" - intentionally unimplemented
- Need triage: implement, defer, or remove

### 5. Mock/Patch Structure Issues (Medium Priority)
- Mocks expect different module structure than exists
- Tests failing on AttributeError for missing attributes

## Refined Debugging Strategy

### Phase 0: Diagnostic Deep Dive (NEW - Critical Foundation)

#### 0.1 Failure Pattern Analysis
```bash
# Categorize all 47 failures by error type
pytest --tb=line > failure_analysis.txt
# Create failure_categories.txt with groupings:
# - Import errors
# - Constructor mismatches  
# - XML namespace issues
# - Placeholder tests
# - Mock/patch issues
```

#### 0.2 Module Architecture Audit  
- Map expected vs actual import paths
- Create visual diagram of current vs expected module structure
- Document all discrepancies between test expectations and implementation

#### 0.3 Test Coverage Gap Analysis
- Identify what functionality exists vs what's tested
- Distinguish between broken tests vs missing functionality
- Create priority matrix for fixes

### Phase 1: Structural Foundation (Critical Priority)

#### 1.1 Fix Module Exposure
- Update all `__init__.py` files to properly export classes
- Ensure `src/uvi/__init__.py` exposes parsers if backward compatibility needed
- Standardize import patterns across entire codebase
- Create import verification tests to prevent future regressions

#### 1.2 Constructor/API Alignment
- Review all class constructors vs test expectations  
- **Decision point**: Update constructors to match tests OR update tests to match implementation
- Document API decisions for consistency
- Update docstrings to match actual implementation

#### 1.3 Import Stability Tests
```python
def test_import_stability():
    """Ensure all expected imports work."""
    from src.uvi.parsers.verbnet_parser import VerbNetParser
    from src.uvi.parsers.framenet_parser import FrameNetParser
    # etc. - Add for all expected imports
```

### Phase 2: Implementation Triage (High Priority)

#### 2.1 Placeholder Test Categorization  
- **Audit each placeholder**: Mark as "implement", "defer", or "remove"
- **Focus scope**: Core UVI functionality only
- **Remove tests** for features not in MVP scope
- **Prioritize by**: User impact and implementation complexity

#### 2.2 XML Namespace Handling Strategy
- Create base parser class with namespace-aware XML parsing
- Update all XML parsers (FrameNet, PropBank, VerbNet) to handle namespaced elements
- Use namespace mapping dictionaries in parsers
- Test with real corpus XML files to validate

#### 2.3 Missing Functionality Implementation
- Implement only categorized "implement" features from placeholder audit
- Focus on core UVI operations: loading, parsing, cross-referencing
- Defer advanced features to future releases

### Phase 3: Testing Infrastructure Hardening (Medium Priority)

#### 3.1 Mock/Patch Systematic Fix
- Update all mock/patch references to correct module paths
- Use actual module structure in test mocking
- Implement consistent mocking patterns across test suite

#### 3.2 Test Data Management
- Use pytest fixtures for consistent test data setup
- Create minimal test corpora for faster iteration  
- Separate test data creation from test logic
- Verify test data files match expected corpus structures

#### 3.3 Test Isolation and Cleanup
- Ensure proper test isolation (no shared state)
- Implement proper cleanup in tearDown methods
- Add test data factories for edge cases

### Phase 4: Validation and Regression Prevention (Ongoing)

#### 4.1 Incremental Testing Approach
- **Test order**: parsers � utils � UVI � integration
- **Failure isolation**: Run tests in smaller subsets to prevent cascade failures
- **Progress tracking**: Monitor passing test count after each fix session
- **Target**: Fix 10 failures per day with no regressions

#### 4.2 Hybrid Test Strategy
- **Unit tests**: Fix in isolation first
- **Integration tests**: Run after all unit tests pass
- **End-to-end tests**: Final validation with real corpus data

#### 4.3 Performance and Integration Testing
- Test cross-module dependencies after individual fixes
- Validate end-to-end UVI functionality with real corpus data
- Performance testing for large corpus loads
- Memory usage monitoring during test runs

## Implementation Guidelines

### Test Execution Strategy
```bash
# Diagnostic runs
pytest --tb=no --no-header -v | grep FAILED > failure_analysis.txt

# Development iteration
pytest -k "parser" -x  # Stop on first failure
pytest -k "not placeholder" # Skip placeholder tests during development

# Progress tracking
pytest --tb=line | tee test_results_$(date +%Y%m%d).txt
```

### Success Metrics
- **Short term**: Reduce failures from 47 to <20 within 1 week
- **Medium term**: Reduce failures to <10 within 2 weeks  
- **Long term**: Achieve >95% test pass rate (d15 failures)
- **Quality gate**: No regressions in previously passing tests

### Risk Mitigation
- **Daily regression testing**: Run full test suite before committing changes
- **Backup strategy**: Keep git branches for each major fix phase
- **Documentation updates**: Update docstrings and examples as API changes
- **Feature scope control**: Don't implement new features during bug fixing phase

## Technical Debt Considerations

### Documentation Debt
- Update docstrings to match actual implementation
- Create working usage examples with current code structure
- Document actual vs intended API differences

### Architecture Decisions  
- **Import structure**: Decide on final module exposure pattern
- **API consistency**: Ensure consistent constructor patterns across classes
- **XML parsing strategy**: Standardize namespace handling approach
- **Test architecture**: Establish testing patterns for future development

## Next Steps Priority Order

1. **Start with Phase 0**: Complete diagnostic deep dive before any fixes
2. **Fix imports systematically**: Update all `__init__.py` files before touching individual tests
3. **Implement XML namespace handling**: Create base parser with namespace-aware parsing
4. **Triage placeholder tests ruthlessly**: Remove tests for unplanned features
5. **Add regression prevention measures**: Import stability tests and daily test runs

---

*This strategy was developed through comprehensive test analysis, codebase review, and expert feedback. Focus on systematic progression through phases rather than random bug fixes.*