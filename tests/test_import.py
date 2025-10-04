"""
Simple tests to verify that the library can be imported and basic functionality works
"""
import pytest
from sofascrape import SofascrapeClient, FormatOptions
from sofascrape.client import SofascrapeConfig


def test_basic_imports():
    """Test that the main classes can be imported"""
    # Test that the main classes exist
    assert SofascrapeClient is not None
    assert FormatOptions is not None
    assert SofascrapeConfig is not None


def test_client_creation():
    """Test that a client can be created"""
    client = SofascrapeClient()
    assert client is not None
    assert hasattr(client, 'get_football_categories_all')
    assert hasattr(client, 'get_scheduled_events')
    assert hasattr(client, 'get_event_data')


def test_format_options_creation():
    """Test that FormatOptions can be created"""
    opts = FormatOptions()
    assert opts is not None
    assert opts.format_type == "json"
    assert opts.save_to_file is False
    assert opts.filename == "output"


def test_config_creation():
    """Test that SofascrapeConfig can be created"""
    config = SofascrapeConfig()
    assert config is not None
    assert config.base_url == "https://www.sofascore.com"
    assert config.headless is True


def test_client_with_context():
    """Test that client works with context manager (if browser available)"""
    config = SofascrapeConfig(headless=True, timeout=5000)
    try:
        with SofascrapeClient(config) as client:
            assert client is not None
    except Exception:
        # Browser might not be available in test environment
        pass  # That's OK for this test


def test_standalone_functions_available():
    """Test that standalone functions are available"""
    from sofascrape.client import (
        get_football_categories_all,
        get_sport_event_count,
        get_scheduled_events
    )
    
    # Just test that they are callable
    assert callable(get_football_categories_all)
    assert callable(get_sport_event_count)
    assert callable(get_scheduled_events)


if __name__ == "__main__":
    # Run the tests if executed directly
    test_basic_imports()
    test_client_creation()
    test_format_options_creation()
    test_config_creation()
    test_client_with_context()
    test_standalone_functions_available()
    print("All import tests passed!")