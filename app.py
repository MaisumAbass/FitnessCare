import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import pdfplumber

from openai import OpenAI

load_dotenv()

app = Flask(__name__)


def clean_and_structure_table(raw_table):
    """Cleans and structures the workout table."""
    structured_data = []
    current_day = None
    current_round = None

    for row in raw_table:
        # Identify and set the current day
        if row[0] and "Day" in row[0]:
            current_day = row[0]
            continue
        # Identify and set the current round
        elif row[0] and "Round" in row[0]:
            current_round = row[0]
            continue
        # Extract valid workout details
        elif row[0] and row[0].isdigit():
            # Ensure all fields are present to avoid incomplete data
            if len(row) >= 5:
                workout = {
                    "Day": current_day,
                    "Round": current_round,
                    "Exercise": row[1].replace("\n", " "),  # Handle text wrapping
                    "Weight": row[2] if row[2] else "N/A",  # Fill missing values with "N/A"
                    "Reps": row[3] if row[3] else "N/A",
                    "Sets": row[4] if row[4] else "N/A",
                }
                structured_data.append(workout)

    return structured_data

def extract_table_data(file_path):
    """Extracts and processes workout table data from the given PDF."""
    data = {}
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                # Look for the table with the workout details
                if 'No Workout Weight Reps Sets' in text:
                    tables = page.extract_tables()
                    if tables:
                        # Assuming the first relevant table is the workout table
                        raw_table = tables[0]
                        data['Workout_Table'] = clean_and_structure_table(raw_table)
    except Exception as e:
        print(f"Error while reading the PDF: {e}")
    
    return data

def extract_text_from_pdf(file_path):
    """Extracts the text content from the provided PDF."""
    try:
        with pdfplumber.open(file_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                full_text += text + "\n"
        return full_text
    except Exception as e:
        print(f"Error while reading the PDF: {e}")
        return ""

def call_azure_openai(prompt):
    """Calls Azure OpenAI API and returns the response."""
    messages = [{"role": "user", "content": prompt}]
    response = openai_client.chat.completions.create(
        model="GPT4TURBO",
        messages=messages
    )
    if response.choices:
        content = response.choices[0].message.content.strip()
        print("content ",content)
        clean_content = content.replace("json", "").replace("", "").strip()
        return clean_content
    raise ValueError("Failed to get a valid response from OpenAI GPT")


table_pdf_path = 'planner.pdf'  # Path to the workout table PDF
text_pdf_path = 'updated.pdf'

@app.route('/')
def home():
    return render_template('index.html')  # Ensure your index.html exists in the templates folder

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
        gym = data.get('gym')
        desired_weight = data.get('desiredWeight')  # Desired weight
        days = data.get('days')  # Days to achieve desired weight
        sport = data.get('sport')  # Sport preference
       
        # Extract table data (workout plan)
        table_data = extract_table_data(table_pdf_path)
        
        # Extract text data (diet plan)
        text_data = extract_text_from_pdf(text_pdf_path)

        # Simplified prompt for AI (uses extracted PDF data and user data)
        prompt = f"""
I am giving you the user data and a PDF data:

User Information:
Height: {height} cm
Weight: {weight} kg
Diet preference: {diet}
Location: {location}
Goal: {goal}
Age: {age}
Activity level: {activity_level}
Gym: {gym}
Desired Weight: {desired_weight}
Days to achieve goal: {days}
Sport: {sport}

PDF data:
Workout Plan Data: {table_data['Workout_Table']}
Diet Plan Data: {text_data}

Create a weekly plan in JSON format based on the provided data. Ensure the following:
1. Include all 7 days of the week for both the diet plan and workout plan.
2. For each day in the workout plan, provide only 2 exercises for weight loss and 3 exercises for weight gain.
3. Create the data based on the PDF if needed, if the exercise or meal from the PDF doesn't match the user data, you can also create the plan based on AI and user details.
4. Please make sure that your output is totally matching the diet preference, location, and other provided details.
5. Ensure the structure is strictly JSON and free from errors:
6. Don't even write json at the starting nothing only the formatted output only
7. Be practical about all the detial you give like if the person is from let suppose kargil then you should not suggest diet like idlie dosa, etc.
8. Add the game he use to play in the workout sometimes.
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
               "exercise1": "... x3",
               "exercise2": "... x2.etc"
           }},
           ...
       }}
   }}
9. Do not include any text or explanations outside the JSON output.
10. Format the JSON properly to avoid any parsing issues 
""" 
        
        # Call Azure OpenAI API
        ai_response = call_azure_openai(prompt)

        # Parse the AI response
        plan_content = ai_response
        print(f"AI response: {plan_content}")

        # Convert the string into a Python dictionary
        try:
            plan_dict = json.loads(plan_content)
        except json.JSONDecodeError as e:
            print(f"Error in JSON formatting from OpenAI response: {e}")
            return jsonify({'error': 'AI response is not valid JSON'}), 400
     
        # Return the parsed response
        return jsonify({
            'diet_plan': plan_dict.get('diet_plan', {}),
            'workout_plan': plan_dict.get('workout_plan', {})
        })

    except Exception as e:
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
