from datetime import datetime

# The tool configuration
tool_config = {
    "type": "function",
    "function": {
        "name": "get_current_datetime",
        "description": "Returns the current date and time in ISO 8601 format.",
        "parameters": {}  # No parameters needed for this function
    }
}


# The callback function (Returns current date and time)
def get_current_datetime(arguments):
  """
    Returns the current date and time.

    :param arguments: dict, not used in this function.
    :return: str, Current date and time in ISO 8601 format.
    """
  # Getting the current date and time
  current_datetime = datetime.now().isoformat()

  # Return the current date and time
  return current_datetime
