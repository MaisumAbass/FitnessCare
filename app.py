# # import re
# import json
# import os
# from flask import Flask, render_template, request, jsonify
# from openai import OpenAI
# from dotenv import load_dotenv
# # import pdfplumber


# load_dotenv()

# app = Flask(__name__)

# api_key = os.getenv("OPENAI_API_KEY")
# client = OpenAI(api_key=api_key)

# @app.route('/')
# def home():
#     return render_template('index.html')  # Make sure your index.html exists in the templates folder


# @app.route('/get_plan', methods=['POST'])
# def get_plan():
#     try:
#         # User data from the request
#         data = request.get_json()
#         height = data.get('height')
#         weight = data.get('weight')
#         diet = data.get('diet')
#         location = data.get('location')
#         goal = data.get('goal')
#         age = data.get('age')
#         activity_level = data.get('activityLevel')

#         # Simplified prompt for AI (uses PDF data only)
#         prompt = f"""
#         Using the provided PDF data:
#         User Information:
#         Height: {height} cm
#         Weight: {weight} kg
#         Diet preference: {diet}
#         Location: {location}
#         Goal: {goal}
#         Age: {age}
#         Activity level: {activity_level}

#         Create a simple weekly plan in JSON format based on the PDF data, structured like this:
#         {{
#             "diet_plan": {{
#                 "monday": {{
#                     "breakfast": "...",
#                     "lunch": "...",
#                     "snack": "...",
#                     "dinner": "..."
#                 }},
#                 ...
#             }},
#             "workout_plan": {{
#                 "monday": {{
#                     "exercise1": "...",
#                     "exercise2": "..."
#                 }},
#                 ...
#             }}
#         }} Caution: Give me the data in JSON format only and no other text should be there.
#         """

#         # Call OpenAI API
#         ai_response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are a fitness care assistant."},
#                 {"role": "user", "content": prompt}
#             ]
#         )

#         # Parse the AI response
#         plan_content = ai_response.choices[0].message.content.strip()
#         print(f"AI response: {plan_content}")

#         # Convert the string into a Python dictionary
#         try:
#             plan_dict = json.loads(plan_content)  # This converts the string to a Python dictionary
#         except json.JSONDecodeError as e:
#             print("error in json formating")
#             return jsonify({'error': 'AI response is not valid JSON'}), 400
        
#         # Return the parsed response
#         return jsonify({
#             'diet_plan': plan_dict.get('diet_plan', {}),
#             'workout_plan': plan_dict.get('workout_plan', {})
#         })

#     except Exception as e:
#         return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500



# if __name__ == '__main__':
#     app.run(debug=True)
import os
import json
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import pdfplumber


load_dotenv()

app = Flask(__name__)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

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
table_pdf_path = 'planner.pdf'  # Path to the workout table PDF
text_pdf_path = 'updated.pdf'
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

        
        # Extract table data (workout plan)
        table_data = extract_table_data(table_pdf_path)
        
        # Extract text data (diet plan)
        text_data = extract_text_from_pdf(text_pdf_path)

        # Simplified prompt for AI (uses extracted PDF data and user data)
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

        Workout Plan Data: {table_data['Workout_Table']}
        Diet Plan Data: {text_data}

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
        }} Caution: Give me the data in JSON format only and no other text even single should be there.
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
            print("error in json formatting")
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
