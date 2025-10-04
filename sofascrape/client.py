"""
Sofascrape API Client - Main class for interacting with SofaScore APIs
"""
import json
import inspect
import pandas as pd
import time
import random
from typing import Optional, Dict, Any, Literal
from pathlib import Path

from playwright.sync_api import sync_playwright
from .models import FormatOptions, SofascrapeConfig


class SofascrapeError(Exception):
    """Custom exception for Sofascrape-related errors"""
    pass


class SofascrapeClient:
    """Main client class for interacting with SofaScore APIs"""
    
    def __init__(self, config: Optional[SofascrapeConfig] = None):
        """
        Initialize the Sofascrape client
        
        Args:
            config: Configuration options for the client
        """
        self.config = config or SofascrapeConfig()
        self._playwright = None
        self._browser = None
    
    def __enter__(self):
        """Context manager entry"""
        self._start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def _start_browser(self):
        """Start the Playwright browser instance"""
        if self._browser is None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=self.config.headless)
    
    def _get_current_function_name(self) -> str:
        """Get the name of the calling function"""
        current_frame = inspect.currentframe()
        if current_frame is None:
            return "unknown_function"
        caller_frame = current_frame.f_back
        if caller_frame is None:
            return "unknown_function"
        return caller_frame.f_code.co_name
    
    def _run_browser(self, api_path: str) -> Optional[str]:
        """
        Run browser automation to fetch data from a specific API path
        
        Args:
            api_path: The API endpoint path to fetch
            
        Returns:
            String content from the API response or None if failed
        """
        url = f"{self.config.base_url}{api_path}"
        
        for attempt in range(self.config.max_retries):
            try:
                page = self._browser.new_page()
                
                # Set user agent if provided
                if self.config.user_agent:
                    page.set_extra_http_headers({"User-Agent": self.config.user_agent})
                
                page.goto(url, timeout=self.config.timeout)
                pre_content = page.locator("pre").first.text_content()
                
                page.close()
                return pre_content
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    print(f"Error fetching data from {url} after {self.config.max_retries} attempts: {e}")
                    return None
                else:
                    # Wait before retrying
                    time.sleep(self.config.delay_between_retries + random.uniform(0, 1))
    
    def _process_response(self, data: str, format_options: FormatOptions) -> Optional[Dict[str, Any]]:
        """
        Process the raw response data according to format options
        
        Args:
            data: Raw response data as string
            format_options: Format options for processing
            
        Returns:
            Processed data as dictionary or None if conversion fails
        """
        if data is None:
            print("No data to process.")
            return None
        
        try:
            parsed_data = json.loads(data)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return None
        
        if format_options.save_to_file:
            filename = format_options.filename
            if filename == "output":
                # Get the calling function name as filename
                frame = inspect.currentframe()
                if frame and frame.f_back:
                    filename = frame.f_back.f_code.co_name
                else:
                    filename = "default_output"
            
            # Ensure the filename is safe for filesystem
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()
            
            if format_options.format_type.lower() == "json":
                with open(f"{filename}.{format_options.format_type}", "w", encoding="utf-8") as f:
                    json.dump(parsed_data, f, ensure_ascii=True, indent=4)
                    print(f"Data saved to {filename}.{format_options.format_type}")
            
            elif format_options.format_type.lower() == "csv":
                try:
                    df = pd.json_normalize(parsed_data)
                    df.to_csv(f"{filename}.{format_options.format_type}", index=False, encoding="utf-8")
                    print(f"Data saved to {filename}.{format_options.format_type}")
                except Exception as e:
                    print(f"Failed to convert to CSV: {e}")
        else:
            return parsed_data
    
    def close(self):
        """Close the browser if it's open"""
        if self._browser:
            try:
                self._browser.close()
            except:
                pass  # Browser might already be closed
            self._browser = None
        if self._playwright:
            try:
                self._playwright.stop()
            except:
                pass  # Playwright might already be stopped
            self._playwright = None
    
    # Football endpoints
    def get_football_categories_all(self, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/sport/football/categories/all"""
        opts = FormatOptions(**kwargs)
        api_path = "/api/v1/sport/football/categories/all"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_sport_event_count(self, sport_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/sport/{sportId}/event-count"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/sport/{sport_id}/event-count"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_scheduled_events(self, date: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/sport/football/scheduled-events/{date}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/sport/football/scheduled-events/{date}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_ai_insights(self, event_id: int, language: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/ai-insights/{language}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/ai-insights/{language}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_incidents(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/incidents"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/incidents"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_pregame_form(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/pregame-form"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/pregame-form"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_h2h(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/h2h"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/h2h"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_managers(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/managers"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/managers"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_country_channels(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/tv/event/{eventId}/country-channels"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/tv/event/{event_id}/country-channels"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_team_featured_players(self, team_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/team/{teamId}/featured-players"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/team/{team_id}/featured-players"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_win_probability_graph(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/graph/win-probability"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/graph/win-probability"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_team_statistics_seasons(self, team_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/team/{teamId}/team-statistics/seasons"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/team/{team_id}/team-statistics/seasons"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_team_tournament_statistics(self, team_id: int, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/team/{teamId}/unique-tournament/{utId}/season/{seasonId}/statistics/overall"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/team/{team_id}/unique-tournament/{ut_id}/season/{season_id}/statistics/overall"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_highlights(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/highlights"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/highlights"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_lineups(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/lineups"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/lineups"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_tournament_standings(self, tournament_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/tournament/{tournamentId}/season/{seasonId}/standings/total"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/tournament/{tournament_id}/season/{season_id}/standings/total"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_comments(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/comments"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/comments"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_tournament_cuptrees(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/cuptrees"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/cuptrees"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_data(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_team_streaks_betting_odds(self, event_id: int, provider_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/team-streaks/betting-odds/{providerId}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/team-streaks/betting-odds/{provider_id}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_featured_odds(self, event_id: int, provider_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/odds/{providerId}/featured"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/odds/{provider_id}/featured"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_all_odds(self, event_id: int, provider_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/odds/{providerId}/all"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/odds/{provider_id}/all"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_winning_odds(self, event_id: int, provider_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/provider/{providerId}/winning-odds"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/provider/{provider_id}/winning-odds"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_graph(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/graph"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/graph"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_newly_added_events(self, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/newly-added-events"""
        opts = FormatOptions(**kwargs)
        api_path = "/api/v1/event/newly-added-events"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_odds_providers(self, country_code: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/odds/providers/{countryCode}/web"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/odds/providers/{country_code}/web"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_branding_providers(self, country_code: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/branding/providers/{countryCode}/web"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/branding/providers/{country_code}/web"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_tv_channel_event_votes(self, channel_id: int, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/tv/channel/{channelId}/event/{eventId}/votes"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/tv/channel/{channel_id}/event/{event_id}/votes"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_player_attribute_overviews(self, player_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/player/{playerId}/attribute-overviews"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/player/{player_id}/attribute-overviews"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_votes(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/votes"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/votes"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_video_stories(self, event_id: int, country_code: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/video-stories/country/{countryCode}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/video-stories/country/{country_code}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_extended_highlights(self, event_id: int, country_code: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/sport-video-highlights/country/{countryCode}/extended"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/sport-video-highlights/country/{country_code}/extended"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_signup_link(self, country_code: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/offers/signuplink/{countryCode}/web"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/offers/signuplink/{country_code}/web"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_average_positions(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/average-positions"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/average-positions"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_venue_data(self, venue_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/venue/{venueId}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/venue/{venue_id}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_venue_image(self, venue_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/venue/{venueId}/image"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/venue/{venue_id}/image"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_venue_near_events(self, venue_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/venue/{venueId}/near-events"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/venue/{venue_id}/near-events"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_entity_meta(self, entity_type: str, entity_id: int, language: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/seo/entity-meta/{entityType}/{entityId}/language/{language}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/seo/entity-meta/{entity_type}/{entity_id}/language/{language}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_footer_config(self, language: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/config/footer/{language}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/config/footer/{language}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_venue_next_events(self, venue_id: int, offset: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/venue/{venueId}/events/all/next/{offset}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/venue/{venue_id}/events/all/next/{offset}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_venue_last_events(self, venue_id: int, offset: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/venue/{venueId}/events/all/last/{offset}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/venue/{venue_id}/events/all/last/{offset}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_event_meta(self, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/{eventId}/meta"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/{event_id}/meta"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_seo_content(self, entity_type: str, entity_id: int, language: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/seo/content/{entityType}/{entityId}/{language}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/seo/content/{entity_type}/{entity_id}/{language}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_popular_compare_teams(self, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/popular-compare/football/team"""
        opts = FormatOptions(**kwargs)
        api_path = "/api/v1/popular-compare/football/team"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_team_data(self, team_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/team/{teamId}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/team/{team_id}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_football_seo_meta(self, language: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/seo/entity-meta/sport/football/language/{language}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/seo/entity-meta/sport/football/language/{language}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_football_seo_content(self, language: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/seo/content/sport/football/{language}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/seo/content/sport/football/{language}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_football_live_events(self, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/sport/football/events/live"""
        opts = FormatOptions(**kwargs)
        api_path = "/api/v1/sport/football/events/live"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_football_odds(self, provider_id: int, date: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/sport/football/odds/{providerId}/{date}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/sport/football/odds/{provider_id}/{date}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_calendar_data(self, year_month: str, sport_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/calendar/{yearMonth}/{sportId}/football/unique-tournaments"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/calendar/{year_month}/{sport_id}/football/unique-tournaments"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_countries_list(self, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/country/alpha2"""
        opts = FormatOptions(**kwargs)
        api_path = "/api/v1/country/alpha2"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_country_sport_priorities(self, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/config/country-sport-priorities/country"""
        opts = FormatOptions(**kwargs)
        api_path = "/api/v1/config/country-sport-priorities/country"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_country_sport_priorities_by_country(self, country_code: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/config/country-sport-priorities/country/{countryCode}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/config/country-sport-priorities/country/{country_code}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_unique_tournament_data(self, ut_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_unique_tournament_seasons(self, ut_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/seasons"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/seasons"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_unique_tournament_meta(self, ut_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/meta"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/meta"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_unique_tournament_season_info(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/info"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/info"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_unique_tournament_standings(self, ut_id: int, season_id: int, type_: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/standings/{type}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/standings/{type_}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_unique_tournament_last_events(self, ut_id: int, season_id: int, offset: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/events/last/{offset}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/events/last/{offset}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_unique_tournament_next_events(self, ut_id: int, season_id: int, offset: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/events/next/{offset}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/events/next/{offset}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_unique_tournament_cuptrees(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/cuptrees"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/cuptrees"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_unique_tournament_editors(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/editors"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/editors"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_player_of_the_season(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/player-of-the-season"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/player-of-the-season"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_player_of_the_season_race(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/player-of-the-season-race"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/player-of-the-season-race"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_unique_tournament_featured_events(self, ut_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/featured-events"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/featured-events"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_power_rankings_rounds(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/power-rankings/rounds"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/power-rankings/rounds"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_fan_rating_ranking(self, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/event/fan-rating/ranking/season/{seasonId}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/event/fan-rating/ranking/season/{season_id}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_team_of_the_week_rounds(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/team-of-the-week/rounds"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/team-of-the-week/rounds"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_tournament_video_highlight_rounds(self, country_code: str, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/sport-video-highlights/country/{countryCode}/unique-tournament/{utId}/season/{seasonId}/rounds"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/sport-video-highlights/country/{country_code}/unique-tournament/{ut_id}/season/{season_id}/rounds"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_player_statistics_types(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/player-statistics/types"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/player-statistics/types"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_team_statistics_types(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/team-statistics/types"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/team-statistics/types"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_unique_tournament_media(self, ut_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/media"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/media"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_top_players_per_game(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/top-players-per-game/all/overall"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/top-players-per-game/all/overall"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_top_teams(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/top-teams/overall"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/top-teams/overall"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_translation_description(self, id_: int, language: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/translation/description/{id}/language/{language}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/translation/description/{id_}/language/{language}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_team_events(self, ut_id: int, season_id: int, type_: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/team-events/{type}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/team-events/{type_}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_team_performance_graph_data(self, ut_id: int, season_id: int, team_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/team/{teamId}/team-performance-graph-data"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/team/{team_id}/team-performance-graph-data"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_team_goal_distributions(self, ut_id: int, season_id: int, team_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/team/{teamId}/goal-distributions"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/team/{team_id}/goal-distributions"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_top_players_overall(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/top-players/overall"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/top-players/overall"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_team_of_the_week(self, ut_id: int, season_id: int, round_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/team-of-the-week/{roundId}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/team-of-the-week/{round_id}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_tournament_rounds(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/rounds"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/rounds"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_tournament_groups(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/groups"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/groups"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_tournament_venues(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/venues"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/venues"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_tournament_events_by_round(self, ut_id: int, season_id: int, round_number: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/events/round/{roundNumber}"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/events/round/{round_number}"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_tournament_divisions(self, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/divisions"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/unique-tournament/{ut_id}/season/{season_id}/divisions"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)
    
    def get_default_unique_tournaments(self, country_code: str, **kwargs) -> Optional[Dict[str, Any]]:
        """GET /api/v1/config/default-unique-tournaments/{countryCode}/football"""
        opts = FormatOptions(**kwargs)
        api_path = f"/api/v1/config/default-unique-tournaments/{country_code}/football"
        raw_data = self._run_browser(api_path)
        return self._process_response(raw_data, opts)


# For backward compatibility - standalone functions
def get_football_categories_all(**kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/sport/football/categories/all"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_football_categories_all(**kwargs)


def get_sport_event_count(sport_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/sport/{sportId}/event-count"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_sport_event_count(sport_id, **kwargs)


def get_scheduled_events(date: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/sport/football/scheduled-events/{date}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_scheduled_events(date, **kwargs)


def get_event_ai_insights(event_id: int, language: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/ai-insights/{language}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_ai_insights(event_id, language, **kwargs)


def get_event_incidents(event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/incidents"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_incidents(event_id, **kwargs)


def get_event_pregame_form(event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/pregame-form"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_pregame_form(event_id, **kwargs)


def get_event_h2h(event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/h2h"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_h2h(event_id, **kwargs)


def get_event_managers(event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/managers"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_managers(event_id, **kwargs)


def get_event_country_channels(event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/tv/event/{eventId}/country-channels"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_country_channels(event_id, **kwargs)


def get_team_featured_players(team_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/team/{teamId}/featured-players"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_team_featured_players(team_id, **kwargs)


def get_event_win_probability_graph(event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/graph/win-probability"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_win_probability_graph(event_id, **kwargs)


def get_team_statistics_seasons(team_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/team/{teamId}/team-statistics/seasons"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_team_statistics_seasons(team_id, **kwargs)


def get_team_tournament_statistics(team_id: int, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/team/{teamId}/unique-tournament/{utId}/season/{seasonId}/statistics/overall"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_team_tournament_statistics(team_id, ut_id, season_id, **kwargs)


def get_event_highlights(event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/highlights"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_highlights(event_id, **kwargs)


def get_event_lineups(event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/lineups"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_lineups(event_id, **kwargs)


def get_tournament_standings(tournament_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/tournament/{tournamentId}/season/{seasonId}/standings/total"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_tournament_standings(tournament_id, season_id, **kwargs)


def get_event_comments(event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/comments"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_comments(event_id, **kwargs)


def get_tournament_cuptrees(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/cuptrees"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_tournament_cuptrees(ut_id, season_id, **kwargs)


def get_event_data(event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_data(event_id, **kwargs)


def get_event_team_streaks_betting_odds(event_id: int, provider_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/team-streaks/betting-odds/{providerId}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_team_streaks_betting_odds(event_id, provider_id, **kwargs)


def get_event_featured_odds(event_id: int, provider_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/odds/{providerId}/featured"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_featured_odds(event_id, provider_id, **kwargs)


def get_event_all_odds(event_id: int, provider_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/odds/{providerId}/all"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_all_odds(event_id, provider_id, **kwargs)


def get_event_winning_odds(event_id: int, provider_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/provider/{providerId}/winning-odds"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_winning_odds(event_id, provider_id, **kwargs)


def get_event_graph(event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/graph"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_graph(event_id, **kwargs)


def get_newly_added_events(**kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/newly-added-events"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_newly_added_events(**kwargs)


def get_odds_providers(country_code: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/odds/providers/{countryCode}/web"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_odds_providers(country_code, **kwargs)


def get_branding_providers(country_code: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/branding/providers/{countryCode}/web"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_branding_providers(country_code, **kwargs)


def get_tv_channel_event_votes(channel_id: int, event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/tv/channel/{channelId}/event/{eventId}/votes"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_tv_channel_event_votes(channel_id, event_id, **kwargs)


def get_player_attribute_overviews(player_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/player/{playerId}/attribute-overviews"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_player_attribute_overviews(player_id, **kwargs)


def get_event_votes(event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/votes"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_votes(event_id, **kwargs)


def get_event_video_stories(event_id: int, country_code: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/video-stories/country/{countryCode}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_video_stories(event_id, country_code, **kwargs)


def get_event_extended_highlights(event_id: int, country_code: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/sport-video-highlights/country/{countryCode}/extended"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_extended_highlights(event_id, country_code, **kwargs)


def get_signup_link(country_code: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/offers/signuplink/{countryCode}/web"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_signup_link(country_code, **kwargs)


def get_event_average_positions(event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/average-positions"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_average_positions(event_id, **kwargs)


def get_venue_data(venue_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/venue/{venueId}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_venue_data(venue_id, **kwargs)


def get_venue_image(venue_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/venue/{venueId}/image"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_venue_image(venue_id, **kwargs)


def get_venue_near_events(venue_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/venue/{venueId}/near-events"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_venue_near_events(venue_id, **kwargs)


def get_entity_meta(entity_type: str, entity_id: int, language: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/seo/entity-meta/{entityType}/{entityId}/language/{language}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_entity_meta(entity_type, entity_id, language, **kwargs)


def get_footer_config(language: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/config/footer/{language}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_footer_config(language, **kwargs)


def get_venue_next_events(venue_id: int, offset: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/venue/{venueId}/events/all/next/{offset}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_venue_next_events(venue_id, offset, **kwargs)


def get_venue_last_events(venue_id: int, offset: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/venue/{venueId}/events/all/last/{offset}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_venue_last_events(venue_id, offset, **kwargs)


def get_event_meta(event_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/{eventId}/meta"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_event_meta(event_id, **kwargs)


def get_seo_content(entity_type: str, entity_id: int, language: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/seo/content/{entityType}/{entityId}/{language}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_seo_content(entity_type, entity_id, language, **kwargs)


def get_popular_compare_teams(**kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/popular-compare/football/team"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_popular_compare_teams(**kwargs)


def get_team_data(team_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/team/{teamId}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_team_data(team_id, **kwargs)


def get_football_seo_meta(language: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/seo/entity-meta/sport/football/language/{language}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_football_seo_meta(language, **kwargs)


def get_football_seo_content(language: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/seo/content/sport/football/{language}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_football_seo_content(language, **kwargs)


def get_football_live_events(**kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/sport/football/events/live"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_football_live_events(**kwargs)


def get_football_odds(provider_id: int, date: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/sport/football/odds/{providerId}/{date}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_football_odds(provider_id, date, **kwargs)


def get_calendar_data(year_month: str, sport_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/calendar/{yearMonth}/{sportId}/football/unique-tournaments"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_calendar_data(year_month, sport_id, **kwargs)


def get_countries_list(**kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/country/alpha2"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_countries_list(**kwargs)


def get_country_sport_priorities(**kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/config/country-sport-priorities/country"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_country_sport_priorities(**kwargs)


def get_country_sport_priorities_by_country(country_code: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/config/country-sport-priorities/country/{countryCode}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_country_sport_priorities_by_country(country_code, **kwargs)


def get_unique_tournament_data(ut_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_unique_tournament_data(ut_id, **kwargs)


def get_unique_tournament_seasons(ut_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/seasons"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_unique_tournament_seasons(ut_id, **kwargs)


def get_unique_tournament_meta(ut_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/meta"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_unique_tournament_meta(ut_id, **kwargs)


def get_unique_tournament_season_info(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/info"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_unique_tournament_season_info(ut_id, season_id, **kwargs)


def get_unique_tournament_standings(ut_id: int, season_id: int, type_: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/standings/{type}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_unique_tournament_standings(ut_id, season_id, type_, **kwargs)


def get_unique_tournament_last_events(ut_id: int, season_id: int, offset: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/events/last/{offset}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_unique_tournament_last_events(ut_id, season_id, offset, **kwargs)


def get_unique_tournament_next_events(ut_id: int, season_id: int, offset: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/events/next/{offset}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_unique_tournament_next_events(ut_id, season_id, offset, **kwargs)


def get_unique_tournament_cuptrees(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/cuptrees"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_unique_tournament_cuptrees(ut_id, season_id, **kwargs)


def get_unique_tournament_editors(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/editors"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_unique_tournament_editors(ut_id, season_id, **kwargs)


def get_player_of_the_season(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/player-of-the-season"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_player_of_the_season(ut_id, season_id, **kwargs)


def get_player_of_the_season_race(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/player-of-the-season-race"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_player_of_the_season_race(ut_id, season_id, **kwargs)


def get_unique_tournament_featured_events(ut_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/featured-events"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_unique_tournament_featured_events(ut_id, **kwargs)


def get_power_rankings_rounds(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/power-rankings/rounds"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_power_rankings_rounds(ut_id, season_id, **kwargs)


def get_fan_rating_ranking(season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/event/fan-rating/ranking/season/{seasonId}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_fan_rating_ranking(season_id, **kwargs)


def get_team_of_the_week_rounds(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/team-of-the-week/rounds"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_team_of_the_week_rounds(ut_id, season_id, **kwargs)


def get_tournament_video_highlight_rounds(country_code: str, ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/sport-video-highlights/country/{countryCode}/unique-tournament/{utId}/season/{seasonId}/rounds"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_tournament_video_highlight_rounds(country_code, ut_id, season_id, **kwargs)


def get_player_statistics_types(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/player-statistics/types"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_player_statistics_types(ut_id, season_id, **kwargs)


def get_team_statistics_types(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/team-statistics/types"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_team_statistics_types(ut_id, season_id, **kwargs)


def get_unique_tournament_media(ut_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/media"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_unique_tournament_media(ut_id, **kwargs)


def get_top_players_per_game(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/top-players-per-game/all/overall"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_top_players_per_game(ut_id, season_id, **kwargs)


def get_top_teams(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/top-teams/overall"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_top_teams(ut_id, season_id, **kwargs)


def get_translation_description(id_: int, language: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/translation/description/{id}/language/{language}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_translation_description(id_, language, **kwargs)


def get_team_events(ut_id: int, season_id: int, type_: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/team-events/{type}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_team_events(ut_id, season_id, type_, **kwargs)


def get_team_performance_graph_data(ut_id: int, season_id: int, team_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/team/{teamId}/team-performance-graph-data"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_team_performance_graph_data(ut_id, season_id, team_id, **kwargs)


def get_team_goal_distributions(ut_id: int, season_id: int, team_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/team/{teamId}/goal-distributions"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_team_goal_distributions(ut_id, season_id, team_id, **kwargs)


def get_top_players_overall(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/top-players/overall"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_top_players_overall(ut_id, season_id, **kwargs)


def get_team_of_the_week(ut_id: int, season_id: int, round_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/team-of-the-week/{roundId}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_team_of_the_week(ut_id, season_id, round_id, **kwargs)


def get_tournament_rounds(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/rounds"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_tournament_rounds(ut_id, season_id, **kwargs)


def get_tournament_groups(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/groups"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_tournament_groups(ut_id, season_id, **kwargs)


def get_tournament_venues(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/venues"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_tournament_venues(ut_id, season_id, **kwargs)


def get_tournament_events_by_round(ut_id: int, season_id: int, round_number: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/events/round/{roundNumber}"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_tournament_events_by_round(ut_id, season_id, round_number, **kwargs)


def get_tournament_divisions(ut_id: int, season_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/unique-tournament/{utId}/season/{seasonId}/divisions"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_tournament_divisions(ut_id, season_id, **kwargs)


def get_default_unique_tournaments(country_code: str, **kwargs) -> Optional[Dict[str, Any]]:
    """GET /api/v1/config/default-unique-tournaments/{countryCode}/football"""
    config = SofascrapeConfig()
    with SofascrapeClient(config) as client:
        return client.get_default_unique_tournaments(country_code, **kwargs)