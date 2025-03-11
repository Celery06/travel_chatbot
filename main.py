import os
import logging
from flask import Flask, render_template
import openai
import core_functions
import assistant
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)

# Check OpenAI version compatibility
core_functions.check_openai_version()

# Create Flask app
app = Flask(__name__)

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
  raise ValueError("No OpenAI API key found in environment variables")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Initialize all available tools
tool_data = core_functions.load_tools_from_directory('tools')
print(tool_data)

# Create or load assistant
assistant_id = assistant.create_assistant(client, tool_data)

if not assistant_id:
  raise ValueError(f"No assistant found by id: {assistant_id}")

# Import integrations
available_integrations = core_functions.import_integrations()

requires_db = False

# Dynamically set up routes for active integrations
for integration_name in available_integrations:
  integration_module = available_integrations[integration_name]
  integration_module.setup_routes(app, client, tool_data, assistant_id)

  #Checks whether or not a DB mapping is required
  if integration_module.requires_mapping():
    requires_db = True

# Maybe initialize the SQLite DB structure
if requires_db:
  core_functions.initialize_mapping_db()


#Display a simple web page for simplicity
@app.route('/')
def home():
  return render_template('index.html')


# start the app
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
