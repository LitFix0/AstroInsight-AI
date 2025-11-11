# Import necessary modules
import os
import requests
import genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import webbrowser # Import the webbrowser module
import threading  # Import threading to run browser opening in a separate thread
import time       # Import time for delays

# Initialize the Flask application
app = Flask(__name__)
# Enable CORS for all routes, allowing your frontend (running on a different origin) to make requests
CORS(app)

# --- Configuration ---
# IMPORTANT: Your actual Gemini API Key is directly integrated here.
# This approach is simpler but less secure for production environments.
GEMINI_API_KEY = 'Your_GEMINI_API_KEY'
# Initialize the genai client with your API key
client = genai.Client(api_key=GEMINI_API_KEY)

# DEBUG: Print the value of the API key right after assignment
print(f"DEBUG: GEMINI_API_KEY value during startup: '{GEMINI_API_KEY}'")

# Check if the API key is set (simplified check, as it's directly assigned now)
# This check simply ensures the string isn't empty.
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure your actual API key is assigned within the code.")

# --- Routes ---

@app.route('/get-astrology-reading', methods=['POST'])
def get_astrology_reading():
    """
    Handles POST requests to generate an astrology reading.
    Expects JSON data with 'name', 'dob', 'tob', and 'place'.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # Extract birth details from the request
    name = data.get('name')
    dob = data.get('dob')
    tob = data.get('tob')
    place = data.get('place')

    # Basic validation for required fields
    if not all([name, dob, tob, place]):
        return jsonify({"error": "Missing birth details. Please provide name, date of birth, time of birth, and place of birth."}), 400

    # Construct the prompt for the Gemini LLM
    prompt = f"Generate a personalized astrological reading for someone named {name}, born on {dob} at {tob} in {place}. Focus on their personality traits, potential life paths, and general outlook based on these details. Be concise and insightful."

    astrology_text = "Failed to generate astrology reading."

    try:
        # Use the genai client to generate content
        # The genai client handles the API request, payload, headers, and retries internally
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # Extract the generated text from the genai client's response
        # The genai client's response object has a .text attribute for the generated content
        astrology_text = response.text

    except genai.types.APIError as e:
        print(f"Gemini API Error: {e}")
        astrology_text = f"An error occurred with the Gemini API: {e.message}"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        astrology_text = "An internal server error occurred while processing your request."

    return jsonify({"reading": astrology_text}), 200

# --- Frontend Autolaunch Function ---
def open_browser():
    # Give the server a moment to start up
    time.sleep(1)
    # Define the path to your frontend HTML file
    # Assuming 'index.html' is in the same directory as app.py
    frontend_filename = 'index.html' # Changed to a variable for clarity
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), frontend_filename))

    # DEBUG: Print the exact path that Python is trying to open
    print(f"DEBUG: Attempting to open frontend at: '{frontend_path}'")
    
    # Use webbrowser to open the HTML file in a new tab
    webbrowser.open_new_tab(f'file:///{frontend_path}')
    print(f"Opened frontend: file:///{frontend_path}")


# --- Run the Flask app ---
if __name__ == '__main__':
    # Start the browser opening in a separate thread
    # This allows the Flask app to start serving immediately
    # without waiting for the browser to open.
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.start()

    # Run the Flask app on host 0.0.0.0 to make it accessible from other devices on the network
    app.run(host='0.0.0.0', port=5000, debug=True) # debug=True is for development, set to False in production

