"""
Using Default Endpoints with Authentication in Python

To interact with the default endpoints, you need to ensure proper authentication. 
This involves setting the X-API-KEY in the request header and using a secret CUSTOM_API_KEY 
within your Replit template. Follow these steps for successful authorization:

1. Set CUSTOM_API_KEY:
   - In your Replit template, define a variable `CUSTOM_API_KEY` with your secret API key. 
     This key is crucial for the authentication process.

2. Choose a Password:
   - Select any password of your choice. This password will be used as the value for the `X-API-KEY`  in the request header. It's important to always include this in the header of every request you make.

3. Formulate the Request:
   - When making a request to the endpoints, your URLs should follow this format:
     a. Start Endpoint URL: "https://your_replit_url/default/start"
        - Use this URL to initiate the start endpoint.
     b. Chat Endpoint URL: "https://your_replit_url/default/chat"
        - Use this URL to access the chat endpoints.

4. Set Headers for the Request:
   - In your request headers, include the following: 'X-API-KEY': [Your chosen password]
"""

import logging
from flask import request, jsonify
import core_functions

# Configure logging for this module
logging.basicConfig(level=logging.INFO)


# Defines if a DB mapping is required
def requires_mapping():
  return False


def setup_routes(app, client, tool_data, assistant_id):
  # Check OpenAI version compatibility
  core_functions.check_openai_version()

  # Route to start the conversation
  @app.route('/default/start', methods=['GET'])
  def start_conversation():
    core_functions.check_api_key()  # Check the API key
    logging.info("Starting a new conversation...")
    thread = client.beta.threads.create()
    logging.info(f"New thread created with ID: {thread.id}")
    return jsonify({"thread_id": thread.id})

  # Route to chat with the assistant
  @app.route('/default/chat', methods=['POST'])
  def chat():
    core_functions.check_api_key()  # Check the API key
    data = request.json
    thread_id = data.get('thread_id')
    user_input = data.get('message', '')

    if not thread_id:
      logging.error("Error: Missing thread_id")
      return jsonify({"error": "Missing thread_id"}), 400

    logging.info(f"Received message: {user_input} for thread ID: {thread_id}")
    client.beta.threads.messages.create(thread_id=thread_id,
                                        role="user",
                                        content=user_input)
    run = client.beta.threads.runs.create(thread_id=thread_id,
                                          assistant_id=assistant_id)
    # This processes any possible action requests
    core_functions.process_tool_calls(client, thread_id, run.id, tool_data)

    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[0].content[0].text.value
    logging.info(f"Assistant response: {response}")
    return jsonify({"response": response})
