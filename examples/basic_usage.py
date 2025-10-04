"""
Basic usage examples for the Sofascrape library
"""
from sofascrape import SofascrapeClient, FormatOptions


def main():
    """
    Example of how to use the Sofascrape library
    """
    print("Starting Sofascrape example...")
    
    # Method 1: Using the client class (recommended)
    print("\n1. Using the client class:")
    with SofascrapeClient() as client:
        # Get football categories
        categories = client.get_football_categories_all()
        if categories:
            print(f"Retrieved {len(categories.get('categories', []))} football categories")
        else:
            print("Failed to retrieve categories")
        
        # Get today's scheduled events (replace with actual date)
        events = client.get_scheduled_events(date="2023-12-25")  # Use a date that has events
        if events:
            print(f"Retrieved scheduled events: {type(events)}")
        else:
            print("No scheduled events found or failed to retrieve")
    
    # Method 2: Using standalone functions (for backward compatibility)
    print("\n2. Using standalone functions:")
    from sofascrape.client import (
        get_football_categories_all, 
        get_sport_event_count
    )
    
    categories = get_football_categories_all()
    if categories:
        print(f"Retrieved categories with standalone function: {len(categories.get('categories', []))} items")
    
    # Get event count for sport ID 1 (football)
    event_count = get_sport_event_count(sport_id=1)
    if event_count:
        print(f"Retrieved event count: {event_count}")
    
    # Method 3: With formatting options
    print("\n3. Using formatting options:")
    options = FormatOptions(format_type="json", save_to_file=True, filename="example_categories")
    categories_with_save = get_football_categories_all(
        format_type="json", 
        save_to_file=True, 
        filename="example_categories"
    )
    print("Categories saved to file if successful")
    
    print("\nExample completed!")


if __name__ == "__main__":
    main()