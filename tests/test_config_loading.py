"""
Tests for indexed server configuration loading (PROMETHEUS_SERVER_0 to PROMETHEUS_SERVER_9).

This test module validates the load_servers() function with various configurations:
- Basic single and multiple server loading
- Gap handling in server indices
- JSON parsing and validation
- Error handling for invalid configurations
- Field validation and default application
"""

import json
import pytest
import prometheus_mcp


class TestBasicLoading:
    """Test basic indexed server loading functionality (User Story 1)."""
    
    def test_single_server_at_index_0(self, mock_env, sample_server_config):
        """T007: Test loading a single server at index 0."""
        # Setup: Configure PROMETHEUS_SERVER_0
        mock_env.setenv(
            'PROMETHEUS_SERVER_0',
            json.dumps(sample_server_config)
        )
        
        # Execute: Load servers
        prometheus_mcp.load_servers()
        
        # Assert: One server loaded with correct configuration
        assert len(prometheus_mcp.SERVERS) == 1
        assert 'test-server' in prometheus_mcp.SERVERS
        
        server = prometheus_mcp.SERVERS['test-server']
        assert server['name'] == sample_server_config['name']
        assert server['url'] == sample_server_config['url']
        assert server['description'] == sample_server_config['description']
        assert server['token'] == sample_server_config['token']
        assert server['verify_ssl'] == sample_server_config['verify_ssl']
    
    def test_multiple_servers_sequential(self, mock_env):
        """T008: Test loading multiple servers in sequential indices."""
        # Setup: Configure servers at indices 0, 1, 2
        configs = [
            {"name": "server-0", "url": "https://prom0.example.com"},
            {"name": "server-1", "url": "https://prom1.example.com"},
            {"name": "server-2", "url": "https://prom2.example.com"}
        ]
        
        for i, config in enumerate(configs):
            mock_env.setenv(f'PROMETHEUS_SERVER_{i}', json.dumps(config))
        
        # Execute
        prometheus_mcp.load_servers()
        
        # Assert: All three servers loaded
        assert len(prometheus_mcp.SERVERS) == 3
        assert 'server-0' in prometheus_mcp.SERVERS
        assert 'server-1' in prometheus_mcp.SERVERS
        assert 'server-2' in prometheus_mcp.SERVERS
        
        # Verify URLs are correct
        assert prometheus_mcp.SERVERS['server-0']['url'] == configs[0]['url']
        assert prometheus_mcp.SERVERS['server-1']['url'] == configs[1]['url']
        assert prometheus_mcp.SERVERS['server-2']['url'] == configs[2]['url']
    
    def test_three_servers_configured(self, mock_env):
        """T009: Test loading exactly three servers."""
        # Setup: Configure three servers with different attributes
        mock_env.setenv('PROMETHEUS_SERVER_0', json.dumps({
            "name": "production",
            "url": "https://prom-prod.example.com",
            "description": "Production server",
            "token": "prod-token"
        }))
        mock_env.setenv('PROMETHEUS_SERVER_1', json.dumps({
            "name": "staging",
            "url": "https://prom-staging.example.com",
            "verify_ssl": False
        }))
        mock_env.setenv('PROMETHEUS_SERVER_2', json.dumps({
            "name": "development",
            "url": "http://localhost:9090"
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        
        # Assert: Exactly three servers
        assert len(prometheus_mcp.SERVERS) == 3
        
        # Verify each server's unique attributes
        assert prometheus_mcp.SERVERS['production']['token'] == 'prod-token'
        assert prometheus_mcp.SERVERS['staging']['verify_ssl'] is False
        assert prometheus_mcp.SERVERS['development']['url'] == 'http://localhost:9090'


class TestGapHandling:
    """Test gap handling in server indices (User Story 1)."""
    
    def test_servers_with_gaps(self, mock_env):
        """T010: Test loading servers with gaps in numbering (indices 1, 3)."""
        # Setup: Configure servers at indices 1 and 3 (skip 0, 2)
        mock_env.setenv('PROMETHEUS_SERVER_1', json.dumps({
            "name": "server-1",
            "url": "https://prom1.example.com"
        }))
        mock_env.setenv('PROMETHEUS_SERVER_3', json.dumps({
            "name": "server-3",
            "url": "https://prom3.example.com"
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        
        # Assert: Only two servers loaded (gaps are OK)
        assert len(prometheus_mcp.SERVERS) == 2
        assert 'server-1' in prometheus_mcp.SERVERS
        assert 'server-3' in prometheus_mcp.SERVERS
        
        # Verify correct URLs
        assert prometheus_mcp.SERVERS['server-1']['url'] == 'https://prom1.example.com'
        assert prometheus_mcp.SERVERS['server-3']['url'] == 'https://prom3.example.com'
    
    def test_all_10_servers_configured(self, mock_env):
        """T011: Test loading all 10 servers (indices 0-9)."""
        # Setup: Configure all 10 server slots
        for i in range(10):
            mock_env.setenv(f'PROMETHEUS_SERVER_{i}', json.dumps({
                "name": f"server-{i}",
                "url": f"https://prom{i}.example.com"
            }))
        
        # Execute
        prometheus_mcp.load_servers()
        
        # Assert: All 10 servers loaded
        assert len(prometheus_mcp.SERVERS) == 10
        
        # Verify all servers present with correct names
        for i in range(10):
            server_name = f"server-{i}"
            assert server_name in prometheus_mcp.SERVERS
            assert prometheus_mcp.SERVERS[server_name]['url'] == f"https://prom{i}.example.com"
    
    def test_only_index_9_configured(self, mock_env):
        """T012: Test loading server only at highest index (9)."""
        # Setup: Configure only index 9 (all others empty)
        mock_env.setenv('PROMETHEUS_SERVER_9', json.dumps({
            "name": "last-server",
            "url": "https://prom9.example.com",
            "description": "Server at maximum index"
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        
        # Assert: Only one server loaded at index 9
        assert len(prometheus_mcp.SERVERS) == 1
        assert 'last-server' in prometheus_mcp.SERVERS
        assert prometheus_mcp.SERVERS['last-server']['url'] == 'https://prom9.example.com'
        assert prometheus_mcp.SERVERS['last-server']['description'] == 'Server at maximum index'


class TestFieldValidation:
    """Test server configuration field validation and defaults (User Story 2)."""
    
    def test_all_fields_present(self, mock_env):
        """T017: Test server config with all fields present."""
        # Setup: Configure server with all fields
        mock_env.setenv('PROMETHEUS_SERVER_0', json.dumps({
            "name": "full-server",
            "url": "https://prom.example.com",
            "description": "A complete server configuration",
            "token": "bearer-token-12345",
            "verify_ssl": True
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        
        # Assert: All fields correctly loaded
        assert len(prometheus_mcp.SERVERS) == 1
        server = prometheus_mcp.SERVERS['full-server']
        assert server['name'] == 'full-server'
        assert server['url'] == 'https://prom.example.com'
        assert server['description'] == 'A complete server configuration'
        assert server['token'] == 'bearer-token-12345'
        assert server['verify_ssl'] is True
    
    def test_only_required_fields(self, mock_env):
        """T018: Test server config with only required fields (name, url)."""
        # Setup: Configure server with only name and url
        mock_env.setenv('PROMETHEUS_SERVER_0', json.dumps({
            "name": "minimal",
            "url": "http://localhost:9090"
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        
        # Assert: Server loaded with defaults for optional fields
        assert len(prometheus_mcp.SERVERS) == 1
        server = prometheus_mcp.SERVERS['minimal']
        assert server['name'] == 'minimal'
        assert server['url'] == 'http://localhost:9090'
        assert server['description'] == ''  # Default
        assert server['token'] == ''  # Default
        assert server['verify_ssl'] is True  # Default
    
    def test_verify_ssl_false(self, mock_env):
        """T019: Test server config with verify_ssl explicitly set to false."""
        # Setup: Configure server with verify_ssl=false
        mock_env.setenv('PROMETHEUS_SERVER_0', json.dumps({
            "name": "insecure",
            "url": "https://internal-prom.local",
            "verify_ssl": False
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        
        # Assert: verify_ssl correctly set to False
        assert len(prometheus_mcp.SERVERS) == 1
        server = prometheus_mcp.SERVERS['insecure']
        assert server['verify_ssl'] is False
    
    def test_verify_ssl_string_formats(self, mock_env):
        """T020: Test verify_ssl with various string formats."""
        # Setup: Configure multiple servers with different verify_ssl string values
        mock_env.setenv('PROMETHEUS_SERVER_0', json.dumps({
            "name": "server-true-str",
            "url": "https://prom0.example.com",
            "verify_ssl": "true"
        }))
        mock_env.setenv('PROMETHEUS_SERVER_1', json.dumps({
            "name": "server-false-str",
            "url": "https://prom1.example.com",
            "verify_ssl": "false"
        }))
        mock_env.setenv('PROMETHEUS_SERVER_2', json.dumps({
            "name": "server-yes",
            "url": "https://prom2.example.com",
            "verify_ssl": "yes"
        }))
        mock_env.setenv('PROMETHEUS_SERVER_3', json.dumps({
            "name": "server-1",
            "url": "https://prom3.example.com",
            "verify_ssl": "1"
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        
        # Assert: All parsed correctly
        assert len(prometheus_mcp.SERVERS) == 4
        assert prometheus_mcp.SERVERS['server-true-str']['verify_ssl'] is True
        assert prometheus_mcp.SERVERS['server-false-str']['verify_ssl'] is False
        assert prometheus_mcp.SERVERS['server-yes']['verify_ssl'] is True
        assert prometheus_mcp.SERVERS['server-1']['verify_ssl'] is True
    
    def test_missing_required_field_name(self, mock_env):
        """T021: Test that server config without 'name' is rejected."""
        # Setup: Configure server missing 'name' field
        mock_env.setenv('PROMETHEUS_SERVER_0', json.dumps({
            "url": "https://prom.example.com",
            "description": "Server without name"
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        
        # Assert: No servers loaded (missing required field)
        assert len(prometheus_mcp.SERVERS) == 0
    
    def test_missing_required_field_url(self, mock_env):
        """T022: Test that server config without 'url' is rejected."""
        # Setup: Configure server missing 'url' field
        mock_env.setenv('PROMETHEUS_SERVER_0', json.dumps({
            "name": "no-url-server",
            "description": "Server without URL"
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        
        # Assert: No servers loaded (missing required field)
        assert len(prometheus_mcp.SERVERS) == 0


class TestErrorHandling:
    """Test error handling for invalid configurations (User Story 3)."""
    
    def test_missing_url_field_warning(self, mock_env, capture_warnings):
        """T027: Test warning when URL field is missing."""
        # Setup: Configure server without url, and one valid server
        mock_env.setenv('PROMETHEUS_SERVER_0', json.dumps({
            "name": "no-url-server"
        }))
        mock_env.setenv('PROMETHEUS_SERVER_1', json.dumps({
            "name": "valid-server",
            "url": "https://prom.example.com"
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        warnings = capture_warnings()
        
        # Assert: Warning logged and valid server loaded
        assert "Warning: PROMETHEUS_SERVER_0 missing required field 'url'" in warnings or \
               "Warning: PROMETHEUS_SERVER_0 missing required fields" in warnings
        assert len(prometheus_mcp.SERVERS) == 1
        assert 'valid-server' in prometheus_mcp.SERVERS
    
    def test_invalid_json_warning(self, mock_env, capture_warnings):
        """T028: Test warning when JSON is malformed."""
        # Setup: Configure invalid JSON and one valid server
        mock_env.setenv('PROMETHEUS_SERVER_0', '{"name":"bad-json","url":"incomplete')
        mock_env.setenv('PROMETHEUS_SERVER_1', json.dumps({
            "name": "good-server",
            "url": "https://prom.example.com"
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        warnings = capture_warnings()
        
        # Assert: Warning for JSON parse error and valid server loaded
        assert "Warning: Failed to parse PROMETHEUS_SERVER_0" in warnings
        assert len(prometheus_mcp.SERVERS) == 1
        assert 'good-server' in prometheus_mcp.SERVERS
    
    def test_duplicate_server_names(self, mock_env, capture_warnings):
        """T029: Test warning when duplicate server names detected."""
        # Setup: Configure two servers with same name
        mock_env.setenv('PROMETHEUS_SERVER_0', json.dumps({
            "name": "duplicate",
            "url": "https://prom0.example.com"
        }))
        mock_env.setenv('PROMETHEUS_SERVER_1', json.dumps({
            "name": "duplicate",
            "url": "https://prom1.example.com"
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        warnings = capture_warnings()
        
        # Assert: Warning for duplicate name
        assert "Warning: Duplicate server name 'duplicate'" in warnings or \
               "already exists" in warnings.lower()
        # Only first server loaded (or both, depending on implementation)
        assert 'duplicate' in prometheus_mcp.SERVERS
    
    def test_invalid_verify_ssl_warning(self, mock_env, capture_warnings):
        """T030: Test warning when verify_ssl has invalid type."""
        # Setup: Configure server with invalid verify_ssl (integer)
        mock_env.setenv('PROMETHEUS_SERVER_0', json.dumps({
            "name": "test-server",
            "url": "https://prom.example.com",
            "verify_ssl": 123  # Invalid type
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        warnings = capture_warnings()
        
        # Assert: Warning about invalid verify_ssl type, defaults to True
        assert "Warning: Invalid verify_ssl value type" in warnings
        assert len(prometheus_mcp.SERVERS) == 1
        server = prometheus_mcp.SERVERS['test-server']
        assert server['verify_ssl'] is True  # Defaulted to True
    
    def test_out_of_range_index_10_warning(self, mock_env, capture_warnings):
        """T031: Test warning for out-of-range index 10."""
        # Setup: Configure server at index 10 (out of range 0-9)
        mock_env.setenv('PROMETHEUS_SERVER_10', json.dumps({
            "name": "out-of-range-10",
            "url": "https://prom10.example.com"
        }))
        mock_env.setenv('PROMETHEUS_SERVER_0', json.dumps({
            "name": "valid-server",
            "url": "https://prom0.example.com"
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        warnings = capture_warnings()
        
        # Assert: Warning for out-of-range index, only valid server loaded
        assert "Warning: PROMETHEUS_SERVER_10 is out of range" in warnings or \
               "invalid index" in warnings.lower()
        assert len(prometheus_mcp.SERVERS) == 1
        assert 'valid-server' in prometheus_mcp.SERVERS
        assert 'out-of-range-10' not in prometheus_mcp.SERVERS
    
    def test_out_of_range_index_15_warning(self, mock_env, capture_warnings):
        """T032: Test warning for out-of-range index 15."""
        # Setup: Configure server at index 15 (out of range 0-9)
        mock_env.setenv('PROMETHEUS_SERVER_15', json.dumps({
            "name": "out-of-range-15",
            "url": "https://prom15.example.com"
        }))
        mock_env.setenv('PROMETHEUS_SERVER_0', json.dumps({
            "name": "valid-server",
            "url": "https://prom0.example.com"
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        warnings = capture_warnings()
        
        # Assert: Warning for out-of-range index, only valid server loaded
        assert "Warning: PROMETHEUS_SERVER_15 is out of range" in warnings or \
               "invalid index" in warnings.lower()
        assert len(prometheus_mcp.SERVERS) == 1
        assert 'valid-server' in prometheus_mcp.SERVERS
        assert 'out-of-range-15' not in prometheus_mcp.SERVERS
    
    def test_multiple_invalid_servers_continue_loading(self, mock_env, capture_warnings):
        """T033: Test that multiple invalid configs don't stop loading valid ones."""
        # Setup: Mix of valid and invalid servers
        mock_env.setenv('PROMETHEUS_SERVER_0', '{"invalid json')  # Bad JSON
        mock_env.setenv('PROMETHEUS_SERVER_1', json.dumps({
            "name": "valid-1",
            "url": "https://prom1.example.com"
        }))
        mock_env.setenv('PROMETHEUS_SERVER_2', json.dumps({
            "name": "no-url-server"  # Missing url
        }))
        mock_env.setenv('PROMETHEUS_SERVER_3', json.dumps({
            "name": "valid-2",
            "url": "https://prom3.example.com"
        }))
        
        # Execute
        prometheus_mcp.load_servers()
        warnings = capture_warnings()
        
        # Assert: Multiple warnings but valid servers loaded
        assert "Warning:" in warnings
        assert len(prometheus_mcp.SERVERS) == 2
        assert 'valid-1' in prometheus_mcp.SERVERS
        assert 'valid-2' in prometheus_mcp.SERVERS
        assert 'no-url-server' not in prometheus_mcp.SERVERS


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    pass  # Tests will be added across phases

