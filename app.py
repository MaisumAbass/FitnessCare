# import re
import json
import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
# import pdfplumber

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Set up OpenAI client with the API key
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Function to parse the PDF and extract workout and diet plans
# def parse_pdf(pdf_path):  # Accept the PDF path as a parameter
#     with pdfplumber.open(pdf_path) as pdf:
#         text = ""
#         for page in pdf.pages:
#             text += page.extract_text()
#     return {
#         "workout_plan": {
#             "Monday": {
#                 "full_body": ["Push-ups", "Bent-over rows", "Squats", "Lunges"]
#             },
          
#         },
#         "diet_plan": {
#             "Monday": {
#                 "breakfast": "Scrambled tofu with spinach",
#                 "lunch": "Chickpea stir-fry",
#                 "dinner": "food not containing more calories "
#             },
           
#         }
#     }  # Return the extracted text (or structured data if needed)

# # Load PDF data once at the start (no return needed here)
# pdf_data = parse_pdf('PDF/Diet_Workout_planner_v2.pdf')

        # PDF Diet Plan: {json.dumps(pdf_data['diet_plan'])}
        # PDF Workout Plan: {json.dumps(pdf_data['workout_plan'])}
@app.route('/')
def home():
    return render_template('index.html')  # Make sure your index.html exists in the templates folder


@app.route('/get_plan', methods=['POST'])
def get_plan():
    try:
        # User data from the request
        data = request.get_json()
        height = data.get('height')
        weight = data.get('weight')
        diet = data.get('diet')
        location = data.get('location')
        goal = data.get('goal')
        age = data.get('age')
        activity_level = data.get('activityLevel')

        # Simplified prompt for AI (uses PDF data only)
        prompt = f"""
        Using the provided PDF data:
        User Information:
        Height: {height} cm
        Weight: {weight} kg
        Diet preference: {diet}
        Location: {location}
        Goal: {goal}
        Age: {age}
        Activity level: {activity_level}

        Create a simple weekly plan in JSON format based on the PDF data, structured like this:
        {{
            "diet_plan": {{
                "monday": {{
                    "breakfast": "...",
                    "lunch": "...",
                    "snack": "...",
                    "dinner": "..."
                }},
                ...
            }},
            "workout_plan": {{
                "monday": {{
                    "exercise1": "...",
                    "exercise2": "..."
                }},
                ...
            }}
        }} Caution: Give me the data in JSON format only and no other text should be there.
        """

        # Call OpenAI API
        ai_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a fitness care assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # Parse the AI response
        plan_content = ai_response.choices[0].message.content.strip()
        print(f"AI response: {plan_content}")

        # Convert the string into a Python dictionary
        try:
            plan_dict = json.loads(plan_content)  # This converts the string to a Python dictionary
        except json.JSONDecodeError as e:
            print("error in json formating")
            return jsonify({'error': 'AI response is not valid JSON'}), 400
        
        # Return the parsed response
        return jsonify({
            'diet_plan': plan_dict.get('diet_plan', {}),
            'workout_plan': plan_dict.get('workout_plan', {})
        })

    except Exception as e:
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500



if __name__ == '__main__':
    app.run(debug=True)
