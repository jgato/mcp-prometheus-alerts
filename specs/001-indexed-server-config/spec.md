# Feature Specification: Indexed Server Configuration

**Feature Branch**: `001-indexed-server-config`  
**Created**: 2025-11-14  
**Status**: Draft  
**Input**: User description: "Improve multi-server configuration by using indexed environment variables (PROMETHEUS_SERVER_1, PROMETHEUS_SERVER_2, etc.) instead of a single long JSON array, making it easier to read and modify"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Multiple Servers with Individual Variables (Priority: P1)

As an MCP user managing multiple Prometheus environments, I need to configure each server using separate, clearly labeled environment variables (PROMETHEUS_SERVER_0 through PROMETHEUS_SERVER_9) so that I can easily read, understand, and modify individual server configurations without dealing with complex JSON formatting.

**Why this priority**: This is the core value proposition of the feature. Individual environment variables dramatically improve usability for the primary use case of managing multiple Prometheus servers. This provides immediate user value and can be deployed independently.

**Independent Test**: Can be fully tested by setting PROMETHEUS_SERVER_0, PROMETHEUS_SERVER_1, etc. environment variables with server configurations and verifying the MCP server loads all servers correctly using the list_servers tool.

**Acceptance Scenarios**:

1. **Given** no servers are configured, **When** I set PROMETHEUS_SERVER_0 with a valid server configuration, **Then** the MCP server loads exactly one server with the specified configuration
2. **Given** PROMETHEUS_SERVER_0 is configured, **When** I add PROMETHEUS_SERVER_1 with different server details, **Then** the MCP server loads both servers and I can query either by name
3. **Given** three indexed server variables are configured (0, 1, 2), **When** the MCP server starts, **Then** all three servers appear in the list_servers output with their respective configurations
4. **Given** PROMETHEUS_SERVER_1 and PROMETHEUS_SERVER_3 are configured, **When** PROMETHEUS_SERVER_0 and PROMETHEUS_SERVER_2 are not set, **Then** the system loads both configured servers successfully (gaps in numbering are acceptable)
5. **Given** I configure all 10 servers (PROMETHEUS_SERVER_0 through PROMETHEUS_SERVER_9), **When** the MCP server starts, **Then** all 10 servers are loaded successfully
6. **Given** only one server is needed, **When** I configure PROMETHEUS_SERVER_0, **Then** the single server is loaded correctly using the indexed format

---

### User Story 2 - Individual Server Configuration Format (Priority: P1)

As an MCP user, I need each indexed environment variable to support all server configuration fields (name, url, description, token, verify_ssl) in JSON format so that I have full control over each server's settings in a format consistent with mcp.json configuration.

**Format Example**:
```
PROMETHEUS_SERVER_0='{"name":"production","url":"https://prometheus-prod.example.com","description":"Production Server","token":"my-token","verify_ssl":true}'
PROMETHEUS_SERVER_1='{"name":"staging","url":"https://prometheus-staging.example.com","description":"Staging Server","token":"","verify_ssl":false}'
```

**Why this priority**: Defines the actual format users will work with daily. This is critical for P1 user story to be usable. Grouped with P1 as they're closely coupled.

**Independent Test**: Can be tested by setting various field combinations in indexed variables and verifying they're correctly parsed and applied when querying that specific server.

**Acceptance Scenarios**:

1. **Given** PROMETHEUS_SERVER_0 contains all fields (name, url, description, token, verify_ssl) in JSON format, **When** the server starts, **Then** all fields are correctly parsed and reflected in the server configuration
2. **Given** PROMETHEUS_SERVER_0 contains only required fields (name and url) in JSON format, **When** the server starts, **Then** the server loads with defaults for optional fields (empty token, empty description, verify_ssl=true)
3. **Given** PROMETHEUS_SERVER_0 has verify_ssl set to false in JSON, **When** checking the server connection, **Then** SSL verification is disabled for that server
4. **Given** PROMETHEUS_SERVER_5 contains a valid JSON object with all server fields, **When** the server starts, **Then** the JSON is correctly parsed into server configuration

---

### User Story 3 - Clear Error Messages for Configuration Issues (Priority: P2)

As an MCP user, I need clear error messages when my indexed server configurations are invalid so that I can quickly identify and fix configuration problems.

**Why this priority**: Enhances user experience but not blocking for core functionality. Users can still configure servers correctly with P1 working.

**Independent Test**: Can be tested by deliberately creating invalid configurations and verifying the error messages are clear and actionable.

**Acceptance Scenarios**:

1. **Given** PROMETHEUS_SERVER_0 is missing the required url field, **When** the server starts, **Then** a warning is logged indicating which server variable is invalid and which field is missing
2. **Given** PROMETHEUS_SERVER_3 contains invalid JSON, **When** the server starts, **Then** a warning is logged with the parse error and that server is skipped
3. **Given** PROMETHEUS_SERVER_0 and PROMETHEUS_SERVER_5 have the same name, **When** the server starts, **Then** a warning is logged about duplicate names and the second one is skipped or renamed
4. **Given** PROMETHEUS_SERVER_2 has an invalid verify_ssl value, **When** the server starts, **Then** it defaults to true and logs a warning
5. **Given** PROMETHEUS_SERVER_10 is configured (index out of range), **When** the server starts, **Then** a warning is logged that only indices 0-9 are supported and that server is ignored

---

### Edge Cases

- What happens when indexed variables are not sequential (e.g., SERVER_0, SERVER_3, SERVER_7 with gaps)?
  - System should load all found servers regardless of gaps (only indices 0-9 are scanned)
- What happens when indices outside the 0-9 range are used (e.g., PROMETHEUS_SERVER_10, PROMETHEUS_SERVER_15)?
  - System ignores them and logs a warning that only indices 0-9 are supported
- What happens when a server name is empty or invalid in the JSON?
  - Use the index as the name (e.g., "server-0", "server-5") or log warning and skip
- How are environment variable JSON parsing errors handled?
  - Log warning with specific parse error, skip invalid server, continue loading valid servers
- What happens when JSON is valid but missing required fields (name or url)?
  - Log warning about missing required fields, skip that server, continue loading others
- What happens when only one server is configured?
  - Single server must still use indexed format (e.g., PROMETHEUS_SERVER_0)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support server configuration via indexed environment variables named PROMETHEUS_SERVER_0 through PROMETHEUS_SERVER_9 (maximum 10 servers)
- **FR-002**: System MUST detect all indexed server variables by scanning for the pattern PROMETHEUS_SERVER_N where N is an integer from 0 to 9 inclusive
- **FR-003**: System MUST ignore any environment variables with indices outside the 0-9 range and log a warning
- **FR-004**: System MUST parse each indexed environment variable as a JSON object containing server configuration
- **FR-005**: Each indexed variable MUST support these configuration fields in JSON format: name (required), url (required), description (optional), token (optional), verify_ssl (optional)
- **FR-006**: System MUST apply sensible defaults for optional fields: empty string for token and description, true for verify_ssl
- **FR-007**: System MUST validate that each server configuration contains at minimum a name and url
- **FR-008**: System MUST handle gaps in numbering (e.g., SERVER_0, SERVER_3, SERVER_7) by loading all found servers within the 0-9 range
- **FR-009**: System MUST log warnings for invalid server configurations but continue loading valid servers
- **FR-010**: System MUST prevent duplicate server names by either skipping duplicates with warnings or auto-renaming them
- **FR-011**: System MUST support single-server deployments using the indexed format (e.g., PROMETHEUS_SERVER_0 for a single server)
- **FR-012**: System MUST load indexed server variables during the startup load_servers() function

### Key Entities

- **Server Configuration**: Represents a Prometheus server connection with fields: name (unique identifier), url (endpoint), description (human-readable label), token (authentication), verify_ssl (security setting)
- **Environment Variable Pattern**: PROMETHEUS_SERVER_N where N is an integer from 0 to 9 inclusive (maximum 10 servers), containing a JSON object with server configuration data

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can configure 10 Prometheus servers using indexed variables in under 5 minutes compared to 15+ minutes with JSON array format
- **SC-002**: Configuration readability improves as measured by users being able to identify a specific server's URL within 10 seconds (vs 60+ seconds in JSON array)
- **SC-003**: Configuration modification time reduces by 70% - users can change a single server's token in under 30 seconds
- **SC-004**: Configuration errors are detected and reported with actionable messages, reducing troubleshooting time by 50%
- **SC-005**: New users successfully configure multiple servers on first attempt 90% of the time (vs 60% with JSON array)

## Assumptions

- Users are familiar with JSON format from mcp.json configuration files
- JSON format provides sufficient readability when each server is in its own environment variable
- Environment variable limits (typically 32KB-128KB per variable) are sufficient for individual server configurations in JSON format
- 10 servers (indices 0-9) is sufficient for typical deployment scenarios
- Single-digit indices (0-9) are simpler and more manageable than larger numbers
- Zero-based indexing is familiar to technical users and aligns with programming conventions
- Most deployments will have between 2-5 Prometheus servers, with 10 being a reasonable maximum
- Users running MCP in containers or systemd services can easily set multiple environment variables
- The numbering of indexed variables doesn't need to be sequential (gaps are acceptable)
- Breaking backward compatibility is acceptable since the project has no existing users

## Dependencies

- Existing environment variable loading mechanism in load_servers() function
- Current server configuration structure (SERVERS dictionary)

## Out of Scope

- Dynamic reloading of server configurations without restart
- Configuration via files (only environment variables are supported)
- Validation of Prometheus server URLs or connection testing during configuration load
- Support for other naming patterns (e.g., PROM_SERVER_N or SERVER_N_PROMETHEUS)
- Backward compatibility with old configuration formats (PROMETHEUS_URL, PROMETHEUS_TOKEN, PROMETHEUS_SERVERS)
- Alternative formats like key-value pairs, YAML, or TOML (JSON-only)
