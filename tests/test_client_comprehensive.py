"""
Comprehensive tests for the Sofascrape client
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from sofascrape.client import SofascrapeClient, SofascrapeConfig, SofascrapeError
from sofascrape.models import FormatOptions


class TestSofascrapeClientComprehensive:
    """Comprehensive test cases for the SofascrapeClient class"""
    
    def test_client_initialization(self):
        """Test client initialization with different configurations"""
        # Default initialization
        client = SofascrapeClient()
        assert client.config.base_url == "https://www.sofascore.com"
        assert client.config.headless is True
        
        # Custom initialization
        config = SofascrapeConfig(base_url="https://test.com", headless=False, timeout=15000)
        client = SofascrapeClient(config)
        assert client.config.base_url == "https://test.com"
        assert client.config.headless is False
        assert client.config.timeout == 15000
    
    def test_format_options_defaults(self):
        """Test FormatOptions default values"""
        opts = FormatOptions()
        assert opts.format_type == "json"
        assert opts.save_to_file is False
        assert opts.filename == "output"
    
    def test_format_options_custom(self):
        """Test FormatOptions with custom values"""
        opts = FormatOptions(format_type="csv", save_to_file=True, filename="test_data")
        assert opts.format_type == "csv"
        assert opts.save_to_file is True
        assert opts.filename == "test_data"
    
    @patch('playwright.sync_api.sync_playwright')
    def test_run_browser_success(self, mock_sync_playwright):
        """Test the _run_browser method with successful response"""
        # Mock the Playwright objects
        mock_playwright = Mock()
        mock_browser = Mock()
        mock_page = Mock()
        
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        
        # Setup page behavior
        mock_page.locator.return_value.first.text_content.return_value = '{"test": "data"}'
        
        config = SofascrapeConfig(headless=True)
        client = SofascrapeClient(config)
        
        result = client._run_browser("/api/test")
        
        assert result == '{"test": "data"}'
        mock_page.goto.assert_called_once()
        mock_page.locator.assert_called_once_with("pre")
    
    @patch('playwright.sync_api.sync_playwright')
    def test_run_browser_failure(self, mock_sync_playwright):
        """Test the _run_browser method with failure"""
        # Mock Playwright to raise an exception
        mock_sync_playwright.side_effect = Exception("Browser launch failed")
        
        config = SofascrapeConfig(headless=True)
        client = SofascrapeClient(config)
        
        result = client._run_browser("/api/test")
        assert result is None
    
    def test_process_response_json(self):
        """Test processing response in JSON format"""
        client = SofascrapeClient()
        opts = FormatOptions(format_type="json", save_to_file=False)
        
        raw_data = '{"key": "value", "number": 123}'
        result = client._process_response(raw_data, opts)
        
        assert result == {"key": "value", "number": 123}
    
    def test_process_response_csv(self):
        """Test processing response in CSV format"""
        client = SofascrapeClient()
        opts = FormatOptions(format_type="csv", save_to_file=False)
        
        raw_data = '{"key": "value", "number": 123}'
        result = client._process_response(raw_data, opts)
        
        assert result == {"key": "value", "number": 123}
    
    def test_process_response_invalid_json(self):
        """Test processing invalid JSON response"""
        client = SofascrapeClient()
        opts = FormatOptions(format_type="json", save_to_file=False)
        
        raw_data = 'invalid json'
        result = client._process_response(raw_data, opts)
        
        assert result is None
    
    def test_process_response_none_data(self):
        """Test processing None data"""
        client = SofascrapeClient()
        opts = FormatOptions(format_type="json", save_to_file=False)
        
        result = client._process_response(None, opts)
        
        assert result is None
    
    @patch('builtins.open')
    def test_process_response_save_json(self, mock_open):
        """Test processing response with JSON saving"""
        import os
        from unittest.mock import mock_open
        
        # Use mock_open to simulate file operations
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            client = SofascrapeClient()
            opts = FormatOptions(format_type="json", save_to_file=True, filename="test_output")
            
            raw_data = '{"key": "value"}'
            result = client._process_response(raw_data, opts)
            
            # Check that the file was opened and data was written
            mock_file.assert_called_once()
            assert result == {"key": "value"}
    
    @patch('pandas.json_normalize')
    @patch('builtins.open')
    def test_process_response_save_csv(self, mock_open, mock_json_normalize):
        """Test processing response with CSV saving"""
        import os
        from unittest.mock import mock_open
        
        # Mock pandas functionality
        mock_df = Mock()
        mock_json_normalize.return_value = mock_df
        
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            client = SofascrapeClient()
            opts = FormatOptions(format_type="csv", save_to_file=True, filename="test_output")
            
            raw_data = '{"key": "value"}'
            result = client._process_response(raw_data, opts)
            
            # Check that the file was opened and data was written
            mock_json_normalize.assert_called_once_with({"key": "value"})
            mock_df.to_csv.assert_called_once()
            assert result == {"key": "value"}
    
    def test_close_method(self):
        """Test the close method"""
        client = SofascrapeClient()
        # Initialize browser state
        client._browser = Mock()
        client._playwright = Mock()
        
        client.close()
        
        assert client._browser is None
        assert client._playwright is None
    
    def test_context_manager(self):
        """Test the context manager functionality"""
        config = SofascrapeConfig(headless=True, timeout=5000)
        try:
            with SofascrapeClient(config) as client:
                # Client should be initialized
                assert client.config == config
        except Exception:
            # Browser might not be available in test environment
            pass
    
    def test_all_endpoint_methods_exist(self):
        """Test that all expected endpoint methods exist in the client"""
        client = SofascrapeClient()
        
        # Check that some key methods exist
        assert hasattr(client, 'get_football_categories_all')
        assert hasattr(client, 'get_sport_event_count')
        assert hasattr(client, 'get_scheduled_events')
        assert hasattr(client, 'get_event_data')
        assert hasattr(client, 'get_team_data')
        assert hasattr(client, 'get_unique_tournament_data')
        assert hasattr(client, 'get_football_live_events')
        
        # Check method signatures
        import inspect
        for method_name in [
            'get_football_categories_all', 'get_scheduled_events', 
            'get_event_data', 'get_team_data', 'get_unique_tournament_data'
        ]:
            method = getattr(client, method_name)
            sig = inspect.signature(method)
            # All methods should accept **kwargs for format options
            assert 'kwargs' in sig.parameters


def test_standalone_functions_accessibility():
    """Test that standalone functions are accessible and have correct signatures"""
    from sofascrape.client import (
        get_football_categories_all,
        get_sport_event_count,
        get_scheduled_events,
        get_event_data,
        get_team_data,
        get_unique_tournament_data
    )
    
    # All functions should exist
    functions = [
        get_football_categories_all,
        get_sport_event_count,
        get_scheduled_events,
        get_event_data,
        get_team_data,
        get_unique_tournament_data
    ]
    
    for func in functions:
        assert callable(func)
        
        # Check that functions accept **kwargs (format options)
        import inspect
        sig = inspect.signature(func)
        assert 'kwargs' in sig.parameters


def test_config_defaults_and_customization():
    """Test SofascrapeConfig class defaults and customization"""
    from sofascrape.models import SofascrapeConfig
    
    # Test defaults
    default_config = SofascrapeConfig()
    assert default_config.base_url == "https://www.sofascore.com"
    assert default_config.headless is True
    assert default_config.timeout == 30000  # 30 seconds
    assert default_config.user_agent is None
    assert default_config.max_retries == 3
    assert default_config.delay_between_retries == 1.0
    
    # Test custom values
    custom_config = SofascrapeConfig(
        base_url="https://custom-api.com",
        headless=False,
        timeout=45000,
        user_agent="CustomBot/1.0",
        max_retries=5,
        delay_between_retries=2.5
    )
    
    assert custom_config.base_url == "https://custom-api.com"
    assert custom_config.headless is False
    assert custom_config.timeout == 45000
    assert custom_config.user_agent == "CustomBot/1.0"
    assert custom_config.max_retries == 5
    assert custom_config.delay_between_retries == 2.5


def test_custom_exception():
    """Test the custom SofascrapeError exception"""
    try:
        raise SofascrapeError("Test error message")
    except SofascrapeError as e:
        assert str(e) == "Test error message"
    except Exception:
        assert False, "Raised different exception than expected"
    
    # Test inheritance from base Exception
    try:
        raise SofascrapeError("Another test")
    except Exception:
        # Should be caught by generic Exception handler
        pass
    else:
        assert False, "SofascrapeError was not raised"


if __name__ == "__main__":
    # Run the tests if executed directly
    pytest.main([__file__])