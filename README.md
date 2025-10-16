# Prometheus MCP Server

A Model Context Protocol (MCP) server for interacting with Prometheus monitoring system.

## Features

- Check Prometheus server connection
- Query alerts and metrics from Prometheus
- Bearer token authentication support

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your Prometheus connection:

```bash
cp .env.example .env
# Edit .env with your Prometheus URL and token
```

## Configuration

The server requires the following environment variables:

- `PROMETHEUS_URL`: The base URL of your Prometheus server (e.g., `https://prometheus.example.com`)
- `PROMETHEUS_TOKEN`: Bearer token for authentication (optional, if your Prometheus requires auth)
- `PROMETHEUS_VERIFY_SSL`: Set to `false` to disable SSL certificate verification for self-signed certificates (default: `true`)

## Usage

### Running the Server

```bash
python prometheus_mcp.py
```

### Using with MCP Client

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "prometheus": {
      "command": "python",
      "args": ["/path/to/prometheus-alerts-mcp/prometheus_mcp.py"],
      "env": {
        "PROMETHEUS_URL": "https://your-prometheus-server.com",
        "PROMETHEUS_TOKEN": "your-bearer-token",
        "PROMETHEUS_VERIFY_SSL": "false"
      }
    }
  }
}
```

## Available Tools

### check_prometheus_connection

Check the connection to the Prometheus server and retrieve build information.

**Returns:** JSON string with connection status and server information.

### list_alerts

List all alert rules from Prometheus with optional filtering by state.

This function returns all alert rules defined in the system, regardless of their current state. You can optionally filter to see only specific states.

**Parameters:**
- `state` (optional): Filter by alert state. Can be 'firing', 'pending', or 'inactive'. Leave empty to get all alert rules.

**Returns:** JSON string with all alert rules including:
- Summary statistics (total rules, firing, pending, inactive counts)
- Applied filter
- Alert rule groups with complete definitions
- Rule queries, labels, annotations
- Current state and active alerts for each rule

## Development

### Project Structure

```
prometheus-alerts-mcp/
├── prometheus_mcp.py    # Main MCP server implementation
├── requirements.txt     # Python dependencies
├── .env.example        # Example environment configuration
└── README.md           # This file
```

### Adding New Features

New tools can be added by decorating functions with `@mcp.tool()`:

```python
@mcp.tool()
async def your_new_tool(param: str) -> str:
    """Tool description"""
    # Implementation
    return result
```

## License

Apache License 2.0

Copyright 2025 Jose Gato Luis <jgato@redhat.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Author

**Jose Gato Luis**  
Email: jgato@redhat.com
