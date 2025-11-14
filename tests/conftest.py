"""
Pytest configuration and shared fixtures for prometheus_mcp tests.

This module provides reusable fixtures for testing the indexed server
configuration loading functionality.
"""

import pytest
import prometheus_mcp


@pytest.fixture
def mock_env(monkeypatch):
    """
    Clean environment fixture that clears any existing PROMETHEUS_SERVER_* variables.
    
    Usage:
        def test_something(mock_env):
            mock_env.setenv('PROMETHEUS_SERVER_0', '{"name":"test","url":"http://..."}')
    """
    # Clear any existing PROMETHEUS_SERVER_* variables (0-19 for safety)
    for i in range(20):
        monkeypatch.delenv(f"PROMETHEUS_SERVER_{i}", raising=False)
    return monkeypatch


@pytest.fixture(autouse=True)
def reset_servers():
    """
    Automatically reset the global SERVERS dict before and after each test.
    
    This ensures test isolation by clearing server state between tests.
    Uses autouse=True to run automatically for all tests.
    """
    prometheus_mcp.SERVERS = {}
    yield
    prometheus_mcp.SERVERS = {}


@pytest.fixture
def sample_server_config():
    """
    Provide a sample valid server configuration for use in tests.
    
    Returns:
        dict: A complete server configuration with all fields.
    """
    return {
        "name": "test-server",
        "url": "https://prometheus.example.com",
        "description": "Test Prometheus Server",
        "token": "test-bearer-token-123",
        "verify_ssl": True
    }


@pytest.fixture
def minimal_server_config():
    """
    Provide a minimal valid server configuration (required fields only).
    
    Returns:
        dict: Server configuration with only name and url.
    """
    return {
        "name": "minimal-server",
        "url": "http://localhost:9090"
    }


@pytest.fixture
def capture_warnings(capfd):
    """
    Fixture to capture warning messages printed to stdout.
    
    Usage:
        def test_warning(mock_env, capture_warnings):
            # ... code that prints warnings ...
            warnings = capture_warnings()
            assert "Warning:" in warnings
    
    Returns:
        function: A callable that returns captured stdout as a string.
    """
    def _capture():
        captured = capfd.readouterr()
        return captured.out
    return _capture

