# Sofascrape

A Python library for scraping and interacting with SofaScore APIs to access football (soccer) statistics, events, and other sports data.

## Installation

```bash
pip install sofascrape
```

## Quick Start

### Using the Client Class (Recommended)

```python
from sofascrape import SofascrapeClient, FormatOptions

# Initialize the client
with SofascrapeClient() as client:
    # Get football categories
    categories = client.get_football_categories_all()
    print(categories)

    # Save data to a file
    options = FormatOptions(format_type="json", save_to_file=True, filename="categories")
    client.get_football_categories_all(format_type="json", save_to_file=True, filename="categories")

    # Get scheduled events for a specific date
    events = client.get_scheduled_events(date="2023-12-25")
    print(events)
```

### Using Standalone Functions (Backward Compatibility)

```python
from sofascrape import get_football_categories_all, get_scheduled_events

# Using standalone functions (returns data directly)
categories = get_football_categories_all()
print(categories)

# With formatting options
events = get_scheduled_events(date="2023-12-25", format_type="json", save_to_file=True, filename="events")
print(events)
```

## Configuration

You can customize the client behavior with configuration options:

```python
from sofascrape import SofascrapeClient, SofascrapeConfig

# Custom configuration
config = SofascrapeConfig(
    base_url="https://www.sofascore.com",
    headless=True,  # Run browser in headless mode
    timeout=30000,  # 30 seconds timeout
    user_agent="Custom User Agent",
    max_retries=3,  # Number of retry attempts
    delay_between_retries=1.0  # Delay in seconds between retries
)

client = SofascrapeClient(config)
```

## Available Methods

The library provides access to many SofaScore API endpoints:

### Football Data
- `get_football_categories_all()` - Get all football categories
- `get_sport_event_count(sport_id)` - Get event count for a sport
- `get_scheduled_events(date)` - Get scheduled events for a date
- `get_football_live_events()` - Get live football events
- `get_football_odds(provider_id, date)` - Get football odds

### Event Data
- `get_event_data(event_id)` - Get data for a specific event
- `get_event_incidents(event_id)` - Get incidents for an event
- `get_event_lineups(event_id)` - Get lineups for an event
- `get_event_h2h(event_id)` - Get head-to-head data
- `get_event_comments(event_id)` - Get comments for an event

### Team Data
- `get_team_data(team_id)` - Get data for a team
- `get_team_featured_players(team_id)` - Get featured players for a team
- `get_team_statistics_seasons(team_id)` - Get team statistics seasons

### Tournament Data
- `get_unique_tournament_data(ut_id)` - Get tournament data
- `get_tournament_standings(tournament_id, season_id)` - Get tournament standings
- `get_unique_tournament_seasons(ut_id)` - Get tournament seasons

### Player Data
- `get_player_attribute_overviews(player_id)` - Get player attribute overviews

And many more endpoints! Check the source code for a complete list.

## Format Options

You can control how data is returned and saved:

```python
from sofascrape import FormatOptions

# Default: Return data as dictionary
data = get_football_categories_all()

# Save as JSON file
data = get_football_categories_all(format_type="json", save_to_file=True, filename="categories")

# Save as CSV file
data = get_scheduled_events(date="2023-12-25", format_type="csv", save_to_file=True, filename="events")
```

## Error Handling

The library includes proper error handling for network requests and data parsing:

```python
from sofascrape import SofascrapeClient

try:
    with SofascrapeClient() as client:
        data = client.get_football_categories_all()
        if data:
            print(f"Retrieved {len(data)} categories")
        else:
            print("No data retrieved")
except Exception as e:
    print(f"Error occurred: {e}")
```

## Development

### Building the Package

To build the package locally:

```bash
pip install build
python -m build
```

### Uploading to PyPI

To upload to TestPyPI or PyPI:

```bash
# First, build the package
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

Or use the provided upload script:

```bash
python upload_package.py
```

### Running Tests

```bash
pip install -e .[dev]
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This library is intended for educational and personal use. Please respect SofaScore's terms of service and rate limits when using this library. The authors are not responsible for any misuse of this library.