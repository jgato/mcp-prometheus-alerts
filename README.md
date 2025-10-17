# Prometheus MCP Server

A Model Context Protocol (MCP) server for interacting with Prometheus monitoring system.

> **⚠️ Disclaimer**  
> This is a beta project and my first MCP implementation. I'm learning and experimenting with the Model Context Protocol while building something to address specific functional needs. If you're looking for a mature, production-ready solution, you may want to explore other established MCP projects in the ecosystem. Project developed together with Cursor and Cloude-4.5-sonnet.

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

The server supports two configuration modes:

### Single Server Configuration (Backward Compatible)

For a single Prometheus server, use these environment variables:

- `PROMETHEUS_URL`: The base URL of your Prometheus server (e.g., `https://prometheus.example.com`)
- `PROMETHEUS_TOKEN`: Bearer token for authentication (optional, if your Prometheus requires auth)
- `PROMETHEUS_VERIFY_SSL`: Set to `false` to disable SSL certificate verification for self-signed certificates (default: `true`)

### Multiple Server Configuration

For multiple Prometheus servers, use the `PROMETHEUS_SERVERS` environment variable with a JSON array:

```bash
export PROMETHEUS_SERVERS='[
  {
    "name": "production",
    "description": "Production Prometheus Server",
    "url": "https://prometheus-prod.example.com",
    "token": "prod-bearer-token",
    "verify_ssl": true
  },
  {
    "name": "staging",
    "description": "Staging Prometheus Server",
    "url": "https://prometheus-staging.example.com",
    "token": "staging-bearer-token",
    "verify_ssl": false
  },
  {
    "name": "development",
    "description": "Development Prometheus Server",
    "url": "https://prometheus-dev.example.com",
    "token": "",
    "verify_ssl": true
  }
]'
```

Each server configuration includes:
- `name` (required): Unique identifier for the server
- `description` (optional): Human-readable description
- `url` (required): Base URL of the Prometheus server
- `token` (optional): Bearer token for authentication
- `verify_ssl` (optional): Whether to verify SSL certificates (default: `true`)

**Note:** See `servers-config-example.json` for a formatted example of the JSON configuration.

## Usage

### Running the Server

```bash
python prometheus_mcp.py
```

### Using with MCP Client

#### Single Server Configuration

Add to your MCP client configuration (e.g., `~/.cursor/mcp.json`):

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

#### Multiple Server Configuration

For multiple servers, use the `PROMETHEUS_SERVERS` environment variable:

```json
{
  "mcpServers": {
    "prometheus": {
      "command": "python",
      "args": ["/path/to/prometheus-alerts-mcp/prometheus_mcp.py"],
      "env": {
        "PROMETHEUS_SERVERS": "[{\"name\":\"production\",\"description\":\"Production Server\",\"url\":\"https://prometheus-prod.example.com\",\"token\":\"prod-token\",\"verify_ssl\":true},{\"name\":\"staging\",\"description\":\"Staging Server\",\"url\":\"https://prometheus-staging.example.com\",\"token\":\"staging-token\",\"verify_ssl\":false}]"
      }
    }
  }
}
```

## Available Tools

### list_servers

List all configured Prometheus servers.

**Returns:** JSON string with list of available servers and their configurations, including:
- Server name
- Description
- URL
- Whether authentication token is configured
- SSL verification setting

### check_prometheus_connection

Check the connection to a Prometheus server and retrieve build information.

**Parameters:**
- `server_name` (optional): Name of the server to check. If empty, uses the first configured server.

**Returns:** JSON string with connection status and server information.

**Example usage:**
```python
# Check default/first server
check_prometheus_connection()

# Check specific server
check_prometheus_connection(server_name="production")
```

### list_alerts

List all alert rules from Prometheus with optional filtering by state.

This function returns all alert rules defined in the system, regardless of their current state. You can optionally filter to see only specific states.

**Parameters:**
- `server_name` (optional): Name of the server to query. If empty, uses the first configured server.
- `state` (optional): Filter by alert state. Can be 'firing', 'pending', or 'inactive'. Leave empty to get all alert rules.

**Returns:** JSON string with all alert rules including:
- Server name and description
- Summary statistics (total rules, firing, pending, inactive counts)
- Applied filter
- Alert rule groups with complete definitions
- Rule queries, labels, annotations
- Current state and active alerts for each rule

**Example usage:**
```python
# List all alerts from default server
list_alerts()

# List all alerts from specific server
list_alerts(server_name="production")

# List only firing alerts from specific server
list_alerts(server_name="production", state="firing")

# List only firing alerts from default server
list_alerts(state="firing")
```

### Example: Comparing Alerts Across Multiple Servers

You can easily compare if specific alerts exist across different Prometheus servers:

![Comparing alerts across multiple servers](pics/multiserver_compare_alerts.png)

This example shows checking whether the same Kubernetes persistent volume alerts exist on different servers (vsno5 and vsno7), helping you identify configuration differences between environments.

You can also combine different filters for more advanced results:

![Using different filters with multiple servers](pics/multiserver_filters.png)

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

and Cursor with claude-4.5-sonnet