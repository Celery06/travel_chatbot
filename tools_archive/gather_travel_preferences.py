import os
import requests
import json

AIRTABLE_API_KEY = 'patssjECjwT3zpzCu.3fe17f22ad87f95df463bbdc7a0a359c5b99c0e24f473ca226a0ba47e96f9042'

tool_config = {
    "type": "function",
    "function": {
        "name": "gather_travel_preferences",
        "description": (
            "Engages in a structured, multi-round conversation with the user to "
            "gather detailed travel preferences and stores them in Airtable. "
            "If the user does not complete all rounds, partial information is still "
            "saved under the user's email record."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "User's email address (used to match/update their record)."
                },
                "user_input": {
                    "type": "string",
                    "description": (
                        "The latest response from the user. It can be empty if the user skipped."
                    )
                },
                "conversation_state": {
                    "type": "object",
                    "description": (
                        "Holds the ongoing conversation state. Must include at least: "
                        "current_round, max_rounds, preferences (dict of gathered data), "
                        "questions (the list of questions to ask)."
                    ),
                    "properties": {
                        "current_round": {
                            "type": "number",
                            "description": "Current round number (0-indexed)."
                        },
                        "max_rounds": {
                            "type": "number",
                            "description": "Maximum number of rounds (e.g., 5)."
                        },
                        "preferences": {
                            "type": "object",
                            "description": "Dictionary of all gathered user preferences so far."
                        },
                        "questions": {
                            "type": "array",
                            "description": "List of questions or prompts to guide data collection.",
                            "items": {  # ✅ Explicitly defining that it contains strings
                                "type": "string"
                            }
                        }
                    },
                    "required": ["current_round", "max_rounds", "preferences", "questions"]
                }
            },
            "required": ["email", "user_input", "conversation_state"]
        }
    }
}


def gather_travel_preferences(arguments):
    """
    Conduct a structured, multi-round conversation to gather travel preferences.
    Stores partial or final data in Airtable under the user's record identified by 'email'.

    :param arguments: dict containing:
                      - email: User's email (string)
                      - user_input: The user's latest answer or response (string)
                      - conversation_state: dict with keys:
                          current_round (int),
                          max_rounds (int),
                          preferences (dict),
                          questions (list of questions)
    :return: dict with:
             - conversation_state (updated after processing user input)
             - message (prompt or final summary)
             - is_complete (bool indicating whether data collection is finished)
    """

    email = arguments["email"]
    user_input = arguments["user_input"]
    state = arguments["conversation_state"]

    # Extract state details
    current_round = state.get("current_round", 0)
    max_rounds = state.get("max_rounds", 15)
    preferences = state.get("preferences", {})
    questions = state.get("questions", [])

    # Safety check for questions list; if empty, define default questions:
    if not questions:
        questions = [
            "What activities do you enjoy most during your travels?",
            "Do you have any dietary restrictions or preferences?",
            "How many travelers (including you) will be on this trip?",
            "Do you have any preferred travel tools (flight, train, etc.)?",
            "Are there any additional details or preferences you'd like to share?"
        ]
        state["questions"] = questions

    # If there’s a previously asked question, store the user's response
    # against that question’s index. We use current_round-1 if the user just answered question i.
    if current_round > 0 and current_round <= len(questions):
        # Save the user input as the answer to the previous question
        question_key = f"q{current_round-1}"
        preferences[question_key] = user_input.strip() if user_input else ""

    # Determine if we have more questions to ask
    if current_round < max_rounds and current_round < len(questions):
        # Ask the next question
        next_question = questions[current_round]
        state["current_round"] = current_round + 1
        state["preferences"] = preferences

        return {
            "conversation_state": state,
            "message": next_question,
            "is_complete": False
        }
    else:
        # We are done collecting (either max rounds reached or questions exhausted)

        # 1. Update conversation state as complete
        state["current_round"] = max_rounds
        state["preferences"] = preferences

        # 2. Construct a summary of preferences
        summary_list = []
        for i, q in enumerate(questions):
            answer = preferences.get(f"q{i}", "No response")
            summary_list.append(f"{q} -> {answer}")
        summary_text = "\n".join(summary_list)

        # 3. Store the preferences in Airtable under the record matching the user’s email
        _store_preferences_in_airtable(email, summary_text)

        # Return final summary
        return {
            "conversation_state": state,
            "message": "Here's a summary of your travel preferences:\n"
                       f"{summary_text}\n\n"
                       "Your preferences have been saved.",
            "is_complete": True
        }


def _store_preferences_in_airtable(email, preferences_summary):
    """
    Helper function to find the user's record by email and update the 'Preferences' field
    in Airtable. If a matching record is not found, it creates a new one.
    """

    # base_url = "https://api.airtable.com/v0/"  # base for Airtable requests
    # base_id = "appg4m5uM2BmfDTA2"            # Example base ID
    # table_name = "Table1"                     # Example table name
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # 1. Search for existing record by email
    search_url = f"https://api.airtable.com/v0/appg4m5uM2BmfDTA2/Table%201"
    params = {
        "filterByFormula": f"{{useremail}} = '{email}'"
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
                        "useremail": email,
                        "verified": "verified",
                        "preferences": preferences_summary
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
    _store_preferences_in_airtable('scycq2@gmail.com','hahahaha')