import os
import requests
# from dotenv import load_dotenv

# load_dotenv()
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY", "")

tool_config = {
    "type": "function",
    "function": {
        "name": "store_travel_preferences",
        "description": (
            "Stores or updates the user's travel preferences in Airtable, keyed by their email."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "User's email (unique identifier for record lookup)."
                },
                "preferences_summary": {
                    "type": "string",
                    "description": (
                        "Compiled or final summary of user preferences to be stored in Airtable."
                    )
                }
            },
            "required": ["email", "preferences_summary"]
        }
    }
}

def store_travel_preferences(arguments):
    """
    Stores or updates the user's travel preferences in Airtable under the record matching their email.
    If the record is not found, it creates a new one.

    :param arguments: dict containing:
                      - email (string): user's email
                      - preferences_summary (string): the final preferences summary
    :return: string indicating success or failure
    """
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # 1. Search for existing record by email
    search_url = f"https://api.airtable.com/v0/appg4m5uM2BmfDTA2/Table%201"
    params = {
        "filterByFormula": f"{{useremail}} = '{arguments['email']}'"
    }
    search_response = requests.get(search_url, headers=headers, params=params)

    if search_response.status_code != 200:
        print(f"Error searching for user record: {search_response.text}")
        return

    records = search_response.json().get("records", [])

    if len(records) > 0:
        # Record exists, update the first match
        record_id = records[0]["id"]
        update_url = f"https://api.airtable.com/v0/appg4m5uM2BmfDTA2/Table%201"
        update_data = {
            "records": [
                {
                    "id": record_id,
                    "fields": {
                        "useremail": arguments['email'],
                        "verified": "verified",
                        "preferences": arguments['preferences_summary']
                    }
                }
            ]
        }
        update_response = requests.patch(update_url, headers=headers, json=update_data)

        if update_response.status_code == 200:
            print("User preferences updated successfully.")
        else:
            print(f"Failed to update user preferences: {update_response.text}")
    else:
        print("Uable to find the record")


if __name__ == "__main__":
    store_travel_preferences({'email':'scycq2@gmail.com','preferences_summary':'hahahaha'})