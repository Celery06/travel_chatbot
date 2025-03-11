import os
import core_functions
import json

# This is the storage path for the new assistant.json file
assistant_file_path = '.storage/assistant.json'
assistant_name = "TravelGenie"
assistant_instructions_path = 'assistant/instructions.txt'


# Get the instructions for the assistant
def get_assistant_instructions():

  # Open the file and read its contents
  with open(assistant_instructions_path, 'r', encoding="utf-8") as file:
    return file.read()


# Create or load assistant
def create_assistant(client, tool_data):

  # If there is an assistant.json file, load the assistant
  if os.path.exists(assistant_file_path):

    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)

      assistant_id = assistant_data['assistant_id']

      # Generate current hash sums
      current_tool_hashsum = core_functions.generate_hashsum('tools')
      current_resource_hashsum = core_functions.generate_hashsum('resources')
      current_assistant_hashsum = core_functions.generate_hashsum(
          'assistant.py')

      current_assistant_data = {
          'tools_sum': core_functions.generate_hashsum('tools'),
          'resources_sum': core_functions.generate_hashsum('resources'),
          'assistant_sum': core_functions.generate_hashsum('assistant.py')
      }

      # Assuming assistant_data is loaded from a JSON file
      if compare_assistant_data_hashes(current_assistant_data, assistant_data):

        print("Assistant is up-to-date. Loaded existing assistant ID.")

        return assistant_id
      else:
        print("Changes detected. Updating assistant...")

        # Find and validate all given files
        file_ids = core_functions.get_resource_file_ids(client)

        try:
          # Update the assistant
          assistant = client.beta.assistants.update(
            instructions=get_assistant_instructions(),
            assistant_id = assistant_id,
            name=assistant_name,
            model="gpt-4o",
            tools=tool_data["tool_configs"])

          # Build the JSON
          assistant_data = {
              'assistant_id': assistant.id,
              'tools_sum': current_tool_hashsum,
              'resources_sum': current_resource_hashsum,
              'assistant_sum': current_assistant_hashsum,
          }

          save_assistant_data(assistant_data, assistant_file_path)

          print(f"Assistant (ID: {assistant_id}) updated successfully.")

        except Exception as e:
          print(f"Error updating assistant: {e}")
  else:
    # Create a new assistant

    # Find and validate all given files
    file_ids = core_functions.get_resource_file_ids(client)

    # Create the assistant
    assistant = client.beta.assistants.create(
        instructions=get_assistant_instructions(),
        name=assistant_name,
        model="gpt-4o",
        tools=tool_data["tool_configs"])

    # Print the assistant ID or any other details you need
    print(f"Assistant ID: {assistant.id}")

    #Generate the hashsums for tools, resources, and the assistant.json file
    tool_hashsum = core_functions.generate_hashsum('tools')
    resource_hashsum = core_functions.generate_hashsum('resources')
    assistant_hashsum = core_functions.generate_hashsum('assistant.py')

    # Build the JSON
    assistant_data = {
        'assistant_id': assistant.id,
        'tools_sum': tool_hashsum,
        'resources_sum': resource_hashsum,
        'assistant_sum': assistant_hashsum,
    }

    save_assistant_data(assistant_data, assistant_file_path)

    print(f"Assistant has been created with ID: {assistant.id}")

    assistant_id = assistant.id

  return assistant_id


# Save the assistant to a file
def save_assistant_data(assistant_data, file_path):
  """
  Save assistant data into a JSON file.

  :param assistant_data: Dictionary containing assistant's data.
  :param file_path: Path where the JSON file will be saved.
  """
  try:
    with open(file_path, 'w') as file:
      json.dump(assistant_data, file)
  except Exception as e:
    print(f"Error saving assistant data: {e}")


# Checks if the Assistant JSON has all required fields
def is_valid_assistant_data(assistant_data):
  """
  Check if the assistant data contains valid values for all required keys.

  :param assistant_data: Dictionary containing assistant's data.
  :return: Boolean indicating whether the data is valid.
  """
  required_keys = [
      'assistant_id', 'tools_sum', 'resources_sum', 'assistant_sum'
  ]
  return all(key in assistant_data and assistant_data[key]
             for key in required_keys)


#Compares if all of the fields match with the current hashes
def compare_assistant_data_hashes(current_data, saved_data):
  """
  Compare current assistant data with saved data.

  :param current_data: Current assistant data.
  :param saved_data: Saved assistant data from JSON file.
  :return: Boolean indicating whether the data matches.
  """
  if not is_valid_assistant_data(saved_data):
    return False

  return (current_data['tools_sum'] == saved_data['tools_sum']
          and current_data['resources_sum'] == saved_data['resources_sum']
          and current_data['assistant_sum'] == saved_data['assistant_sum'])
