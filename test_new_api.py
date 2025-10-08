#!/usr/bin/env python3
"""
Test script to verify the new API works as requested
"""

def test_new_api():
    print("Testing the new API...")
    
    try:
        from sofascrape import SofascoreClient

        # Use context manager for automatic resource management
        client = SofascoreClient()
        print("Client instantiated successfully!")

        # Test that we can access methods (without actually calling them to avoid HTTP requests)
        print(f"Available method: {hasattr(client, 'get_sport_categories')}")
        
        # Close the client
        client.close()
        print("Test successful - instantiation works!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_api()