from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS

# Define the full path to the JSON file
TEMP_JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_input.json')

# Route to handle saving input data to a JSON file
@app.route('/save-input', methods=['POST'])
def save_input():
    try:
        # Parse the incoming JSON data
        data = request.get_json()

        # Debugging: Log the received data
        print(f"Data received: {data}")

        # Save the data to a JSON file
        with open(TEMP_JSON_FILE, 'w') as f:
            json.dump(data, f)

        print("Data saved to JSON file successfully.")

        return jsonify({"status": "success", "message": "Data saved successfully."}), 200

    except Exception as e:
        # Log any error that occurs
        print(f"Error while saving data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Route to retrieve input data from the JSON file
@app.route('/get-input', methods=['GET'])
def get_input():
    try:
        # Check if the file exists
        if os.path.exists(TEMP_JSON_FILE):
            # Open and load the file
            with open(TEMP_JSON_FILE, 'r') as f:
                data = json.load(f)

            # Debugging: Log the data being returned
            print(f"Data returned: {data}")
            return jsonify({"status": "success", "data": data}), 200
        else:
            # File not found, log the error
            print("File not found: user_input.json")
            return jsonify({"status": "error", "message": "No input data found."}), 404

    except Exception as e:
        # Log any error that occurs
        print(f"Error while retrieving data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
