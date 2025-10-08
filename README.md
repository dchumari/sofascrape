# Sofascrape

A Python library for scraping and interacting with SofaScore APIs to access football (soccer) statistics, events, and other sports data.

## Installation

```bash
pip install sofascrape
```

## Quick Start

### Using the Client Class (New Simple Method)

```python
from sofascrape import SofascoreClient

# Use directly without context manager
client = SofascoreClient()

# Get football categories
categories = client.get_sport_categories()
print(categories.data)  # Access raw data

# Save as JSON file
categories.json("football_categories.json")

# Save as CSV file
categories.csv("football_categories.csv")
```

### Using the Client Class (Original Context Manager Method - Still Supported)

```python
from sofascrape import SofascoreClient

# Initialize the client with context manager (optional, but ensures cleanup)
with SofascoreClient() as client:
    # Get football categories
    categories = client.get_sport_categories()
    print(categories)

    # Save data to a file
    categories.json("categories.json")
    categories.csv("categories.csv")
```

## Available Methods

The library provides access to many SofaScore API endpoints:

### Sport Data
- `get_sport_categories()` - Get all sport categories
- `get_sport_event_count(sport_id)` - Get event count for a sport
- `get_sport_scheduled_events(date)` - Get scheduled events for a date
- `get_live_events()` - Get live events
- `get_newly_added_events()` - Get newly added events

### Event Data
- `get_event_data(event_id)` - Get data for a specific event
- `get_event_incidents(event_id)` - Get incidents for an event
- `get_event_lineups(event_id)` - Get lineups for an event
- `get_event_h2h(event_id)` - Get head-to-head data
- `get_event_comments(event_id)` - Get comments for an event
- `get_event_ai_insights(event_id, language="en")` - Get AI-generated match insights
- `get_event_pregame_form(event_id)` - Get pregame form for an event
- `get_event_managers(event_id)` - Get managers for an event
- `get_event_highlights(event_id)` - Get video highlights for an event
- `get_event_votes(event_id)` - Get votes/polls for an event

### Team Data
- `get_team_info(team_id)` - Get core information about a specific team
- `get_team_featured_players(team_id)` - Get featured players for a team
- `get_team_statistics_seasons(team_id)` - Get available seasons for team statistics
- `get_team_statistics(team_id, ut_id, season_id)` - Get team statistics for a specific tournament and season

### Tournament Data
- `get_unique_tournament_info(ut_id)` - Get core information about a specific unique tournament
- `get_unique_tournament_seasons(ut_id)` - Get all seasons for a specific unique tournament
- `get_tournament_standings(tournament_id, season_id)` - Get standings for a specific tournament and season
- `get_tournament_standings_by_type(ut_id, season_id, standings_type="total")` - Get tournament standings by type (total, home, away)
- `get_tournament_events_last(ut_id, season_id, offset=0)` - Get last events from a tournament season
- `get_tournament_events_next(ut_id, season_id, offset=0)` - Get next events from a tournament season
- `get_tournament_top_players(ut_id, season_id)` - Get top players for a tournament season
- `get_tournament_top_teams(ut_id, season_id)` - Get top teams for a tournament season
- `get_tournament_rounds(ut_id, season_id)` - Get rounds for a tournament season
- `get_tournament_events_by_round(ut_id, season_id, round_number)` - Get events for a specific round in a tournament season
- `get_tournament_cuptrees(ut_id, season_id)` - Get cup tree structure for a specific tournament and season

### Betting and Odds
- `get_odds_providers(country_code)` - Get odds providers for a specific country
- `get_branding_providers(country_code)` - Get branding data for odds providers in a specific country
- `get_event_winning_odds(event_id, provider_id)` - Get winning odds for a specific event and provider
- `get_event_featured_odds(event_id, provider_id)` - Get featured odds for a specific event and provider
- `get_event_all_odds(event_id, provider_id)` - Get all odds for a specific event and provider
- `get_team_streaks_betting_odds(event_id, provider_id)` - Get team streaks for betting odds

### Player Data
- `get_player_attributes(player_id)` - Get attributes for a specific player

### Other Methods
- `get_event_tv_channels(event_id, country_code)` - Get TV channels for a specific event in a country
- `get_event_win_probability(event_id)` - Get win probability graph data for a specific event
- `get_event_graph(event_id)` - Get graph data for a specific event

## Saving Data

All API responses support saving as JSON or CSV format:

```python
from sofascrape import SofascoreClient

client = SofascoreClient()

# Get data
categories = client.get_sport_categories()

# Save as JSON
categories.json("football_categories.json")

# Save as CSV
categories.csv("football_categories.csv")

# Access raw data
raw_data = categories.data
```

## Error Handling

The library includes proper error handling for network requests and data parsing:

```python
from sofascrape import SofascoreClient

# Direct instantiation
client = SofascoreClient()

try:
    data = client.get_sport_categories()
    if data:
        print(f"Retrieved {len(data)} categories")
        # Access raw data: data.data
    else:
        print("No data retrieved")
except Exception as e:
    print(f"Error occurred: {e}")
finally:
    client.close()  # Ensure resources are cleaned up
```

## Development

### Building the Package

To build the package locally:

```bash
pip install build
python -m build
```

### Uploading to PyPI

To upload to TestPyPI or PyPI, you'll need to set up environment variables first:

```bash
# Set your PyPI tokens as environment variables:

# On Windows Command Prompt:
set PYPI_API_TOKEN=pypi-your-pypi-token-here
set TESTPYPI_API_TOKEN=pypi-your-testpypi-token-here

# On Windows PowerShell:
$env:PYPI_API_TOKEN="pypi-your-pypi-token-here"
$env:TESTPYPI_API_TOKEN="pypi-your-testpypi-token-here"

# Then build and upload:
python -m build
python -m twine upload --repository testpypi dist/*  # for TestPyPI
python -m twine upload dist/*  # for PyPI
```

Or use the provided upload script after setting the environment variables:

```bash
python upload_to_pypi.py
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