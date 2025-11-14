# Research & Technical Decisions: Indexed Server Configuration

**Feature**: 001-indexed-server-config  
**Date**: 2025-11-14  
**Phase**: 0 - Research

---

## R1: Environment Variable Scanning Pattern

### Question
What's the best Python approach to scan for PROMETHEUS_SERVER_0 through PROMETHEUS_SERVER_9?

### Options Evaluated

**Option 1: Explicit Loop (Range-Based)**
```python
for i in range(10):
    var_name = f"PROMETHEUS_SERVER_{i}"
    value = os.getenv(var_name)
    if value:
        # Process server config
```

**Pros**:
- Explicit and clear intent (scan exactly 0-9)
- No regex complexity
- Predictable performance (exactly 10 lookups)
- Simple to test

**Cons**:
- Hardcoded range (but that's a spec requirement)

**Option 2: Scan All Environment Variables**
```python
import re
pattern = re.compile(r"PROMETHEUS_SERVER_(\d+)")
for key, value in os.environ.items():
    match = pattern.match(key)
    if match:
        index = int(match.group(1))
        if 0 <= index <= 9:
            # Process server config
```

**Pros**:
- Could detect out-of-range indices for warnings
- More flexible for future expansion

**Cons**:
- More complex code
- Performance overhead (scans ALL env vars)
- Still need explicit 0-9 range check

**Option 3: List Comprehension Filter**
```python
server_vars = [
    (i, os.getenv(f"PROMETHEUS_SERVER_{i}"))
    for i in range(10)
    if os.getenv(f"PROMETHEUS_SERVER_{i}")
]
```

**Pros**:
- Pythonic
- Compact code

**Cons**:
- Double lookup (getenv called twice per index)
- Less readable for complex processing

### Decision: **Option 1 (Explicit Loop)**

**Rationale**:
- Matches spec requirements exactly (scan 0-9)
- Simple, maintainable code
- 10 lookups is trivial performance-wise
- Easy to add logging/error handling
- Clear for testing

**Implementation Sketch**:
```python
def load_servers():
    global SERVERS
    SERVERS = {}
    
    for i in range(10):
        var_name = f"PROMETHEUS_SERVER_{i}"
        config_json = os.getenv(var_name)
        
        if not config_json:
            continue  # Gap allowed
        
        try:
            config = json.loads(config_json)
            # Validate and process config
            # Add to SERVERS dict
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse {var_name}: {e}")
            continue
```

**Out-of-Range Detection** (for FR-003):
Add separate check after main loop:
```python
# Check for out-of-range indices
for i in range(10, 100):  # Check 10-99
    if os.getenv(f"PROMETHEUS_SERVER_{i}"):
        print(f"Warning: PROMETHEUS_SERVER_{i} ignored (only 0-9 supported)")
```

---

## R2: JSON Parsing Error Handling

### Question
How to handle JSON parsing errors gracefully with helpful error messages?

### Options Evaluated

**Option 1: Try/Except Per Variable**
```python
try:
    config = json.loads(config_json)
except json.JSONDecodeError as e:
    print(f"Warning: Invalid JSON in {var_name}: {e}")
    print(f"  Expected format: {{'name':'...','url':'...'}}")
    continue
```

**Option 2: JSON Schema Validation**
```python
import jsonschema

schema = {...}  # Full JSON schema
try:
    config = json.loads(config_json)
    jsonschema.validate(config, schema)
except (json.JSONDecodeError, jsonschema.ValidationError) as e:
    print(f"Warning: Invalid config in {var_name}: {e}")
    continue
```

**Option 3: Custom Validator Function**
```python
def validate_server_config(config, var_name):
    errors = []
    if 'name' not in config:
        errors.append("missing required field 'name'")
    if 'url' not in config:
        errors.append("missing required field 'url'")
    # ... more checks
    if errors:
        print(f"Warning: Invalid {var_name}: {', '.join(errors)}")
        return False
    return True
```

### Decision: **Option 1 + Option 3 Hybrid**

**Rationale**:
- No external dependencies (jsonschema not in requirements.txt)
- Clear, specific error messages per spec requirement FR-009
- Separation of concerns: JSON parsing vs field validation
- Easy to test each error condition

**Implementation Approach**:

**Step 1: Parse JSON**
```python
try:
    config = json.loads(config_json)
except json.JSONDecodeError as e:
    print(f"Warning: Failed to parse {var_name}: {str(e)}")
    print(f"  Expected JSON format: {{'name':'server','url':'https://...'}}")
    continue
```

**Step 2: Validate Required Fields**
```python
if not config.get('name'):
    print(f"Warning: {var_name} missing required field 'name'")
    continue

if not config.get('url'):
    print(f"Warning: {var_name} missing required field 'url'")
    continue
```

**Step 3: Apply Defaults**
```python
server_config = {
    "name": config['name'],
    "url": config['url'],
    "description": config.get('description', ''),
    "token": config.get('token', ''),
    "verify_ssl": parse_verify_ssl(config.get('verify_ssl', True))
}
```

**Step 4: Check Duplicates**
```python
if server_config['name'] in SERVERS:
    print(f"Warning: Duplicate server name '{server_config['name']}' ")
    print(f"  in {var_name}, already defined. Skipping.")
    continue
```

---

## R3: Testing Framework Setup

### Question
How to structure pytest for MCP server testing with environment variable mocking?

### Research Findings

**pytest-mock vs unittest.mock**:
- pytest has built-in `monkeypatch` fixture for env vars
- No additional dependency needed
- Simple API: `monkeypatch.setenv('VAR', 'value')`

**Testing Strategy**:

**1. Fixture: Mock Environment**
```python
# conftest.py
import pytest

@pytest.fixture
def mock_env(monkeypatch):
    """Clean environment fixture"""
    # Clear any existing PROMETHEUS_SERVER_* vars
    for i in range(20):  # Clear more than 0-9 for safety
        monkeypatch.delenv(f"PROMETHEUS_SERVER_{i}", raising=False)
    return monkeypatch

@pytest.fixture
def sample_server_config():
    """Sample valid server configuration"""
    return {
        "name": "test-server",
        "url": "https://prometheus.example.com",
        "description": "Test server",
        "token": "test-token",
        "verify_ssl": True
    }
```

**2. Fixture: Reset SERVERS Dict**
```python
@pytest.fixture(autouse=True)
def reset_servers():
    """Reset global SERVERS dict before each test"""
    import prometheus_mcp
    prometheus_mcp.SERVERS = {}
    yield
    prometheus_mcp.SERVERS = {}
```

**3. Test Structure**
```python
# test_config_loading.py
import json
import prometheus_mcp

def test_single_server(mock_env, sample_server_config):
    # Setup
    mock_env.setenv(
        'PROMETHEUS_SERVER_0',
        json.dumps(sample_server_config)
    )
    
    # Execute
    prometheus_mcp.load_servers()
    
    # Assert
    assert len(prometheus_mcp.SERVERS) == 1
    assert 'test-server' in prometheus_mcp.SERVERS
    assert prometheus_mcp.SERVERS['test-server']['url'] == sample_server_config['url']
```

**4. Testing Async MCP Tools**:
Not needed for this feature - only testing load_servers() which is synchronous.
MCP tools already work with SERVERS dict, so if loading is correct, tools work.

### Decision: **Use pytest with monkeypatch**

**Test Organization**:
```
tests/
├── __init__.py
├── conftest.py                  # Shared fixtures
├── test_config_loading.py       # Main test suite
│   ├── TestBasicLoading         # Happy path tests
│   ├── TestGapHandling          # Gap scenarios
│   ├── TestErrorHandling        # Invalid configs
│   └── TestEdgeCases            # Boundary conditions
└── test_integration.py          # Optional: full MCP server tests
```

**Estimated Test Count**: 18-20 tests
- 6 happy path
- 8 error handling
- 4-6 edge cases

---

## R4: Backward Compatibility Removal

### Question
What code can be safely deleted from load_servers() without breaking SERVERS dict structure?

### Current Code Analysis

**Lines to Remove** (from prometheus_mcp.py):

**Section 1: JSON Array Parsing (lines ~38-53)**
```python
# Try to load multiple servers from JSON configuration
servers_json = os.getenv("PROMETHEUS_SERVERS", "")
if servers_json:
    try:
        servers_list = json.loads(servers_json)
        for server in servers_list:
            name = server.get("name")
            if name:
                SERVERS[name] = {
                    "name": name,
                    "description": server.get("description", ""),
                    "url": server.get("url", ""),
                    "token": server.get("token", ""),
                    "verify_ssl": server.get("verify_ssl", True)
                }
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse PROMETHEUS_SERVERS JSON: {e}")
```

**Section 2: Single Server Fallback (lines ~56-65)**
```python
# Backward compatibility: Load single server configuration
if not SERVERS:
    prometheus_url = os.getenv("PROMETHEUS_URL", "")
    if prometheus_url:
        SERVERS["default"] = {
            "name": "default",
            "description": "Default Prometheus server",
            "url": prometheus_url,
            "token": os.getenv("PROMETHEUS_TOKEN", ""),
            "verify_ssl": os.getenv("PROMETHEUS_VERIFY_SSL", "true").lower() in ("true", "1", "yes")
        }
```

### Decision: **Complete Removal**

**Approach**:
1. Delete all code between lines ~34-66 (the entire try/if blocks)
2. Keep the global SERVERS dict initialization
3. Keep the structure of SERVERS dict (unchanged)
4. Replace with new indexed scanning logic

**SERVERS Dict Structure** (unchanged):
```python
SERVERS = {
    "server-name": {
        "name": str,
        "description": str,
        "url": str,
        "token": str,
        "verify_ssl": bool
    }
}
```

**Migration Impact**:
- Users with PROMETHEUS_URL/TOKEN: Must migrate to PROMETHEUS_SERVER_0
- Users with PROMETHEUS_SERVERS JSON: Must split into indexed variables
- No gradual migration path (breaking change per spec)

---

## R5: verify_ssl Parsing Logic

### Question
How to handle verify_ssl field accepting both boolean and string values?

### Current Implementation
```python
"verify_ssl": os.getenv("PROMETHEUS_VERIFY_SSL", "true").lower() in ("true", "1", "yes")
```

### Decision: **Reuse Existing Pattern with Helper Function**

**Implementation**:
```python
def parse_verify_ssl(value):
    """Parse verify_ssl from various formats"""
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes")
    
    # Invalid type, default to True with warning
    print(f"Warning: Invalid verify_ssl value type {type(value)}, defaulting to True")
    return True
```

**Usage**:
```python
server_config = {
    # ...
    "verify_ssl": parse_verify_ssl(config.get('verify_ssl', True))
}
```

**Test Cases**:
- `True` → `True`
- `False` → `False`
- `"true"` → `True`
- `"false"` → `False`
- `"yes"` → `True`
- `"1"` → `True`
- `"no"` → `False`
- `"maybe"` → `True` (default with warning)
- `123` → `True` (invalid type with warning)

---

## Summary of Technical Decisions

| Research Area | Decision | Rationale |
|---------------|----------|-----------|
| **Scanning Pattern** | Explicit loop range(10) | Simple, clear, matches spec exactly |
| **Error Handling** | Try/except + custom validation | No dependencies, specific error messages |
| **Testing Framework** | pytest with monkeypatch | Built-in, no extra dependencies |
| **Backward Compat** | Complete removal | Per spec, no gradual migration |
| **verify_ssl Parsing** | Helper function, bool + string | Maintains existing behavior |

---

## Implementation Checklist

- [x] Environment scanning pattern decided
- [x] JSON error handling approach defined
- [x] Testing strategy documented
- [x] Backward compatibility removal planned
- [x] verify_ssl parsing logic designed
- [ ] Ready to proceed to Phase 1 (Design Artifacts)

---

## Next Steps

1. Create `data-model.md` - Document server config structure
2. Create `contracts/config-schema.json` - JSON schema for validation reference
3. Create `quickstart.md` - User migration and configuration guide
4. Begin implementation (Task 1.1: Rewrite load_servers())

