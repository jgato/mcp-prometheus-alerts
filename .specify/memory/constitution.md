# Prometheus Alerts MCP Server Constitution

## Core Principles

### I. MCP Protocol Compliance
- All tools must follow the Model Context Protocol (MCP) specification using FastMCP
- Tools must return structured JSON responses for all operations
- Error handling must be consistent: return JSON with `status: "error"` and descriptive `message` fields
- All async operations must use httpx for HTTP requests
- Tool docstrings must clearly describe parameters, return values, and behavior

### II. Multi-Server Architecture
- Support both single-server (backward compatible) and multi-server configurations
- Server configuration via environment variables: `PROMETHEUS_URL`/`PROMETHEUS_TOKEN` for single server, `PROMETHEUS_SERVERS` JSON for multiple servers
- Every tool must accept optional `server_name` parameter; if empty, default to first configured server
- Server lookup failures must return clear error messages listing available servers
- Each server config must include: name, url, optional description, optional token, and verify_ssl flag

### III. Security & Authentication
- Support Bearer token authentication for protected Prometheus instances
- SSL certificate verification configurable per server (default: enabled)
- Tokens must never be exposed in logs or error messages
- Environment variables are the sole source of credentials (no hardcoded values)
- Each server can have independent authentication configuration

### IV. Efficiency & Context Management
- Default to minimal metadata in responses to conserve context window space
- `extended_metadata` parameter (default: False) controls response verbosity
- Minimal mode returns only: name, state, severity, annotations
- Extended mode includes: queries, evaluation times, health status, all labels
- Documentation must guide users on when to use each mode

### V. Filtering & Query Flexibility
- Support filtering by: server name, alert state (firing/pending/inactive), group name, alert name
- Filters must be composable (can combine multiple filters)
- Empty filter parameters mean "no filter applied"
- All filtered results must include summary statistics: total rules, firing count, pending count, inactive count
- Provide clear feedback about applied filters in response

## Technical Requirements

### Error Handling Standards
- Graceful degradation: connection timeouts, HTTP errors, SSL errors must all return structured error responses
- Specific error messages for: missing servers, connection failures, authentication failures, invalid responses
- Include server name in all error responses for multi-server context
- Catch and handle: `httpx.TimeoutException`, `httpx.ConnectError`, general exceptions

### Response Format Standards
- All tool responses must be valid JSON strings
- Success responses include: `status: "success"`, relevant data, server identification
- Error responses include: `status: "error"`, descriptive `message`, server context, optional `details`
- Use 2-space indentation for JSON responses (readable in logs)
- Include summary statistics where applicable

### Configuration Standards
- Environment variables parsed at startup via `load_servers()`
- JSON configuration must handle parse errors gracefully with warnings
- Server configurations stored in global `SERVERS` dictionary
- Support for `PROMETHEUS_VERIFY_SSL` as boolean string ("true"/"false"/"yes"/"1")
- Validation: all servers must have name and url; other fields optional

## Development Workflow

### Tool Development Requirements
- Each new tool must be decorated with `@mcp.tool()`
- Tools must be async functions
- Tool names should be clear and action-oriented (e.g., `get_alerts`, `check_prometheus_connection`)
- Parameter descriptions must explain purpose and expected format
- Document backward compatibility considerations for any changes

### Testing Priorities
- Connection testing against real Prometheus instances
- Multi-server configuration parsing and selection
- Filter combinations (state + group + alert name)
- Error scenarios: timeouts, invalid servers, auth failures
- SSL verification toggle behavior
- JSON response validation

### Documentation Standards
- README must document both single and multi-server configuration modes
- Provide example configurations for common scenarios
- Tool descriptions must explain when to use minimal vs extended metadata
- Include examples showing filter usage and multi-server comparisons
- Document context window management strategies
- Documentation is simple, clean, short and avoiding abuse of emoticons

## Governance

- This constitution defines the minimum requirements for the Prometheus Alerts MCP Server
- All new features must comply with MCP protocol standards and multi-server architecture
- Breaking changes require backward compatibility consideration (e.g., single-server mode support)
- Security changes (auth, SSL) require explicit documentation
- Performance optimizations must not sacrifice error clarity or user experience
- Amendments to this constitution should be documented with rationale and migration notes

**Version**: 1.0.0 | **Ratified**: 2025-11-14 | **Last Amended**: 2025-11-14
