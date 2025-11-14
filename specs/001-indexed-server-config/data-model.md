# Data Model: Indexed Server Configuration

**Feature**: 001-indexed-server-config  
**Date**: 2025-11-14  
**Phase**: 1 - Design

---

## Entity: Server Configuration

### Description
Represents a single Prometheus server connection configuration loaded from an indexed environment variable.

### Fields

| Field | Type | Required | Default | Description | Validation |
|-------|------|----------|---------|-------------|------------|
| `name` | string | Yes | - | Unique identifier for the server | Non-empty, unique across all servers |
| `url` | string | Yes | - | Base URL of Prometheus server | Non-empty string, must include protocol |
| `description` | string | No | `""` | Human-readable label | Any string |
| `token` | string | No | `""` | Bearer token for authentication | Any string, kept confidential |
| `verify_ssl` | boolean | No | `true` | Whether to verify SSL certificates | Boolean or string ("true"/"false") |

### JSON Representation (Input Format)

Environment variable contains JSON object:

```json
{
  "name": "production",
  "url": "https://prometheus-prod.example.com",
  "description": "Production Prometheus Server",
  "token": "my-bearer-token-123",
  "verify_ssl": true
}
```

### Python Dictionary (Internal Storage)

Stored in `SERVERS` global dictionary:

```python
SERVERS = {
    "production": {  # Key is the 'name' field
        "name": "production",
        "url": "https://prometheus-prod.example.com",
        "description": "Production Prometheus Server",
        "token": "my-bearer-token-123",
        "verify_ssl": True
    }
}
```

---

## Storage Structure: SERVERS Dictionary

### Type Signature
```python
SERVERS: Dict[str, Dict[str, Union[str, bool]]]
```

### Structure
```python
{
    "server-name-1": ServerConfig,
    "server-name-2": ServerConfig,
    ...
}
```

### Key Rules
- Dictionary key is the server's `name` field
- Must be unique (duplicates rejected with warning)
- Used for server lookup in MCP tools

### Value Rules
- Each value is a ServerConfig dictionary
- All fields present (defaults applied if missing in input)
- `verify_ssl` always stored as boolean (not string)

---

## Entity Relationships

```
Environment Variables (Input)
  │
  ├─ PROMETHEUS_SERVER_0  →  ServerConfig
  ├─ PROMETHEUS_SERVER_1  →  ServerConfig
  ├─ PROMETHEUS_SERVER_2  →  ServerConfig
  │  ...
  └─ PROMETHEUS_SERVER_9  →  ServerConfig
          │
          ↓
      SERVERS Dict (Storage)
          │
          ↓
  MCP Tools (Consumers)
    ├─ list_servers()
    ├─ check_prometheus_connection(server_name)
    └─ get_alerts(server_name, ...)
```

---

## State Transitions

### Loading Process

```
1. [Not Loaded]
   │
   ├─ Environment variable exists
   │  └─ Parse JSON
   │     ├─ Success → [Validate Fields]
   │     └─ Fail → [Skip with Warning]
   │
   ├─ Environment variable missing
   │  └─ [Skip silently] (gap allowed)
   │
2. [Validate Fields]
   │
   ├─ Required fields present (name, url)
   │  └─ [Apply Defaults]
   │     └─ [Check Uniqueness]
   │        ├─ Name unique → [Loaded Successfully]
   │        └─ Name duplicate → [Skip with Warning]
   │
   └─ Required fields missing
      └─ [Skip with Warning]
```

### Final States
- **Loaded Successfully**: Server added to SERVERS dict
- **Skip with Warning**: Error logged, server not added, continue with others
- **Skip silently**: Environment variable not set (gap), no action needed

---

## Validation Rules

### Name Field
```python
# Must be non-empty string
if not config.get('name') or not isinstance(config['name'], str):
    # Invalid: skip with warning
    
# Must be unique
if config['name'] in SERVERS:
    # Duplicate: skip with warning
```

### URL Field
```python
# Must be non-empty string
if not config.get('url') or not isinstance(config['url'], str):
    # Invalid: skip with warning

# Note: URL format validation out of scope per spec
# Accept any non-empty string
```

### Description Field (Optional)
```python
# Default to empty string
description = config.get('description', '')
if not isinstance(description, str):
    description = str(description)  # Coerce to string
```

### Token Field (Optional)
```python
# Default to empty string
token = config.get('token', '')
if not isinstance(token, str):
    token = str(token)  # Coerce to string
```

### verify_ssl Field (Optional)
```python
def parse_verify_ssl(value):
    """
    Accept:
    - Boolean True/False
    - String "true"/"false"/"yes"/"1"
    Default to True for invalid values with warning
    """
    if value is None:
        return True  # Default
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes")
    
    # Invalid type
    print(f"Warning: Invalid verify_ssl value, defaulting to True")
    return True
```

---

## Index to Server Name Mapping

### Input
```bash
PROMETHEUS_SERVER_0='{"name":"prod","url":"https://..."}'
PROMETHEUS_SERVER_3='{"name":"staging","url":"https://..."}'
PROMETHEUS_SERVER_7='{"name":"dev","url":"https://..."}'
```

### Output
```python
SERVERS = {
    "prod": {...},      # From index 0
    "staging": {...},   # From index 3
    "dev": {...}        # From index 7
}
```

### Key Point
- Index number (0, 3, 7) is **not** stored
- Server identified by `name` field only
- Index only used during loading phase
- Gaps (1, 2, 4, 5, 6, 8, 9) are silently ignored

---

## Examples

### Example 1: Minimal Configuration
```json
{
  "name": "simple",
  "url": "http://localhost:9090"
}
```

**Result**:
```python
{
    "name": "simple",
    "url": "http://localhost:9090",
    "description": "",
    "token": "",
    "verify_ssl": True
}
```

### Example 2: Full Configuration
```json
{
  "name": "production",
  "url": "https://prometheus-prod.example.com",
  "description": "Production Prometheus Server",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "verify_ssl": true
}
```

**Result**:
```python
{
    "name": "production",
    "url": "https://prometheus-prod.example.com",
    "description": "Production Prometheus Server",
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "verify_ssl": True
}
```

### Example 3: Self-Signed Certificate
```json
{
  "name": "staging",
  "url": "https://prometheus-staging.local",
  "verify_ssl": false
}
```

**Result**:
```python
{
    "name": "staging",
    "url": "https://prometheus-staging.local",
    "description": "",
    "token": "",
    "verify_ssl": False
}
```

---

## Error Cases

### Case 1: Missing Required Field
**Input**: `{"name": "test"}`  
**Error**: Missing required field 'url'  
**Result**: Skip server, log warning, continue

### Case 2: Invalid JSON
**Input**: `{"name": "test", "url": "http://..."`  
**Error**: JSON parse error  
**Result**: Skip server, log warning with parse details, continue

### Case 3: Duplicate Name
**Input**: Two servers both named "production"  
**Error**: Duplicate server name  
**Result**: Keep first, skip second with warning, continue

### Case 4: Empty Name
**Input**: `{"name": "", "url": "http://..."}`  
**Error**: Name field empty  
**Result**: Skip server, log warning, continue

---

## Constraints

| Constraint | Value | Enforcement |
|------------|-------|-------------|
| Max Servers | 10 | Only scan indices 0-9 |
| Min Servers | 0 | Empty SERVERS dict if no configs found |
| Name Length | No limit | Any non-empty string accepted |
| URL Length | No limit | Limited by env var size (~32KB) |
| Token Length | No limit | Limited by env var size |
| Uniqueness | Names must be unique | First occurrence wins |
| Index Range | 0-9 only | Out-of-range ignored with warning |

---

## Performance Characteristics

- **Load Time**: O(n) where n = 10 (constant, always scan 10 indices)
- **Memory**: O(m) where m = number of valid servers loaded (≤10)
- **Lookup**: O(1) by server name (dict key access)
- **Expected Load Time**: <50ms for 10 servers on modern hardware

---

## Implementation Notes

1. **Global State**: SERVERS dict is module-level global, initialized once at startup
2. **Thread Safety**: Not required (single-threaded MCP server startup)
3. **Immutability**: SERVERS not modified after load_servers() completes
4. **No Persistence**: Configuration only in memory, reloaded on each restart
5. **No Dynamic Reload**: Server restart required to change configuration

