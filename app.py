import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import openai
from flask_pymongo import PyMongo

# Load the .env file
load_dotenv()

# Get the secret key from the environment variables
openai.api_key = os.getenv("SECRET_KEY")

# Define the Flask app
app = Flask(__name__)
cors = CORS(app)
mongo_uri = os.getenv("MONGO_URI")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

# Print the MongoDB URIs
print("mongo_uri:", mongo_uri)
print("app.config['MONGO_URI']:", app.config["MONGO_URI"])

# Initialize PyMongo
mongo = PyMongo(app)

# Print the PyMongo object
print("mongo:", mongo)

@app.route('/feedback-submit', methods=['POST'])
def handle_feedback_submit():
    data = request.get_json()
    result = mongo.db.feedback.insert_one(data)  # assuming 'feedback' is the name of your collection
    return jsonify({"_id": str(result.inserted_id)})

@app.route('/waitlist-submit', methods=['POST'])
def handle_waitlist_submit():
    data = request.get_json()
    result = mongo.db.waitlist.insert_one(data)  # assuming 'waitlist' is the name of your collection
    return jsonify({"_id": str(result.inserted_id)})

# Route for predicting with OpenAI integration
@app.route('/openai-predict', methods=['POST'])
def openai_predict():
    # Retrieve the input data from the request
    input_text = request.json['inputText']

    # Prepend the desired string to the input text
    prompt_string = "List 5 high quality problem statements based on the following problem, in a user story format from the agile software development framework. Make each item in the format As a <something>, I want to <do something>, so that <some outcome>. No line breaks. The problem is:"
    input_text = prompt_string + " " + input_text

    # Make the request to the OpenAI API using the openai.Completion.create() method
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=input_text,
        max_tokens=60
    )

    # Check for errors in the response
    if 'choices' in response and len(response['choices']) > 0:
        # Extract the predicted text from the API response
        predicted_text = response['choices'][0]['text'].strip()

        # Split the predicted text into individual items if it's a list
        predicted_items = predicted_text.split('\n')

        # Return the predicted items as JSON response
        return jsonify({'predicted_items': predicted_items})
    else:
        # Handle the situation where 'choices' is not in the response
        print("No 'choices' in API response")
        print(response)
        return jsonify({'error': "No 'choices' in API response"})

@app.route('/openai-solution', methods=['POST'])
def openai_solution():
    # Retrieve the input data from the request
    input_text = request.json['inputText']

    # Prepend or append the desired string to the problem statement
    prompt_string = "Provide 5 really good solution hypotheses for the following solution hypothesis. Keep each problem statement within 200 characters. No line breaks."
    problem_statement = prompt_string + " " + input_text

    # Make the request to the OpenAI API using the openai.Completion.create() method
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=problem_statement,
        max_tokens=200
    )

    # Check for errors in the response
    if 'choices' in response and len(response['choices']) > 0:
        # Extract the predicted text from the API response
        predicted_text = response['choices'][0]['text'].strip()

        # Split the predicted text into individual solutions if it's a list
        predicted_solutions = predicted_text.split('\n')

        # Return the predicted solutions as JSON response
        return jsonify({'predicted_items': predicted_solutions})
    else:
        # Handle the situation where 'choices' is not in the response
        print("No 'choices' in API response")
        print(response)
        return jsonify({'error': "No 'choices' in API response"})

# Run the Flask app
if __name__ == '__main__':
    app.run()