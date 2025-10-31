# Prometheus MCP Server

A Model Context Protocol (MCP) server for interacting with Prometheus monitoring system.

> **⚠️ Disclaimer**  
> This is a beta project and my first MCP implementation. I'm learning and experimenting with the Model Context Protocol while building something to address specific functional needs. If you're looking for a mature, production-ready solution, you may want to explore other established MCP projects in the ecosystem. Project developed together with Cursor and Cloude-4.5-sonnet.

## Features

- Check Prometheus server connection
- Query alerts from Prometheus
- Bearer token authentication support

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your Prometheus connection:

```bash
touch .env
# Edit .env with your Prometheus URL and token
```

## Configuration

The server supports two configuration modes:

### Single Prometheus Server Configuration (Backward Compatible)

For a single Prometheus server, use these environment variables:

- `PROMETHEUS_URL`: The base URL of your Prometheus server (e.g., `https://prometheus.example.com`)
- `PROMETHEUS_TOKEN`: Bearer token for authentication (optional, if your Prometheus requires auth)
- `PROMETHEUS_VERIFY_SSL`: Set to `false` to disable SSL certificate verification for self-signed certificates (default: `true`)

### Multiple Prometheus Server Configuration

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

### get_alerts

Get alert rules from Prometheus with optional filtering by state, group, and alert name.

This function returns all alert rules defined in the system. You can filter by state, group name, alert name, and control the level of detail returned.

**Parameters:**
- `server_name` (optional): Name of the server to query. If empty, uses the first configured server.
- `state` (optional): Filter by alert state. Can be 'firing', 'pending', or 'inactive'. Leave empty to get all alert rules.
- `group_name` (optional): Filter by alert rule group name. Leave empty to get all groups.
- `alert_name` (optional): Filter by specific alert name. Leave empty to get all alerts.
- `extended_metadata` (optional): If `False` (default), returns only essential fields (name, state, severity, annotations) for each alert, reducing response size significantly. If `True`, returns full metadata including queries, evaluation times, health status, and all labels. Use `False` for efficient context window management when querying many alerts, and `True` only when you need complete technical details for specific alerts.

**Returns:** JSON string with alert rules including:
- Server name and description
- Summary statistics (total rules, firing, pending, inactive counts)
- Applied filters
- Alert rule groups with definitions (full or simplified based on `extended_metadata`)


### Example: Comparing Alerts Across Multiple Servers

You can easily compare if specific alerts exist across different Prometheus servers:

![Comparing alerts across multiple servers](pics/multiserver_compare_alerts.png)

This example shows checking whether the same Kubernetes persistent volume alerts exist on different servers (vsno5 and vsno7), helping you identify configuration differences between environments.

You can also combine different filters for more advanced results:

![Using different filters with multiple servers](pics/multiserver_filters.png)

## Advanced queries and context windows

The MCP interacts with Prometheus Alerts API retrieving a whole json with all the queries. That could be long enough to exceed your context windows, specially when comparing multiple servers (even if we dont take the extra_metadata):

![Context window exceeded](pics/complex_prompts_context_2.png)

Instead of that, you can instruct the agent to do the inform on different steps:

![Context window not exceeded](pics/complex_prompts_context_1.png)

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