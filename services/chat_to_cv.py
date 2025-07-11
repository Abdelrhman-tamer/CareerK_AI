import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def process_message(session_id: str, message: str):
    try:
        
        prompt = f"""
You are an AI assistant that extracts CV fields from user input.

Identify affected fields and return only those in `structured_fields`.

Available fields:

- personal_info: {{ "name": "", "email": "", "phone": "", "address": "", "linkedin": "", "portfolio": "", "summary": "" }}
- education: [{{ "institution": "", "location": "", "degree": "", "field": "", "start_date": "", "end_date": "", "gpa": "" }}]
- experience: [{{ "position": "", "company": "", "dates": "", "achievements": ["", ""] }}]
- skillsets: ["", ""]
- projects: [{{ "title": "", "description": "", "technologies": [""], "results": [""] }}]
- certifications: [{{ "name": "", "issuer": "", "date": "" }}]
- additional: [{{ "title": "", "description": "" }}]

Return in this format ONLY:

{{
  "reply": "Your friendly response.",
  "structured_fields": {{ ... }}
}}

User: "{message}"

Respond ONLY with JSON. No markdown. No explanations.
"""

#         prompt = f"""
# You are a helpful AI assistant that extracts CV information from user messages.

# For each message from the user, identify which CV sections are mentioned or affected and return only those sections in "structured_fields".

# Possible CV sections and their structures:
# - personal_info: {{ "full_name": "", "email": "", "phone": "", "address": "", "linkedin": "", "github": "", "summary": "" }}
# - experience: [{{ "position": "", "company": "", "duration": "", "description": "" }}]
# - education: [{{ "degree": "", "institution": "", "year": "", "description": "" }}]
# - skills: ["skill1", "skill2", ...]
# - projects: [{{ "name": "", "description": "" }}]
# - certifications: ["cert1", "cert2", ...]
# - additional: ""

# Return a response in this strict JSON format (do not add markdown, ``` or explanations):

# {{
#   "reply": "Your friendly response to the user.",
#   "structured_fields": {{
#     // Include only the sections that are mentioned or affected by the user's message
#     // Example 1:
#     // User: "I worked at Amazon as a Backend Developer from 2020 to 2023"
#     // structured_fields: {{
#     //   "experience": [{{ "position": "Backend Developer", "company": "Amazon", "duration": "2020-2023", "description": "" }}]
#     // }}
#     // Example 2:
#     // User: "I am good at React, JavaScript, and CSS"
#     // structured_fields: {{
#     //   "skills": ["React", "JavaScript", "CSS"]
#     // }}
#     // Example 3:
#     // User: "My email is ismail@example.com"
#     // structured_fields: {{
#     //   "personal_info": {{ "email": "ismail@example.com" }}
#     // }}
#     // If no sections are mentioned, return an empty structured_fields: {{}}
#   }}
# }}

# User: "{message}"

# Now return only the JSON object. Do not include explanations, markdown, or code blocks.
#         """

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 1024,
                "top_p": 1,
                "top_k": 1,
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            ]
        )

        raw_output = response.text.strip()
        print("🔵 Raw Gemini Output:\n", raw_output)

        # Clean up markdown/code block wrappers if Gemini ignores prompt
        cleaned_output = raw_output.replace("```json", "").replace("```", "").strip()

        # Try to parse structured JSON output
        parsed = json.loads(cleaned_output)

        # Ensure keys exist
        if "reply" not in parsed or "structured_fields" not in parsed:
            raise ValueError("Missing required keys in Gemini response")

        return parsed

    except Exception as e:
        print("🔴 Error processing Gemini response:", e)
        return {
            "reply": "Sorry, I couldn’t understand that. Please try rephrasing your message.",
            "structured_fields": {}
        }








# # chat_to_cv.py

# import os
# import google.generativeai as genai
# from dotenv import load_dotenv
# import json

# load_dotenv()

# # Configure Gemini API
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel("gemini-1.5-flash")  # or "gemini-2.0-flash" if named that in your dashboard

# def process_message(session_id: str, message: str):
#     try:
#         prompt = f"""
# You are a helpful AI assistant that extracts CV information from user messages.

# For each message from the user, return a response in this strict JSON format (do not add markdown, ``` or explanations):

# {{
#   "reply": "Your friendly response to the user.",
#   "structured_fields": {{
#     "personal_info": {{
#       "full_name": "",
#       "email": "",
#       "phone": "",
#       "address": ""
#     }},
#     "experience": [
#       {{
#         "position": "",
#         "company": "",
#         "duration": "",
#         "description": ""
#       }}
#     ],
#     "education": [
#       {{
#         "degree": "",
#         "institution": "",
#         "year": "",
#         "description": ""
#       }}
#     ],
#     "skills": [],
#     "projects": [],
#     "certifications": [],
#     "additional": ""
#   }}
# }}

# The fields may be left empty if not provided in the message.

# User: "{message}"

# Now return only the JSON object. Do not include explanations, markdown, or code blocks.
#         """

#         response = model.generate_content(
#             prompt,
#             generation_config={
#                 "temperature": 0.3,
#                 "max_output_tokens": 1024,
#                 "top_p": 1,
#                 "top_k": 1,
#             },
#             safety_settings=[
#                 {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
#                 {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
#                 {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
#                 {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
#             ]
#         )

#         raw_output = response.text.strip()
#         print("🔵 Raw Gemini Output:\n", raw_output)

#         # Clean up markdown/code block wrappers if Gemini ignores prompt
#         cleaned_output = raw_output.replace("```json", "").replace("```", "").strip()

#         # Try to parse structured JSON output
#         parsed = json.loads(cleaned_output)

#         # Ensure keys exist
#         if "reply" not in parsed or "structured_fields" not in parsed:
#             raise ValueError("Missing required keys in Gemini response")

#         return parsed

#     except Exception as e:
#         print("🔴 Error processing Gemini response:", e)
#         return {
#             "reply": "Sorry, I couldn’t understand that. Please try rephrasing your message.",
#             "structured_fields": {}
#         }
