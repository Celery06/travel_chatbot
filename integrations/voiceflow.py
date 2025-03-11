"""
Using Voiceflow Endpoints with Authentication

To interact with the Voiceflow endpoints, you need to ensure proper authentication. 
This involves setting the X-API-KEY in the request header and using a secret CUSTOM_API_KEY 
within your Replit template. Follow these steps for successful authorization:

1. Set CUSTOM_API_KEY:
   - In your Replit template, define a variable `CUSTOM_API_KEY` with your secret API key. 
     This key is crucial for the authentication process.

2. Choose a Password:
   - Select any password of your choice. This password will be used as the value for the `X-API-KEY`  in the request header. It's important to always include this in the header of every request you make.

3. Setup and connect the Voiceflow template:
   - You can get access to the Voiceflow template directly from within our resource hub: https://hub.integraticus.com/how-i-build-openai-assistants-in-2024-gpt-chatbot-framework-2-0/ (It's free)

4. Set the Replit URL:
 - Within the API Widget inside of the Voiceflow template, you need to adjust the URL to your current Replit URL. You can do that by starting your Replit template and copying the URL from the Web View. Do this for both of the API Widgets. 
 - Here are the endpoints you can use: 
   - YOUR_REPLIT_URL/voiceflow/start
   - YOUR_REPLIT_URL/voiceflow/chat

5. Set Headers for the Request:
   - In your request headers of the Voiceflow API Widget, include the following: 'X-API-KEY': [Your chosen password]
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
  @app.route('/voiceflow/start', methods=['GET'])
  def start_conversation():
    core_functions.check_api_key()  # Check the API key
    logging.info("Starting a new conversation...")
    thread = client.beta.threads.create()
    logging.info(f"New thread created with ID: {thread.id}")
    return jsonify({"thread_id": thread.id})

  # Route to chat with the assistant
  @app.route('/voiceflow/chat', methods=['POST'])
  def chat():
    core_functions.check_api_key()  # Check the API key
    data = request.json
    thread_id = data.get('thread_id')
    user_input = data.get('message', '')
    email = data.get('email')

    if not thread_id:
      logging.error("Error: Missing thread_id")
      return jsonify({"error": "Missing thread_id"}), 400

    logging.info(f"Received message: {user_input} for thread ID: {thread_id}")

    # Add system message with email info
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="assistant",
        content=f"The user's email is {email}. Use this information if needed."
    )
    logging.info({email})
    # Add user message
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_input
    )

    # Run assistant
    run = client.beta.threads.runs.create(thread_id=thread_id,
                                          assistant_id=assistant_id)

    # This processes any possible action requests
    core_functions.process_tool_calls(client, thread_id, run.id, tool_data)

    # Get the assistant's response
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[0].content[0].text.value
    logging.info(f"Assistant response: {response}")

    return jsonify({"response": response})
