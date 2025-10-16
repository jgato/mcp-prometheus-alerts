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

# Initialize FastMCP server
mcp = FastMCP("Prometheus MCP Server")

# Configuration
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "")
PROMETHEUS_TOKEN = os.getenv("PROMETHEUS_TOKEN", "")
PROMETHEUS_VERIFY_SSL = os.getenv("PROMETHEUS_VERIFY_SSL", "true").lower() in ("true", "1", "yes")


def get_headers():
    """Get headers for Prometheus API requests"""
    headers = {}
    if PROMETHEUS_TOKEN:
        headers["Authorization"] = f"Bearer {PROMETHEUS_TOKEN}"
    return headers


@mcp.tool()
async def check_prometheus_connection() -> str:
    """
    Check the connection to Prometheus server.
    
    Returns:
        str: JSON string with connection status and server information.
    """
    if not PROMETHEUS_URL:
        return '{"status": "error", "message": "PROMETHEUS_URL not configured"}'
    
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=PROMETHEUS_VERIFY_SSL) as client:
            # Try to get build info to verify connection
            response = await client.get(
                f"{PROMETHEUS_URL}/api/v1/status/buildinfo",
                headers=get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                return f'{{"status": "success", "message": "Connected to Prometheus", "build_info": {data}}}'
            else:
                return f'{{"status": "error", "message": "Failed to connect", "status_code": {response.status_code}, "details": "{response.text}"}}'
                
    except httpx.TimeoutException:
        return '{"status": "error", "message": "Connection timeout"}'
    except httpx.ConnectError as e:
        return f'{{"status": "error", "message": "Connection error: {str(e)}"}}'
    except Exception as e:
        return f'{{"status": "error", "message": "Unexpected error: {str(e)}"}}'


@mcp.tool()
async def list_alerts(state: str = "") -> str:
    """
    List all alert rules and alerts from Prometheus.
    
    This function returns all alert rules defined in the system, regardless of their current state.
    You can optionally filter by state to see only firing, pending, or inactive alerts.
    
    Args:
        state: Optional filter by alert state. Can be 'firing', 'pending', or 'inactive'.
               Leave empty to get all alert rules regardless of state.
    
    Returns:
        str: JSON string with all alert rules including:
             - Summary statistics (total rules, counts by state)
             - Alert rule groups with complete definitions
             - Rule queries, labels, annotations
             - Current state and active alerts for each rule
    """
    if not PROMETHEUS_URL:
        return '{"status": "error", "message": "PROMETHEUS_URL not configured"}'
    
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=PROMETHEUS_VERIFY_SSL) as client:
            response = await client.get(
                f"{PROMETHEUS_URL}/api/v1/rules",
                headers=get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") != "success":
                    return json.dumps({
                        "status": "error",
                        "message": "Failed to retrieve alert rules",
                        "details": data
                    })
                
                groups = data.get("data", {}).get("groups", [])
                
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
                
                result = {
                    "status": "success",
                    "filter": state if state else "all",
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
                    "status_code": response.status_code,
                    "details": response.text
                })
                
    except httpx.TimeoutException:
        return '{"status": "error", "message": "Connection timeout"}'
    except httpx.ConnectError as e:
        return json.dumps({"status": "error", "message": f"Connection error: {str(e)}"})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Unexpected error: {str(e)}"})


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()

