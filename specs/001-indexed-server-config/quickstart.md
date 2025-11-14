# Quickstart: Indexed Server Configuration

**Feature**: 001-indexed-server-config  
**Target Audience**: MCP users configuring Prometheus servers  
**Date**: 2025-11-14

---

## Overview

Starting with this version, Prometheus servers are configured using **indexed environment variables** (PROMETHEUS_SERVER_0 through PROMETHEUS_SERVER_9) instead of a single JSON array or legacy single-server variables.

### Key Changes
- ✅ Maximum 10 servers supported (indices 0-9)
- ✅ Zero-based indexing (starts at 0, not 1)
- ✅ JSON format for each server
- ✅ Gaps in numbering allowed
- ⚠️ **BREAKING**: Old formats (PROMETHEUS_URL, PROMETHEUS_SERVERS) no longer supported

---

## Quick Start for New Users

### Single Server Configuration

```bash
export PROMETHEUS_SERVER_0='{"name":"my-prometheus","url":"https://prometheus.example.com"}'
```

That's it! Start your MCP server and it will load one server named "my-prometheus".

### Multiple Servers

```bash
export PROMETHEUS_SERVER_0='{"name":"production","url":"https://prom-prod.example.com","token":"prod-token"}'
export PROMETHEUS_SERVER_1='{"name":"staging","url":"https://prom-staging.example.com","token":"staging-token"}'
export PROMETHEUS_SERVER_2='{"name":"development","url":"http://localhost:9090"}'
```

---

## Migration Guide (Breaking Changes)

###⚠️ Old Configuration Format No Longer Works

If you're upgrading from an older version, you **must** migrate your configuration.

### Migration: Single Server (PROMETHEUS_URL/TOKEN)

**OLD**:
```bash
export PROMETHEUS_URL="https://prometheus.example.com"
export PROMETHEUS_TOKEN="my-bearer-token"
export PROMETHEUS_VERIFY_SSL="false"
```

**NEW**:
```bash
export PROMETHEUS_SERVER_0='{"name":"prometheus","url":"https://prometheus.example.com","token":"my-bearer-token","verify_ssl":false}'
```

### Migration: JSON Array (PROMETHEUS_SERVERS)

**OLD**:
```bash
export PROMETHEUS_SERVERS='[{"name":"prod","url":"https://prom-prod.example.com","token":"token1"},{"name":"staging","url":"https://prom-staging.example.com","token":"token2"}]'
```

**NEW**:
```bash
export PROMETHEUS_SERVER_0='{"name":"prod","url":"https://prom-prod.example.com","token":"token1"}'
export PROMETHEUS_SERVER_1='{"name":"staging","url":"https://prom-staging.example.com","token":"token2"}'
```

### Why This Change?

- **Readability**: Each server in its own variable is easier to read
- **Modifiability**: Change one server without editing large JSON array
- **Tooling**: Standard environment variable tools work better with individual vars
- **Debugging**: Easier to see which server configuration is problematic

---

## Configuration Format

### Required Fields

Every server configuration **must** include:

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Unique server identifier | `"production"` |
| `url` | Prometheus base URL with protocol | `"https://prometheus.example.com"` |

### Optional Fields

| Field | Default | Description | Example |
|-------|---------|-------------|---------|
| `description` | `""` | Human-readable label | `"Production Server"` |
| `token` | `""` | Bearer token for auth | `"eyJhbGci..."` |
| `verify_ssl` | `true` | Verify SSL certificates | `false` for self-signed |

---

## Configuration Examples

### Example 1: Minimal Single Server

```bash
export PROMETHEUS_SERVER_0='{"name":"local","url":"http://localhost:9090"}'
```

### Example 2: Production Server with Authentication

```bash
export PROMETHEUS_SERVER_0='{
  "name": "production",
  "url": "https://prometheus-prod.example.com",
  "description": "Production Prometheus Monitoring",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "verify_ssl": true
}'
```

### Example 3: Self-Signed Certificate (Staging)

```bash
export PROMETHEUS_SERVER_0='{
  "name": "staging",
  "url": "https://prometheus-staging.local",
  "description": "Staging Environment",
  "verify_ssl": false
}'
```

### Example 4: Three Servers (Production, Staging, Dev)

```bash
export PROMETHEUS_SERVER_0='{"name":"prod","url":"https://prom-prod.example.com","description":"Production","token":"prod-token-123"}'
export PROMETHEUS_SERVER_1='{"name":"staging","url":"https://prom-staging.example.com","description":"Staging","token":"staging-token-456"}'
export PROMETHEUS_SERVER_2='{"name":"dev","url":"http://localhost:9090","description":"Local Development"}'
```

### Example 5: Servers with Gaps (Indices 0, 3, 7)

```bash
export PROMETHEUS_SERVER_0='{"name":"prod-us-east","url":"https://prom-use1.example.com"}'
export PROMETHEUS_SERVER_3='{"name":"prod-eu-west","url":"https://prom-euw1.example.com"}'
export PROMETHEUS_SERVER_7='{"name":"prod-ap-south","url":"https://prom-aps1.example.com"}'
```

Gaps at indices 1, 2, 4, 5, 6, 8, 9 are perfectly fine!

### Example 6: Maximum 10 Servers

```bash
export PROMETHEUS_SERVER_0='{"name":"prod-use1","url":"https://prom-use1.example.com"}'
export PROMETHEUS_SERVER_1='{"name":"prod-use2","url":"https://prom-use2.example.com"}'
export PROMETHEUS_SERVER_2='{"name":"prod-usw1","url":"https://prom-usw1.example.com"}'
export PROMETHEUS_SERVER_3='{"name":"prod-euw1","url":"https://prom-euw1.example.com"}'
export PROMETHEUS_SERVER_4='{"name":"prod-euc1","url":"https://prom-euc1.example.com"}'
export PROMETHEUS_SERVER_5='{"name":"prod-aps1","url":"https://prom-aps1.example.com"}'
export PROMETHEUS_SERVER_6='{"name":"staging-use1","url":"https://prom-staging-use1.example.com"}'
export PROMETHEUS_SERVER_7='{"name":"staging-euw1","url":"https://prom-staging-euw1.example.com"}'
export PROMETHEUS_SERVER_8='{"name":"dev-shared","url":"https://prom-dev.example.com"}'
export PROMETHEUS_SERVER_9='{"name":"localhost","url":"http://localhost:9090"}'
```

---

## MCP Configuration File (mcp.json)

### Single Server

```json
{
  "mcpServers": {
    "prometheus": {
      "command": "python",
      "args": ["/path/to/prometheus-alerts-mcp/prometheus_mcp.py"],
      "env": {
        "PROMETHEUS_SERVER_0": "{\"name\":\"prometheus\",\"url\":\"https://prometheus.example.com\",\"token\":\"my-token\"}"
      }
    }
  }
}
```

### Multiple Servers

```json
{
  "mcpServers": {
    "prometheus": {
      "command": "python",
      "args": ["/path/to/prometheus-alerts-mcp/prometheus_mcp.py"],
      "env": {
        "PROMETHEUS_SERVER_0": "{\"name\":\"production\",\"url\":\"https://prom-prod.example.com\",\"token\":\"prod-token\"}",
        "PROMETHEUS_SERVER_1": "{\"name\":\"staging\",\"url\":\"https://prom-staging.example.com\",\"token\":\"staging-token\"}",
        "PROMETHEUS_SERVER_2": "{\"name\":\"development\",\"url\":\"http://localhost:9090\"}"
      }
    }
  }
}
```

**Note**: In JSON, double quotes must be escaped as `\"`.

---

## Troubleshooting

### Error: "Warning: Failed to parse PROMETHEUS_SERVER_0"

**Cause**: Invalid JSON syntax

**Solution**: Validate your JSON:
```bash
echo $PROMETHEUS_SERVER_0 | python -m json.tool
```

Common JSON errors:
- Missing quotes around keys/values
- Extra comma at end of object
- Single quotes instead of double quotes
- Unescaped quotes in mcp.json

### Error: "Warning: PROMETHEUS_SERVER_0 missing required field 'url'"

**Cause**: JSON doesn't include required field

**Solution**: Ensure both `name` and `url` are present:
```bash
# BAD
export PROMETHEUS_SERVER_0='{"name":"test"}'

# GOOD
export PROMETHEUS_SERVER_0='{"name":"test","url":"http://localhost:9090"}'
```

### Error: "Warning: Duplicate server name 'production'"

**Cause**: Two servers have the same `name` field

**Solution**: Make sure each server has a unique name:
```bash
# BAD - both named "prod"
export PROMETHEUS_SERVER_0='{"name":"prod","url":"http://..."}'
export PROMETHEUS_SERVER_1='{"name":"prod","url":"http://..."}'

# GOOD - unique names
export PROMETHEUS_SERVER_0='{"name":"prod-us","url":"http://..."}'
export PROMETHEUS_SERVER_1='{"name":"prod-eu","url":"http://..."}'
```

### Warning: "PROMETHEUS_SERVER_10 ignored (only 0-9 supported)"

**Cause**: Index out of range

**Solution**: Only use indices 0-9. If you need more than 10 servers, indices 10+ are not supported.

### Server Not Loading But No Error

**Check**:
1. Is the environment variable actually set?
   ```bash
   echo $PROMETHEUS_SERVER_0
   ```

2. Is the JSON valid?
   ```bash
   echo $PROMETHEUS_SERVER_0 | python -m json.tool
   ```

3. Are you using the correct index (0-9)?

4. Check MCP server logs for warnings

---

## Best Practices

### 1. Use Index 0 for Primary Server
```bash
# Recommended
export PROMETHEUS_SERVER_0='{"name":"primary",...}'
```

### 2. Group by Environment
```bash
export PROMETHEUS_SERVER_0='{"name":"prod-1",...}'
export PROMETHEUS_SERVER_1='{"name":"prod-2",...}'
export PROMETHEUS_SERVER_5='{"name":"staging-1",...}'
export PROMETHEUS_SERVER_9='{"name":"dev-local",...}'
```

### 3. Use Descriptive Names
```bash
# Good
"name": "prod-us-east-1"
"name": "staging-europe"

# Less helpful
"name": "server1"
"name": "prom"
```

### 4. Document in Your Config
```bash
# Production servers
export PROMETHEUS_SERVER_0='{"name":"prod-primary",...}'
export PROMETHEUS_SERVER_1='{"name":"prod-backup",...}'

# Non-production
export PROMETHEUS_SERVER_5='{"name":"staging",...}'
```

### 5. Store Tokens Securely
Don't commit tokens to version control. Use:
- Environment files (.env) in .gitignore
- Secret management systems
- Container orchestration secrets

---

## Testing Your Configuration

### 1. Verify Environment Variables Set
```bash
for i in {0..9}; do
    var="PROMETHEUS_SERVER_$i"
    if [ ! -z "${!var}" ]; then
        echo "$var is set"
    fi
done
```

### 2. Validate JSON
```bash
for i in {0..9}; do
    var="PROMETHEUS_SERVER_$i"
    val="${!var}"
    if [ ! -z "$val" ]; then
        echo "Validating $var:"
        echo "$val" | python -m json.tool || echo "  ❌ Invalid JSON"
    fi
done
```

### 3. Test MCP Server
```bash
python prometheus_mcp.py
# Check output for warnings about configuration
```

### 4. Use list_servers Tool
After starting, use the MCP `list_servers` tool to verify all servers loaded correctly.

---

## FAQ

**Q: Why zero-based indexing (0-9 instead of 1-10)?**  
A: Aligns with programming conventions and makes the 0-9 range clearer.

**Q: Can I use only index 5 without 0-4?**  
A: Yes! Gaps are allowed. Use any combination of indices 0-9.

**Q: What happens to index 10 and above?**  
A: They're ignored with a warning. Only 0-9 are supported.

**Q: Can I have more than 10 servers?**  
A: No, the maximum is 10 servers (indices 0-9).

**Q: Do I need to escape JSON in bash?**  
A: Use single quotes around the JSON string: `'{"key":"value"}'`

**Q: Do I need to escape JSON in mcp.json?**  
A: Yes, escape double quotes: `"{\"key\":\"value\"}"`

**Q: Can I reload config without restarting?**  
A: No, you must restart the MCP server to reload configuration.

**Q: Where are logs for configuration errors?**  
A: Check stdout/stderr where you run the MCP server, or your MCP client logs.

---

## Next Steps

1. ✅ Configure your servers using indexed variables
2. ✅ Test with `list_servers` MCP tool
3. ✅ Use `check_prometheus_connection` to verify connectivity
4. ✅ Start querying alerts with `get_alerts` tool

For more information, see the main README.md in the project root.

