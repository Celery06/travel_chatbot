import os
import logging

tool_config = {
    "type": "function",
    "function": {
        "name": "gather_travel_preferences_interactive",
        "description": (
            "Engages in a general, multi-round conversation to gather travel preferences. "
            "By default, provides a set of sample questions, but does NOT force strict ordering. "
            "Does NOT store data in Airtable."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "user_input": {
                    "type": "string",
                    "description": "The user's latest response (can be empty if skipped)."
                },
                "conversation_state": {
                    "type": "object",
                    "description": (
                        "Holds the ongoing conversation state. Must include at least: "
                        "current_round, max_rounds, preferences (dict of gathered data), "
                        "questions (list of questions to ask, if desired)."
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
                            "description": "Dictionary of user preference answers collected so far."
                        },
                        "questions": {
                            "type": "array",
                            "description": "Optional list of questions/prompts to help gather preferences.",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "required": ["current_round", "max_rounds", "preferences", "questions"]
                }
            },
            "required": ["user_input", "conversation_state"]
        }
    }
}

def gather_travel_preferences_interactive(arguments):
    """
    Conducts a general, multi-round conversation to gather travel preferences.
    - Uses a default set of questions if none are provided.
    - Does NOT store the data (for storage, call a separate function).
    - Continues until max_rounds or question list is exhausted, then returns a summary.

    :param arguments: dict with:
        - user_input (str): The user's latest response (can be empty).
        - conversation_state (dict):
            current_round (int),
            max_rounds (int),
            preferences (dict),
            questions (list of questions; can be empty).
    :return: dict containing:
        - conversation_state (updated with any new user response)
        - message (next question or final summary)
        - is_complete (bool indicating if we are done gathering input)
    """

    logging.info("Gathering travel preferences...")

    user_input = arguments["user_input"]
    state = arguments["conversation_state"]

    current_round = state.get("current_round", 0)
    max_rounds = state.get("max_rounds", 6)
    preferences = state.get("preferences", {})
    questions = state.get("questions", [])

    # If no questions provided, use a default set of example questions
    if not questions:
        questions = [
            "What activities do you enjoy most during your travels?",
            "Do you have any dietary restrictions or preferences?",
            "How many travelers (including you) will be on this trip?",
            "Do you have any preferred travel tools (car rental, walking, public transportation and etc.)?",
            "Are there any additional details or preferences you'd like to share?"
        ]
        state["questions"] = questions

    # If we've just completed a previous question, store the user’s answer
    if 0 < current_round <= len(questions):
        question_key = f"q{current_round - 1}"
        preferences[question_key] = user_input.strip() if user_input else ""

    # If there are more questions to ask and we haven't exceeded max rounds
    if current_round < max_rounds and current_round < len(questions):
        next_question = questions[current_round]
        state["current_round"] = current_round + 1
        state["preferences"] = preferences

        return {
            "conversation_state": state,
            "message": next_question,
            "is_complete": False
        }
    else:
        # Either we've hit max_rounds or we've asked all questions
        state["current_round"] = max_rounds
        state["preferences"] = preferences

        # Build a final summary of Q&A
        summary_list = []
        for i, q_text in enumerate(questions):
            answer = preferences.get(f"q{i}", "No response")
            summary_list.append(f"{q_text} -> {answer}")
        summary_text = "\n".join(summary_list)

        return {
            "conversation_state": state,
            "message": (
                "Here is a summary of your travel preferences:\n"
                f"{summary_text}\n\n"
                "If you'd like to store these preferences, please proceed with a separate storage function."
            ),
            "is_complete": True
        }
