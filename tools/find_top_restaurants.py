import os
import requests
from dotenv import load_dotenv

load_dotenv()
# Read the Google Maps API key from environment variables
GOOGLE_MAPS_API_KEY = os.environ["GOOGLE_MAPS_API_KEY"]

# The tool configuration
tool_config = {
    "type": "function",
    "function": {
        "name": "find_top_restaurants",
        "description": (
            "Queries the Google Maps Places API to retrieve high-rated restaurants "
            "in a specified destination based on the user's preferences (e.g., cuisine type, min rating)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "The city or area in which to search for restaurants."
                },
                "cuisine_preference": {
                    "type": "string",
                    "description": "Filters restaurants by the desired cuisine type (e.g., 'spicy', 'Italian', etc.)."
                },
                "min_rating": {
                    "type": "number",
                    "description": "Minimum rating to filter. Defaults to 4.0 if not provided."
                }
            },
            "required": ["destination", "cuisine_preference"]
        }
    }
}

def find_top_restaurants(arguments):
    """
    Queries the Google Maps Places API to retrieve high-rated restaurants 
    matching the user's preferences in a given destination.

    :param arguments: dict containing:
                      - destination (string, required)
                      - cuisine_preference (string, required)
                      - min_rating (number, optional; default 4.5)
    :return: A list (up to 5) of top restaurants, each containing:
             name, rating, address, and Google Maps link. Or an error message if any step fails.
    """

    # Extract required info
    destination = arguments.get("destination", "").strip()
    cuisine_preference = arguments.get("cuisine_preference", "").strip()
    min_rating = arguments.get("min_rating", 4.5)

    # Validate required fields
    if not destination or not cuisine_preference:
        return (
            "Missing required information. Please provide 'destination' "
            "and 'cuisine_preference'."
        )

    # Prepare the query & parameters for Google Maps Places API (Text Search)
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    query = f"{cuisine_preference} restaurant in {destination}"
    params = {
        "query": query,
        "key": GOOGLE_MAPS_API_KEY,
        "type": "restaurant"
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        if response.status_code != 200:
            return f"Error from Google Maps API: {response.text}"
        data = response.json()

        # Extract results and filter by min_rating
        results = data.get("results", [])
        # Filter restaurants that meet or exceed the min_rating
        filtered = [
            place for place in results
            if place.get("rating", 0) >= min_rating
        ]

        # Sort by rating descending
        filtered.sort(key=lambda x: x.get("rating", 0), reverse=True)

        # Take up to 5 top results
        top_restaurants = filtered[:5]

        # Build a concise list to return
        final_list = []
        for place in top_restaurants:
            final_list.append({
                "name": place.get("name", "N/A"),
                "rating": place.get("rating", "N/A"),
                "address": place.get("formatted_address", "N/A"),
                # Link uses the place_id to create a Google Maps URL
                "maps_link": f"https://www.google.com/maps/place/?q=place_id:{place['place_id']}"
            })

        # If no restaurants found, return a friendly message
        if not final_list:
            return "No restaurants found matching your criteria."

        return final_list

    except requests.exceptions.RequestException as e:
        return f"Request error: {e}"

if __name__ == "__main__":
    # Test Case 1: Valid request with all parameters
    test_args_1 = {
        "destination": "Nottingham, UK",
        "cuisine_preference": "spicy",
        "min_rating": 4.5
    }
    print("\n Test Case 1: Valid input (spicy cuisine in Nottingham)")
    result_1 = find_top_restaurants(test_args_1)
    print(result_1)