# Sofascrape

A Python library for scraping and interacting with SofaScore APIs to access football statistics, events, and other sports data.

## Installation

```bash
pip install sofascrape
```

## Features

- Easy access to SofaScore API endpoints
- Built-in data formatting and export capabilities (JSON, CSV)
- Context manager support for resource management
- Comprehensive coverage of SofaScore API endpoints

## Usage

### Basic Usage

```python
from sofascrape import SofascoreClient

# Use context manager for automatic resource management
with SofascoreClient() as client:
    # Get football categories
    categories = client.get_sport_categories()
    print(categories.data)  # Access raw data
    
    # Save as JSON file
    categories.json("football_categories.json")
    
    # Save as CSV file
    categories.csv("football_categories.csv")
```


## Available Methods

The library provides access to various SofaScore API endpoints:

- `get_sport_categories()` - Get all available football categories
- `get_live_events()` - Get all live football events
- `get_event_data(event_id)` - Get core data for a specific event
- `get_event_lineups(event_id)` - Get lineups for a specific event
- `get_tournament_standings(tournament_id, season_id)` - Get standings for a tournament
- `get_team_info(team_id)` - Get information about a specific team
- And many more endpoints...

For a complete list of available methods, check the client.py file.

## Response Objects

API responses are wrapped in `ApiResponse` objects that provide:

- Direct access to data via `.data`
- JSON export via `.json([filename])`
- CSV export via `.csv([filename])`
- Dictionary-like access via `[]`
- Iteration support via `iter()`
- Length via `len()`

## License

MIT License. See the [LICENSE](LICENSE) file for more details.
