# Implementation Plan: Indexed Server Configuration

**Branch**: `001-indexed-server-config` | **Date**: 2025-11-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-indexed-server-config/spec.md`

## Summary

Replace the current multi-server configuration system (which uses either single environment variables or a large JSON array) with indexed environment variables (PROMETHEUS_SERVER_0 through PROMETHEUS_SERVER_9). Each server gets its own JSON-formatted environment variable, improving readability and maintainability. Maximum 10 servers supported, gaps in numbering allowed, zero-based indexing. This breaks backward compatibility but simplifies configuration management.

## Technical Context

**Language/Version**: Python 3.x (existing project constraint)
**Primary Dependencies**: 
- mcp>=1.0.0 (FastMCP framework)
- httpx>=0.27.0 (HTTP client, already in use)
- python-dotenv>=1.0.0 (environment variable loading)
- json (standard library)
- os (standard library)

**Storage**: N/A (stateless MCP server, configuration only)
**Testing**: pytest (needs to be added to requirements.txt)
**Target Platform**: Cross-platform (Linux, macOS, Windows) - runs as MCP server process
**Project Type**: Single project (MCP server tool)
**Performance Goals**: 
- Configuration loading: <100ms for 10 servers
- Startup time: <500ms total
- No runtime performance impact (config loaded once at startup)

**Constraints**: 
- Must break backward compatibility (no legacy config support)
- Zero-based indexing (0-9) for exactly 10 server maximum
- JSON-only format (no alternative formats)
- Gaps in indexing allowed
- Single server still requires indexed format (PROMETHEUS_SERVER_0)

**Scale/Scope**: 
- Maximum 10 servers (indices 0-9)
- Single Python file modification (prometheus_mcp.py)
- Estimated ~150-200 lines of code changes
- ~10-15 test cases needed

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. MCP Protocol Compliance ✅
- **Status**: PASS
- **Rationale**: Feature only modifies configuration loading, not MCP tool behavior. All existing tools (list_servers, check_prometheus_connection, get_alerts) continue to work with loaded servers.
- **Impact**: No changes to tool interfaces or JSON response formats

### II. Multi-Server Architecture ⚠️
- **Status**: PASS with BREAKING CHANGE
- **Rationale**: Feature explicitly breaks backward compatibility by removing support for PROMETHEUS_URL/TOKEN and PROMETHEUS_SERVERS JSON array
- **Impact**: Existing configurations will not work; users must migrate to indexed format
- **Justification**: Spec explicitly states "Breaking backward compatibility is acceptable since the project has no existing users" (Assumptions section)

### III. Security & Authentication ✅
- **Status**: PASS
- **Rationale**: Bearer token support maintained via "token" field in JSON. SSL verification maintained via "verify_ssl" field
- **Impact**: No security changes, same per-server authentication model

### IV. Efficiency & Context Management ✅
- **Status**: PASS
- **Rationale**: Configuration loading is unrelated to context management features
- **Impact**: No changes to extended_metadata or response filtering

### V. Filtering & Query Flexibility ✅
- **Status**: PASS
- **Rationale**: Server loading mechanism independent of filtering features
- **Impact**: No changes to existing tool filtering capabilities

### Error Handling Standards ✅
- **Status**: PASS
- **Rationale**: Spec requires structured error handling (FR-009) with clear warnings for invalid configs
- **Impact**: Must add specific error messages for: JSON parse errors, missing fields, out-of-range indices, duplicate names

### Response Format Standards ✅
- **Status**: PASS
- **Rationale**: No changes to tool response formats
- **Impact**: None

### Configuration Standards ⚠️
- **Status**: PASS with MODIFICATION REQUIRED
- **Current**: load_servers() handles JSON array and single-server configs
- **Required**: load_servers() must be rewritten to scan PROMETHEUS_SERVER_0 through PROMETHEUS_SERVER_9
- **Impact**: Core configuration loading logic changes

### Tool Development Requirements ✅
- **Status**: PASS
- **Rationale**: No new tools being added
- **Impact**: None

### Testing Priorities ⚠️
- **Status**: REQUIRES ADDITION
- **Current**: No automated tests exist in project
- **Required**: Must add pytest and test cases for configuration loading
- **Impact**: New testing infrastructure needed

**Overall Gate Status**: ✅ **APPROVED TO PROCEED**
- Backward compatibility breakage is justified and documented
- Testing infrastructure addition is required
- All other constitutional requirements met

## Project Structure

### Documentation (this feature)

```text
specs/001-indexed-server-config/
├── plan.md              # This file
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (server config structure)
├── quickstart.md        # Phase 1 output (user migration guide)
├── contracts/           # Phase 1 output (config schema)
└── checklists/
    └── requirements.md  # Already created
```

### Source Code (repository root)

```text
prometheus-alerts-mcp/
├── prometheus_mcp.py           # MODIFY: load_servers() function
├── requirements.txt            # ADD: pytest dependency
├── tests/                      # CREATE: new directory
│   ├── __init__.py
│   ├── test_config_loading.py # CREATE: configuration loading tests
│   └── conftest.py             # CREATE: pytest configuration
├── README.md                   # MODIFY: update configuration examples
└── servers-config-example.json # REMOVE: no longer needed
```

**Structure Decision**: Single project structure maintained. This is a modification to existing `prometheus_mcp.py` file, specifically the `load_servers()` function and related configuration logic. New testing infrastructure added in dedicated `tests/` directory.

## Complexity Tracking

> **Not applicable** - No constitutional violations requiring justification. Backward compatibility break is explicitly allowed per spec assumptions.

---

## Phase 0: Research & Technical Decisions

### Research Tasks

#### R1: Environment Variable Scanning Pattern
**Question**: What's the best Python approach to scan for PROMETHEUS_SERVER_0 through PROMETHEUS_SERVER_9?

**Options**:
1. Loop through range(10) and check `os.getenv(f"PROMETHEUS_SERVER_{i}")`
2. Scan all env vars and regex match pattern
3. Use `os.environ.items()` and filter

**Decision Needed**: Choose scanning approach
**Recommendation**: Option 1 (explicit loop) - simpler, more predictable, range is small (10 items)

#### R2: JSON Parsing Error Handling
**Question**: How to handle JSON parsing errors gracefully and provide helpful error messages?

**Options**:
1. Try/except per variable with json.JSONDecodeError
2. Use json.loads with custom error handler
3. Validate JSON schema before parsing

**Decision Needed**: Error handling strategy
**Recommendation**: Option 1 - standard Python pattern, clear error messages per spec requirement

#### R3: Testing Framework Setup
**Question**: How to structure pytest for MCP server testing?

**Areas to research**:
- Mocking environment variables in pytest
- Testing async MCP tools
- Fixture patterns for server configuration
- Integration vs unit test strategy

**Decision Needed**: Test organization and mocking strategy

#### R4: Backward Compatibility Removal
**Question**: What code can be safely deleted from load_servers()?

**Current code paths**:
1. PROMETHEUS_SERVERS JSON array parsing (lines ~38-53)
2. Single server fallback (lines ~56-65)

**Decision Needed**: Clean removal strategy without breaking existing SERVERS dict structure

### Research Output

Create `research.md` with:
- Scanning pattern decision and code sketch
- Error handling patterns with examples
- Testing strategy and fixture design
- Migration guide outline for users

---

## Phase 1: Design Artifacts

### 1.1 Data Model (`data-model.md`)

**Entity**: Server Configuration

```python
{
    "name": str,        # Required, unique identifier
    "url": str,         # Required, Prometheus base URL
    "description": str, # Optional, default: ""
    "token": str,       # Optional, default: ""
    "verify_ssl": bool  # Optional, default: True
}
```

**Validation Rules**:
- `name`: Must be non-empty string, unique across all servers
- `url`: Must be non-empty string (format validation out of scope per spec)
- `description`: String, defaults to empty
- `token`: String, defaults to empty
- `verify_ssl`: Boolean or string "true"/"false", defaults to True

**Storage Structure** (SERVERS dict):
```python
SERVERS = {
    "server-name": {
        "name": "server-name",
        "url": "https://...",
        "description": "...",
        "token": "...",
        "verify_ssl": True
    },
    ...
}
```

### 1.2 Configuration Contract (`contracts/config-schema.json`)

JSON schema for each PROMETHEUS_SERVER_N variable:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["name", "url"],
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "description": "Unique identifier for the server"
    },
    "url": {
      "type": "string",
      "minLength": 1,
      "description": "Base URL of Prometheus server"
    },
    "description": {
      "type": "string",
      "default": "",
      "description": "Human-readable description"
    },
    "token": {
      "type": "string",
      "default": "",
      "description": "Bearer token for authentication"
    },
    "verify_ssl": {
      "type": "boolean",
      "default": true,
      "description": "Whether to verify SSL certificates"
    }
  },
  "additionalProperties": false
}
```

### 1.3 API Contracts

Not applicable - this feature does not add or modify MCP tool interfaces. Configuration loading is internal.

### 1.4 Quickstart Guide (`quickstart.md`)

**Target Audience**: Existing users migrating from old format, new users

**Sections**:
1. **Migration from Old Format**
   - Convert PROMETHEUS_URL/TOKEN to PROMETHEUS_SERVER_0
   - Convert PROMETHEUS_SERVERS JSON array to indexed variables
   - Examples for 1, 3, and 10 servers

2. **New Configuration Guide**
   - Zero-based indexing explanation
   - JSON format requirements
   - Required vs optional fields
   - Gap handling examples

3. **Troubleshooting**
   - Common JSON errors
   - Out-of-range index warnings
   - Duplicate name resolution
   - Missing required fields

4. **Examples**
   - Single server
   - Multiple servers (2, 5, 10)
   - Servers with gaps (0, 3, 7)
   - All field combinations

---

## Phase 2: Implementation Tasks

### Task Phase: Priority 1 (Core Functionality)

#### Task 1.1: Rewrite load_servers() Function
**Functional Requirements**: FR-001, FR-002, FR-004, FR-012
**Acceptance Scenarios**: US1-AS1, US1-AS2, US1-AS3

**Implementation**:
1. Remove existing PROMETHEUS_SERVERS and PROMETHEUS_URL logic
2. Create loop to scan indices 0-9
3. For each index, call `os.getenv(f"PROMETHEUS_SERVER_{i}")`
4. Skip if variable not set (gaps allowed)
5. Parse JSON for each found variable
6. Build SERVERS dictionary

**Tests Required**:
- Single server at index 0
- Multiple servers (0, 1, 2)
- Servers with gaps (0, 3, 7)
- All 10 servers configured
- No servers configured (empty SERVERS dict)

**Estimated Effort**: 2-3 hours

---

#### Task 1.2: Implement JSON Parsing with Validation
**Functional Requirements**: FR-004, FR-005, FR-006, FR-007
**Acceptance Scenarios**: US2-AS1, US2-AS2, US2-AS3, US2-AS4

**Implementation**:
1. Wrap json.loads() in try/except for each variable
2. Validate required fields (name, url) present
3. Apply defaults for optional fields
4. Return None for invalid configs (skip that server)
5. Handle verify_ssl as boolean or string

**Tests Required**:
- Valid JSON with all fields
- Valid JSON with only required fields
- Missing required field (name or url)
- Invalid JSON syntax
- Empty string as environment variable value

**Estimated Effort**: 2 hours

---

#### Task 1.3: Implement Gap Handling
**Functional Requirements**: FR-008, FR-011
**Acceptance Scenarios**: US1-AS4, US1-AS6

**Implementation**:
1. Continue loop even if index N not found
2. Load servers at subsequent indices
3. Verify single server works at any index

**Tests Required**:
- Gaps at beginning (missing 0, have 1-2)
- Gaps in middle (0, 2, 4)
- Gaps at end (0-7, missing 8-9)
- Only index 9 configured
- Only index 0 configured

**Estimated Effort**: 1 hour

---

### Task Phase: Priority 2 (Error Handling)

#### Task 2.1: Implement Out-of-Range Index Warning
**Functional Requirements**: FR-003
**Acceptance Scenarios**: US3-AS5

**Implementation**:
1. Check for PROMETHEUS_SERVER_10+ in environment
2. Log warning message if found
3. Ignore those variables

**Tests Required**:
- INDEX 10 configured and ignored
- INDEX 15 configured and ignored
- Negative indices ignored
- Non-numeric suffixes ignored (PROMETHEUS_SERVER_ABC)

**Estimated Effort**: 1 hour

---

#### Task 2.2: Implement JSON Parse Error Warnings
**Functional Requirements**: FR-009
**Acceptance Scenarios**: US3-AS2

**Implementation**:
1. Catch json.JSONDecodeError
2. Log descriptive warning with:
   - Which variable (PROMETHEUS_SERVER_N)
   - Parse error details
   - Example of correct format
3. Continue loading other servers

**Tests Required**:
- Invalid JSON in index 0
- Invalid JSON in index 5 (others load correctly)
- Multiple invalid JSONs (all skipped with warnings)

**Estimated Effort**: 1.5 hours

---

#### Task 2.3: Implement Missing Field Warnings
**Functional Requirements**: FR-007, FR-009
**Acceptance Scenarios**: US3-AS1

**Implementation**:
1. Check for required fields (name, url)
2. Log warning with specific missing field
3. Skip that server
4. Continue loading others

**Tests Required**:
- Missing name field
- Missing url field
- Missing both fields
- Empty string for required field

**Estimated Effort**: 1 hour

---

#### Task 2.4: Implement Duplicate Name Handling
**Functional Requirements**: FR-010
**Acceptance Scenarios**: US3-AS3

**Implementation**:
1. Track loaded server names
2. Detect duplicates
3. Log warning with both indices
4. Skip duplicate (keep first occurrence)

**Alternative Approach**: Auto-rename by appending index (e.g., "prod" → "prod-5")

**Tests Required**:
- Two servers same name
- Three servers same name
- Duplicate name verification in warning message

**Estimated Effort**: 1.5 hours

---

#### Task 2.5: Implement Invalid verify_ssl Handling
**Functional Requirements**: FR-006
**Acceptance Scenarios**: US3-AS4

**Implementation**:
1. Accept boolean True/False
2. Accept strings "true"/"false"/"yes"/"1"
3. Default to True for invalid values
4. Log warning for invalid values

**Tests Required**:
- Boolean true/false
- String "true"/"false"
- Invalid string "maybe"
- Numeric 1/0
- Missing verify_ssl field (defaults to True)

**Estimated Effort**: 1 hour

---

### Task Phase: Priority 3 (Testing & Documentation)

#### Task 3.1: Setup pytest Infrastructure
**Testing Priority**: Required by constitution check

**Implementation**:
1. Add pytest to requirements.txt
2. Create tests/ directory structure
3. Create conftest.py with fixtures:
   - mock_env_vars fixture
   - reset_servers fixture
   - sample_config fixture
4. Create test_config_loading.py

**Estimated Effort**: 2 hours

---

#### Task 3.2: Write Comprehensive Test Suite
**Testing Priority**: All functional requirements

**Test Categories**:
1. **Happy Path Tests** (6 tests)
   - Single server various indices
   - Multiple servers
   - All 10 servers
   - Servers with gaps

2. **Error Handling Tests** (8 tests)
   - Invalid JSON
   - Missing required fields
   - Duplicate names
   - Out-of-range indices
   - Invalid verify_ssl
   - Empty environment

3. **Edge Case Tests** (4 tests)
   - Only index 9 configured
   - All even indices
   - Single character in JSON
   - Very large JSON (within env var limits)

**Estimated Effort**: 4-5 hours

---

#### Task 3.3: Update README.md
**Documentation Standard**: Per constitution

**Updates Required**:
1. Remove old configuration examples
2. Add indexed configuration section
3. Show examples for 1, 3, 10 servers
4. Explain zero-based indexing
5. Document gap handling
6. Add troubleshooting section

**Estimated Effort**: 1.5 hours

---

#### Task 3.4: Remove Obsolete Files
**Cleanup Task**

**Files to Remove**:
- servers-config-example.json (no longer relevant)

**Files to Update**:
- Remove .env references to PROMETHEUS_SERVERS

**Estimated Effort**: 0.5 hours

---

## Implementation Sequence

### Sprint 1: Core Functionality (6-7 hours)
1. Task 1.1: Rewrite load_servers() - **BLOCKING** for all other tasks
2. Task 1.2: JSON parsing with validation - depends on 1.1
3. Task 1.3: Gap handling - depends on 1.1

**Deliverable**: Basic indexed loading works for valid configurations

---

### Sprint 2: Error Handling (6 hours)
4. Task 2.1: Out-of-range warnings - independent
5. Task 2.2: JSON parse errors - independent
6. Task 2.3: Missing field warnings - independent
7. Task 2.4: Duplicate name handling - independent
8. Task 2.5: Invalid verify_ssl handling - independent

**Deliverable**: All error cases handled gracefully

---

### Sprint 3: Testing & Documentation (8-9 hours)
9. Task 3.1: Setup pytest - **BLOCKING** for 3.2
10. Task 3.2: Write test suite - depends on 3.1
11. Task 3.3: Update README - independent
12. Task 3.4: Remove obsolete files - independent

**Deliverable**: Fully tested, documented feature ready for merge

---

## Total Estimated Effort: 20-22 hours

---

## Acceptance Criteria Summary

**User Story 1 (P1) - Complete when**:
- ✅ Single server loads from PROMETHEUS_SERVER_0
- ✅ Multiple servers load from indexed variables
- ✅ All 10 servers load correctly
- ✅ Gaps in numbering handled correctly
- ✅ list_servers tool shows all loaded servers

**User Story 2 (P1) - Complete when**:
- ✅ All 5 fields parsed correctly from JSON
- ✅ Required fields enforced
- ✅ Optional field defaults applied
- ✅ verify_ssl boolean works correctly

**User Story 3 (P2) - Complete when**:
- ✅ Missing field warnings logged
- ✅ Invalid JSON warnings logged
- ✅ Duplicate name warnings logged
- ✅ Invalid verify_ssl warnings logged
- ✅ Out-of-range index warnings logged
- ✅ Valid servers still load despite errors in others

**Overall Feature Complete when**:
- ✅ All 21 acceptance scenarios pass
- ✅ All 18+ tests pass
- ✅ README updated
- ✅ No linter errors
- ✅ Backward compatibility fully removed
- ✅ Constitution requirements met
