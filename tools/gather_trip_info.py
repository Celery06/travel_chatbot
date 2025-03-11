import os
import json
import requests
from googleapiclient.discovery import build
from google.oauth2 import service_account
# from dotenv import load_dotenv

# load_dotenv()
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY", "")
GOOGLE_CALENDAR_CREDENTIALS = os.environ.get("GOOGLE_CALENDAR_CREDENTIALS", "")

tool_config = {
    "type": "function",
    "function": {
        "name": "gather_trip_info",
        "description": (
            "Retrieves user travel preferences from Airtable and availability from Google Calendar. "
            "Returns the raw data, allowing AI to generate and summarize the final itinerary."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "User's email for retrieving preferences and availability."
                },
                "start_date": {
                    "type": "string",
                    "description": "Trip start date (YYYY-MM-DD)."
                },
                "end_date": {
                    "type": "string",
                    "description": "Trip end date (YYYY-MM-DD)."
                },
                "destination": {
                    "type": "string",
                    "description": "Travel destination."
                }
            },
            "required": ["email", "start_date", "end_date", "destination"]
        }
    }
}

def gather_trip_info(arguments):
    """
    - Fetches user preferences from Airtable.
    - Fetches availability from Google Calendar.
    - Returns raw data for AI processing.
    """

    email = arguments.get("email")
    start_date = arguments.get("start_date")
    end_date = arguments.get("end_date")
    destination = arguments.get("destination")

    # Step 1: Fetch user preferences
    preferences = _fetch_preferences_from_airtable(email)
    
    # Step 2: Fetch availability from Google Calendar
    availability = _check_calendar_availability(email, start_date, end_date)

    # Return structured data for AI to process
    return {
        "email": email,
        "start_date": start_date,
        "end_date": end_date,
        "destination": destination,
        "preferences": preferences,
        "availability": availability
    }

def _fetch_preferences_from_airtable(email):
    """Retrieve user preferences from Airtable."""
    base_url = "https://api.airtable.com/v0/appg4m5uM2BmfDTA2/Table%201"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    params = {"filterByFormula": f"{{useremail}}='{email}'"}
    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code != 200:
        return None

    records = response.json().get("records", [])
    return records[0]["fields"].get("preferences") if records else None

def _check_calendar_availability(email, start_date, end_date):
    """Retrieve free/busy slots from Google Calendar."""
    if not GOOGLE_CALENDAR_CREDENTIALS:
        return "Google Calendar credentials not found."

    try:
        creds_info = json.loads(GOOGLE_CALENDAR_CREDENTIALS)
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build("calendar", "v3", credentials=creds)

        request_body = {
            "timeMin": f"{start_date}T00:00:00Z",
            "timeMax": f"{end_date}T23:59:59Z",
            "items": [{"id": email}]
        }
        result = service.freebusy().query(body=request_body).execute()
        
        return _build_free_hours(start_date, end_date, result["calendars"][email]["busy"])

    except Exception as e:
        return f"Error checking availability: {str(e)}"

def _build_free_hours(start_date, end_date, busy_slots):
    """Convert busy time slots to a structured free-hours map."""
    import datetime
    fmt = "%Y-%m-%d"
    sday = datetime.datetime.strptime(start_date, fmt).date()
    eday = datetime.datetime.strptime(end_date, fmt).date()
    free_map = {
        sday.isoformat(): {f"{h:02d}:00": "free" for h in range(7, 22)}
        for sday in [sday + datetime.timedelta(days=i) for i in range((eday - sday).days + 1)]
    }

    for slot in busy_slots:
        start_dt = datetime.datetime.fromisoformat(slot["start"].replace("Z", "+00:00"))
        end_dt = datetime.datetime.fromisoformat(slot["end"].replace("Z", "+00:00"))
        for day in free_map:
            for h in range(start_dt.hour, end_dt.hour + 1):
                free_map[day][f"{h:02d}:00"] = "busy"

    return free_map

# Example usage
if __name__ == "__main__":
    test_args = {
        "email": "test@example.com",
        "start_date": "2025-06-01",
        "end_date": "2025-06-03",
        "destination": "Paris"
    }
    print(gather_trip_info(test_args))
