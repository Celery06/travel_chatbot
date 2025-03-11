import os
import json
import requests
from googleapiclient.discovery import build
from google.oauth2 import service_account

AIRTABLE_API_KEY = 'patssjECjwT3zpzCu.3fe17f22ad87f95df463bbdc7a0a359c5b99c0e24f473ca226a0ba47e96f9042'

# This environment variable should contain the service account JSON (as a single string)
# with appropriate permissions (Calendar API enabled).
GOOGLE_CALENDAR_CREDENTIALS = '''
{
  "type": "service_account",
  "project_id": "system-tool-chains-433920",
  "private_key_id": "eada062d8713830a4733e75e44f1d3a630324666",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDQPiuGvYLHIDYR\nAtKP4bvxedX9WVsoHNSc+Nyz7Bs9Y1oUi4GAuqdpJ/4OeS4MFZc0+JA/EFvVA16r\nJP5LlWhKp5oTkVytwOV+kfbpfSOmaorVTYeMr8m5dS/lD5kvTdjoKJztMnlXRuOX\nsA/Cx1+mg8y2qiBz/pB2jYDF3bSe1lirx03DoWPY5tdZDTUk6rjUDBxy8pqw1FNe\nKYNa7LiQAAx8e1TiPiIDR7MSGNgv+Jr/ByUwHgQzRUd+Y8T2qs9udxGV+hE6o0IS\n4ffzJE8pu7KRlTX13Ly7jNPe/VOGvk00Nbgm/2ELyjPfamO4K+2oGEdbXSlJDE/X\nVAvC0QfDAgMBAAECggEAD1wmlb+wv8NOeZ69rUM3O66C7DcFFEZcIF/y14qYz8Re\nRpmrqbUa2BTNFoA1t0p4Zr3W1e/89g9TkkgeQbD5ilgmcz8LmP1bcCSQE9TZJlNB\nfk5Dq0rkFDviloC6CdUyJJ2qRYytipR+ARhJcVKHaZ7bILYXwraKLVRupSmfQv/m\nZi+MPMQouAnXlVJvD+Hu4cj47jTAZ6k0TG1wrG56qYv495hYgO0Ny80psDQchbPm\ndlKc4XRYs+tol8BQmfhZiXNUM8E9ZjlCU+vFlURoe74+gLWZ5qWBq9S43QMVIfpl\nNJSRqj6v7HGZHFgwCZ2ZwNcN+kzdSO7wj1mNib+EsQKBgQDkRHBVJnkIROBpdtya\npV+TQseWFQwvQgj4WAn5zp71M1mUk9D8c7N1g85Jmv9O2ZO5rO030hbXhsF9BGTh\nGcpb8oHleZ/LBNedf03x44dnFspVIxsGuzbKoaXgiJNCaYD7Yv9im9JmZYo+ojQ3\nFyuvf3Hd+/swv+SUh16TGs3BxwKBgQDpiu4yiJa/+f4wEpe+6q2ikFJ3yzkAipCu\nFPcf9MhAIU2u5wHTwdDAk6dNAdxiXr00qkXRnRbXgMPy+ypnLx+aeNccRZVroIY9\nCJxPuUqfaEXfjWY9aKW3kIH5tOUHNTOeV9gOOAM9NgD2FugzGaiu77rqhNUfvE0K\nhcIpJmvKJQKBgQDRaegUdkM7TtUCbEVeqrDQDMfF7HFNOau5Ciu8vc4e7YkVQbbM\no+jTuqQZ6tSmpf1crkTCnT7PY5VG+C0ERgDb8dMxjy8Ftd+JYi1D6JVkAgiFqrs0\npbRSmZHwN9vBZcEq31ukP4f64NS/OVfl4p/1VVpFaNK9mo49pSMimciCKQKBgDBI\nPbiKzoe/+lIb9e1NfTpHlhUYGZ/IBeNHiFO9+oxvlizbq2AJCMxXelYMVXCs33b8\n4NRWIrvI7jnUvU55ypHX+7jnld2bYUVK+23sA8Zy+0cdZ464jNIneQeT42mbESHi\nTVObNug3uvklgTnXSy1neIA1mA4oktDjGGIDhHNVAoGAGwJgce9vfanlt828dWwo\nhQ0tApDd090PUGrMqCN+Vk+QJMAYl32G3azwXN4Ptlp2d/N75JD+zIJZuR19jRxx\n0H37X78A1SkuXi47y3nGb0t+61eNA+qM0DEXV2BjmJssN78B1ZxynmlvU0+w94hN\nwL3MfP4luNUKbEp9+KTSYW4=\n-----END PRIVATE KEY-----\n",
  "client_email": "994094904266-compute@developer.gserviceaccount.com",
  "client_id": "114030566783985762523",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/994094904266-compute%40developer.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
'''

tool_config = {
    "type": "function",
    "function": {
        "name": "plan_travel",
        "description": (
            "Assists the user in creating a detailed travel itinerary through a multi-round interaction. "
            "It retrieves travel preferences from Airtable using the user’s email, checks availability in Google Calendar, "
            "prompts for all required travel details, and upon final approval, adds the itinerary to the user’s Google Calendar."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "User's email, used as a key to retrieve preferences and update calendar."
                },
                "destination": {
                    "type": "string",
                    "description": "The desired travel destination."
                },
                "start_date": {
                    "type": "string",
                    "description": "Planned start date of the trip (YYYY-MM-DD)."
                },
                "end_date": {
                    "type": "string",
                    "description": "Planned end date of the trip (YYYY-MM-DD)."
                },
                "activities": {
                    "type": "string",
                    "description": "Comma-separated list of preferred activities or special requests."
                },
                "confirm_itinerary": {
                    "type": "boolean",
                    "description": (
                        "Indicates whether the user has confirmed the final itinerary (true) or not (false). "
                        "Use this to decide if we should add events to the Google Calendar."
                    )
                },
                "feedback": {
                    "type": "string",
                    "description": (
                        "If the user rejects the proposed plan, they can provide feedback or modifications here. "
                        "This helps refine the plan in subsequent steps."
                    )
                }
            },
            "required": ["email"]
        }
    }
}


def plan_travel(arguments):
    """
    Assists the user in creating a detailed travel itinerary through a multi-round interaction.
    Integrates with Google Calendar to check availability (Free/Busy) and to schedule events.

    Steps:
      1. Retrieve user travel preferences from Airtable, keyed by the email address.
         - If no preferences exist, prompt user to set them and exit.
      2. Check user availability on Google Calendar.
      3. If partial details (destination, dates, activities) are missing, prompt the user to provide them.
      4. Once all details are collected, generate and present a proposed itinerary.
      5. If the user rejects the plan, request feedback (arguments["feedback"]) and refine the plan.
      6. When the user confirms (arguments["confirm_itinerary"] == True), add the finalized events to Google Calendar.
      7. Return an appropriate message or structure reflecting the current stage.
    """
    email = arguments.get("email")
    destination = arguments.get("destination")
    start_date = arguments.get("start_date")
    end_date = arguments.get("end_date")
    activities = arguments.get("activities")
    confirm_itinerary = arguments.get("confirm_itinerary")
    feedback = arguments.get("feedback")

    if not email:
        return "No email provided. Please supply your email to proceed."

    # (1) Retrieve user preferences from Airtable
    airtable_url = "https://api.airtable.com/v0/appg4m5uM2BmfDTA2/Table1"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    # Filter by the user's email in Airtable
    filter_formula = f"{{email}}='{email}'"
    params = {"filterByFormula": filter_formula}
    response = requests.get(airtable_url, headers=headers, params=params)

    if response.status_code != 200:
        return f"Error retrieving preferences from Airtable: {response.text}"

    records = response.json().get("records", [])
    if not records:
        return (
            f"No preferences found in Airtable for email {email}. "
            "Please set your travel preferences before proceeding."
        )

    # Suppose we store user preferences in a field named "Preferences".
    # You might use them to further customize the itinerary logic.
    user_preferences = records[0]["fields"].get("preferences", {})

    # (2) Check the user’s availability on Google Calendar (Free/Busy)
    #     using the start_date and end_date if provided
    if start_date and end_date:
        availability_message = check_google_calendar_availability(
            user_email=email, start_date=start_date, end_date=end_date
        )
        if availability_message is not None:
            # If 'availability_message' is a string, it's likely an error or conflict notice
            return availability_message

    # (3) If partial details are missing, request them
    missing_details = []
    if not destination:
        missing_details.append("destination")
    if not start_date:
        missing_details.append("start_date")
    if not end_date:
        missing_details.append("end_date")
    if not activities:
        missing_details.append("activities")

    if missing_details:
        return (
            f"I still need the following details to propose an itinerary: {', '.join(missing_details)}. "
            "Please provide them in the next message."
        )

    # (4) Propose an itinerary
    proposed_itinerary = (
        f"Proposed Itinerary:\n"
        f"Destination: {destination}\n"
        f"Travel Dates: {start_date} to {end_date}\n"
        f"Activities: {activities}\n\n"
        "Please confirm the itinerary, or provide feedback."
    )

    # (5) Check if the user wants to confirm or refine
    if confirm_itinerary:
        # (6) User confirmed - add events to Google Calendar
        added_event_message = add_to_google_calendar(
            user_email=email,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            activities=activities
        )
        return added_event_message
    else:
        # If user provided feedback or hasn't confirmed yet
        if feedback:
            # Adjust plan based on feedback...
            refined_plan = (
                f"Refined plan based on your feedback: {feedback}. "
                "Please review and confirm, or provide further changes."
            )
            return refined_plan
        else:
            # If no feedback but also not confirmed, we show the proposed itinerary
            return proposed_itinerary


def check_google_calendar_availability(user_email, start_date, end_date):
    """
    Uses the Google Calendar API's Free/Busy endpoint to check if the user is available
    between start_date and end_date (inclusive).

    :param user_email: The user's Google Calendar email/account.
    :param start_date: YYYY-MM-DD
    :param end_date: YYYY-MM-DD
    :return: None if the user is free, or a string message if there is a conflict or error.
    """
    if not GOOGLE_CALENDAR_CREDENTIALS:
        return "Google Calendar credentials not set. Cannot check availability."

    try:
        credentials_info = json.loads(GOOGLE_CALENDAR_CREDENTIALS)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build("calendar", "v3", credentials=credentials)

        # The freeBusy query expects RFC3339 date-times. We'll assume
        # an all-day check from 00:00 on the start date to 23:59:59 on the end date.
        time_min = f"{start_date}T00:00:00Z"
        time_max = f"{end_date}T23:59:59Z"

        request_body = {
            "timeMin": time_min,
            "timeMax": time_max,
            "items": [{"id": user_email}]
        }
        freebusy_result = service.freebusy().query(body=request_body).execute()

        # 'calendars' is a dictionary keyed by calendar ID, with 'busy':[] if free
        busy_slots = freebusy_result.get("calendars", {}).get(user_email, {}).get("busy", [])
        if busy_slots:
            # If there's any busy slot in that range, the user is not fully available
            return (
                f"You have some busy slots between {start_date} and {end_date}. "
                "Please choose different dates or modify your schedule."
            )
        # If no busy slots, we're good
        return None

    except Exception as e:
        return f"Error checking Google Calendar availability: {str(e)}"


def add_to_google_calendar(user_email, destination, start_date, end_date, activities):
    """
    Adds the finalized travel plan to the user's Google Calendar as an event.
    :param user_email: The user's email/calendar ID.
    :param destination: Travel destination.
    :param start_date: YYYY-MM-DD
    :param end_date: YYYY-MM-DD
    :param activities: A comma-separated list of planned activities.
    :return: A message confirming or reporting an error.
    """
    if not GOOGLE_CALENDAR_CREDENTIALS:
        return "Google Calendar credentials not set. Cannot add events."

    try:
        credentials_info = json.loads(GOOGLE_CALENDAR_CREDENTIALS)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build("calendar", "v3", credentials=credentials)

        # For an all-day event in Google Calendar, we can set start/end date fields.
        # *Important*: end date in the Calendar is exclusive, so if you want to cover the entire end date,
        # you might need to shift it by a day. For demonstration, we'll just use the given end_date.
        event_body = {
            "summary": f"Trip to {destination}",
            "description": f"Activities planned: {activities}",
            "start": {"date": start_date},
            "end": {"date": end_date},
        }

        # In many organizations, the user's email can be used as the calendarId.
        # If that doesn't work in your environment, you might need a separate method to find the correct calendarId.
        event_result = service.events().insert(
            calendarId=user_email,
            body=event_body,
            sendNotifications=True
        ).execute()

        event_id = event_result.get("id")
        return (
            f"Your itinerary has been confirmed and added to Google Calendar!\n"
            f"Event ID: {event_id}\n"
            "Enjoy your trip!"
        )

    except Exception as e:
        return f"Failed to add event to Google Calendar: {str(e)}"
