#!/usr/bin/env python3
"""
Prometheus MCP Server
A Model Context Protocol server for interacting with Prometheus

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
"""

import os
import json
import httpx
from mcp.server.fastmcp import FastMCP
from typing import Dict, Optional

# Initialize FastMCP server
mcp = FastMCP("Prometheus MCP Server")

# Global dictionary to store server configurations
# Key: server name (string), Value: server config dict
# This dictionary is populated by load_servers() during module initialization
SERVERS: Dict[str, dict] = {}


def parse_verify_ssl(value):
    """
    Parse verify_ssl field from various formats to boolean.
    
    Args:
        value: Boolean, string ("true"/"false"/"yes"/"1"/etc), or other type
        
    Returns:
        bool: True or False
        
    Examples:
        parse_verify_ssl(True) -> True
        parse_verify_ssl("true") -> True
        parse_verify_ssl("false") -> False
        parse_verify_ssl("yes") -> True
        parse_verify_ssl("1") -> True
        parse_verify_ssl(123) -> True (with warning)
    """
    # Handle None - default to True
    if value is None:
        return True
    
    # Handle boolean directly
    if isinstance(value, bool):
        return value
    
    # Handle string values
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes")
    
    # Invalid type - default to True with warning
    print(f"Warning: Invalid verify_ssl value type {type(value).__name__}, defaulting to True")
    return True


def load_servers():
    """
    Load Prometheus server configurations from indexed environment variables.
    
    This function implements a zero-based indexed configuration system that allows
    up to 10 Prometheus servers to be configured via separate environment variables.
    
    Indexing Strategy:
    - Uses zero-based indexing (0-9) following programming conventions
    - Scans PROMETHEUS_SERVER_0 through PROMETHEUS_SERVER_9
    - Gaps in numbering are allowed (e.g., 0, 3, 7 configured, 1-2, 4-6, 8-9 empty)
    - Out-of-range indices (10+) are detected and warned about
    
    Environment variable format:
        PROMETHEUS_SERVER_N='{"name":"server","url":"https://...","description":"...","token":"...","verify_ssl":true}'
    
    Where N is an integer from 0 to 9 (maximum 10 servers).
    
    Error Handling:
    - Invalid JSON: Warning logged, server skipped, other servers continue loading
    - Missing required fields (name/url): Warning logged, server skipped
    - Duplicate server names: Warning logged, last definition wins
    - Invalid verify_ssl: Warning logged, defaults to True
    
    The function populates the global SERVERS dictionary with successfully parsed
    configurations. Servers are keyed by their 'name' field.
    """
    global SERVERS
    SERVERS = {}
    
    # First pass: Check for out-of-range indices (10-99) to help users identify misconfigurations
    # This proactive check prevents silent failures when users accidentally use 1-based indexing
    for i in range(10, 100):
        var_name = f"PROMETHEUS_SERVER_{i}"
        if os.getenv(var_name):
            print(f"Warning: {var_name} is out of range (valid indices: 0-9). This server will be ignored.")
    
    # Main scanning loop: Iterate through valid indices 0-9
    # Using range(10) provides exactly indices 0, 1, 2, ..., 9
    for i in range(10):
        var_name = f"PROMETHEUS_SERVER_{i}"
        config_json = os.getenv(var_name)
        
        # Skip empty slots - this allows gaps in server numbering
        # Example: User can configure servers 0, 3, 7 and skip 1, 2, 4, 5, 6, 8, 9
        if not config_json:
            continue
        
        # T034: Parse JSON with descriptive error handling
        try:
            config = json.loads(config_json)
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse {var_name}: {e}")
            continue
        
        # T035: Validate required fields with specific warnings
        name = config.get('name')
        url = config.get('url')
        
        missing_fields = []
        if not name:
            missing_fields.append('name')
        if not url:
            missing_fields.append('url')
        
        if missing_fields:
            if len(missing_fields) == 1:
                print(f"Warning: {var_name} missing required field '{missing_fields[0]}'. Skipping this server.")
            else:
                print(f"Warning: {var_name} missing required fields {missing_fields}. Skipping this server.")
            continue
        
        # T036: Check for duplicate server names
        if name in SERVERS:
            print(f"Warning: Duplicate server name '{name}' found in {var_name}. "
                  f"Previous definition will be overwritten.")
        
        # T016: Build server configuration with defaults
        server_config = {
            "name": name,
            "url": url,
            "description": config.get('description', ''),
            "token": config.get('token', ''),
            "verify_ssl": parse_verify_ssl(config.get('verify_ssl', True))
        }
        
        # T039: Add to SERVERS dict (graceful continuation - errors don't stop loading)
        SERVERS[name] = server_config

# Load servers on startup
load_servers()


def get_server(server_name: Optional[str] = None) -> Optional[dict]:
    """Get server configuration by name"""
    if not SERVERS:
        return None
    
    # If no server name specified, use the first available server
    if not server_name:
        return next(iter(SERVERS.values()))
    
    return SERVERS.get(server_name)


def get_headers(token: str = "") -> dict:
    """Get headers for Prometheus API requests"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


@mcp.tool()
async def list_servers() -> str:
    """
    List all configured Prometheus servers.
    
    Returns:
        str: JSON string with list of available servers and their configurations.
    """
    if not SERVERS:
        return json.dumps({
            "status": "error",
            "message": "No Prometheus servers configured"
        })
    
    servers_info = []
    for name, config in SERVERS.items():
        servers_info.append({
            "name": config["name"],
            "description": config["description"],
            "url": config["url"],
            "has_token": bool(config["token"]),
            "verify_ssl": config["verify_ssl"]
        })
    
    return json.dumps({
        "status": "success",
        "total_servers": len(servers_info),
        "servers": servers_info
    }, indent=2)


@mcp.tool()
async def check_prometheus_connection(server_name: str = "") -> str:
    """
    Check the connection to a Prometheus server.
    
    Args:
        server_name: Name of the server to check. If empty, uses the first configured server.
    
    Returns:
        str: JSON string with connection status and server information.
    """
    server = get_server(server_name if server_name else None)
    if not server:
        available = ", ".join(SERVERS.keys()) if SERVERS else "none"
        return json.dumps({
            "status": "error",
            "message": f"Server '{server_name}' not found" if server_name else "No servers configured",
            "available_servers": available
        })
    
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=server["verify_ssl"]) as client:
            # Try to get build info to verify connection
            response = await client.get(
                f"{server['url']}/api/v1/status/buildinfo",
                headers=get_headers(server["token"])
            )
            
            if response.status_code == 200:
                data = response.json()
                return json.dumps({
                    "status": "success",
                    "message": "Connected to Prometheus",
                    "server": server["name"],
                    "server_description": server["description"],
                    "build_info": data
                }, indent=2)
            else:
                return json.dumps({
                    "status": "error",
                    "message": "Failed to connect",
                    "server": server["name"],
                    "status_code": response.status_code,
                    "details": response.text
                })
                
    except httpx.TimeoutException:
        return json.dumps({
            "status": "error",
            "message": "Connection timeout",
            "server": server["name"]
        })
    except httpx.ConnectError as e:
        return json.dumps({
            "status": "error",
            "message": f"Connection error: {str(e)}",
            "server": server["name"]
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "server": server["name"]
        })


@mcp.tool()
async def get_alerts(server_name: str = "", state: str = "", group_name: str = "", alert_name: str = "", extended_metadata: bool = False) -> str:
    """
    Get all alert rules and alerts from Prometheus.
    
    This function returns all alert rules defined in the system, regardless of their current state.
    You can optionally filter by state, group name, and/or alert name.
    
    Args:
        server_name: Name of the server to query. If empty, uses the first configured server.
        state: Optional filter by alert state. Can be 'firing', 'pending', or 'inactive'.
               Leave empty to get all alert rules regardless of state.
        group_name: Optional filter by alert rule group name. Leave empty to get all groups.
        alert_name: Optional filter by alert name (not group name). Leave empty to get all alerts.
        extended_metadata: If True, returns full alert metadata. If False (default), returns only 
                          name, state, severity (from labels), and annotations for each alert.
    
    Returns:
        str: JSON string with alert rules. When extended_metadata is False (default):
             - Returns only: name, state, severity (from labels), annotations for each alert
             When extended_metadata is True:
             - Returns complete metadata including queries, evaluation times, health status, all labels, etc.
             Both modes include summary statistics and group information.
    """
    server = get_server(server_name if server_name else None)
    if not server:
        available = ", ".join(SERVERS.keys()) if SERVERS else "none"
        return json.dumps({
            "status": "error",
            "message": f"Server '{server_name}' not found" if server_name else "No servers configured",
            "available_servers": available
        })
    
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=server["verify_ssl"]) as client:
            response = await client.get(
                f"{server['url']}/api/v1/rules",
                headers=get_headers(server["token"])
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") != "success":
                    return json.dumps({
                        "status": "error",
                        "message": "Failed to retrieve alert rules",
                        "server": server["name"],
                        "details": data
                    })
                
                groups = data.get("data", {}).get("groups", [])
                
                # Filter by group name if specified
                if group_name:
                    groups = [g for g in groups if g.get("name") == group_name]
                
                # Filter by alert name if specified
                if alert_name:
                    filtered_groups = []
                    for group in groups:
                        filtered_rules = []
                        for rule in group.get("rules", []):
                            if rule.get("type") == "alerting" and rule.get("name") == alert_name:
                                filtered_rules.append(rule)
                        
                        if filtered_rules:
                            filtered_group = group.copy()
                            filtered_group["rules"] = filtered_rules
                            filtered_groups.append(filtered_group)
                    
                    groups = filtered_groups
                
                # Filter by state if specified
                if state:
                    state_lower = state.lower()
                    filtered_groups = []
                    
                    for group in groups:
                        filtered_rules = []
                        for rule in group.get("rules", []):
                            if rule.get("type") == "alerting":
                                rule_state = rule.get("state", "inactive").lower()
                                if rule_state == state_lower:
                                    filtered_rules.append(rule)
                        
                        if filtered_rules:
                            filtered_group = group.copy()
                            filtered_group["rules"] = filtered_rules
                            filtered_groups.append(filtered_group)
                    
                    groups = filtered_groups
                
                # Count and organize rules
                total_rules = 0
                total_alerts = 0
                firing_count = 0
                pending_count = 0
                inactive_count = 0
                
                for group in groups:
                    for rule in group.get("rules", []):
                        if rule.get("type") == "alerting":
                            total_rules += 1
                            rule_state = rule.get("state", "inactive")
                            if rule_state == "firing":
                                firing_count += 1
                            elif rule_state == "pending":
                                pending_count += 1
                            else:
                                inactive_count += 1
                            
                            # Count active alerts for this rule
                            alerts = rule.get("alerts", [])
                            total_alerts += len(alerts)
                
                # Strip down to minimal metadata if extended_metadata is False
                if not extended_metadata:
                    simplified_groups = []
                    for group in groups:
                        simplified_rules = []
                        for rule in group.get("rules", []):
                            if rule.get("type") == "alerting":
                                labels = rule.get("labels", {})
                                simplified_rule = {
                                    "name": rule.get("name"),
                                    "state": rule.get("state"),
                                    "severity": labels.get("severity", "none"),
                                    "annotations": rule.get("annotations", {})
                                }
                                simplified_rules.append(simplified_rule)
                        
                        if simplified_rules:
                            simplified_group = {
                                "name": group.get("name"),
                                "rules": simplified_rules
                            }
                            simplified_groups.append(simplified_group)
                    
                    groups = simplified_groups
                
                result = {
                    "status": "success",
                    "server": server["name"],
                    "server_description": server["description"],
                    "filter": {
                        "state": state if state else "all",
                        "group_name": group_name if group_name else "all",
                        "alert_name": alert_name if alert_name else "all",
                        "extended_metadata": extended_metadata
                    },
                    "summary": {
                        "total_alert_rules": total_rules,
                        "firing": firing_count,
                        "pending": pending_count,
                        "inactive": inactive_count,
                        "total_active_alerts": total_alerts
                    },
                    "groups": groups
                }
                
                return json.dumps(result, indent=2)
            else:
                return json.dumps({
                    "status": "error",
                    "message": "Failed to fetch alert rules",
                    "server": server["name"],
                    "status_code": response.status_code,
                    "details": response.text
                })
                
    except httpx.TimeoutException:
        return json.dumps({
            "status": "error",
            "message": "Connection timeout",
            "server": server["name"]
        })
    except httpx.ConnectError as e:
        return json.dumps({
            "status": "error",
            "message": f"Connection error: {str(e)}",
            "server": server["name"]
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "server": server["name"]
        })


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()

