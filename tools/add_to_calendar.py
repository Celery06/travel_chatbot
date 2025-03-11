import os
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account
import logging
# from dotenv import load_dotenv

# load_dotenv()
GOOGLE_CALENDAR_CREDENTIALS = os.environ.get("GOOGLE_CALENDAR_CREDENTIALS", "")

tool_config = {
    "type": "function",
    "function": {
        "name": "add_to_calendar",
        "description": (
            "Takes a final hour-by-hour itinerary dict and creates each activity in Google Calendar. "
            "Expects arguments {'email':..., 'itinerary':...}. Optionally accepts a 'timeZone' string."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "The user's email (calendarId) to insert events into."
                },
                "itinerary": {
                    "type": "object",
                    "description": (
                        "Dictionary: { 'YYYY-MM-DD': { 'HH:MM': 'activity' } }, describing each day's itinerary."
                    )
                },
                "timeZone": {
                    "type": "string",
                    "description": (
                        "Optional. The time zone to be used for event creation, "
                        "e.g. 'America/New_York' or 'GMT-05'. If not provided, defaults to 'UTC'."
                    )
                }
            },
            "required": ["email", "itinerary"]
        }
    }
}


def add_to_calendar(arguments):
    """
    Iterates through 'itinerary' and creates each activity as a separate event
    in the user's Google Calendar (1-hour duration per activity).
    """

    logging.info(f"add_to_calendar called with arguments: {arguments}")

    # Handle missing keys gracefully:
    user_email = arguments.get("email")
    if not user_email:
        logging.error("Missing 'email' in add_to_calendar arguments.")
        return "Error: Missing 'email'."

    itinerary = arguments.get("itinerary")
    if not itinerary:
        logging.error("Missing 'itinerary' in add_to_calendar arguments.")
        return "Error: Missing 'itinerary'. Provide a structured itinerary before adding to calendar."

    time_zone = arguments.get("timeZone", "GMT-05")

    if not GOOGLE_CALENDAR_CREDENTIALS:
        return "Error: Google Calendar credentials not set."

    try:
        creds_info = json.loads(GOOGLE_CALENDAR_CREDENTIALS)
        creds = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build("calendar", "v3", credentials=creds)

        events_created = 0
        for date_str, hours_map in itinerary.items():
            for hour_str, activity in hours_map.items():
                start_dt = f"{date_str}T{hour_str}:00"
                end_hour = int(hour_str[:2]) + 1
                end_str = f"{end_hour:02d}:00"
                end_dt = f"{date_str}T{end_str}:00"

                event_body = {
                    "summary": f"Travel Activity: {activity}",
                    "description": "Scheduled by TravelGenie Assistant",
                    "start": {"dateTime": start_dt, "timeZone": time_zone},
                    "end": {"dateTime": end_dt, "timeZone": time_zone},
                }

                service.events().insert(
                    calendarId=user_email,
                    body=event_body,
                    sendNotifications=True
                ).execute()
                events_created += 1

        return f"Successfully created {events_created} event(s) in your calendar!"

    except Exception as e:
        logging.error(f"Error adding events to calendar: {e}")
        return f"Error adding events: {str(e)}"
    

if __name__ == "__main__":
    test_args_2 = {
        "email": "scycq2@gmail.com",
        "itinerary": {
            "2025-02-26": {
                "09:00": "Morning yoga session",
                "11:00": "Brunch at local cafe"
            }
        },
        "timeZone": "America/New_York"
    }
    result_2 = add_to_calendar(test_args_2)
    print("Test with timeZone:", result_2)
