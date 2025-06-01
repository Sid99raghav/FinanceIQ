import os
from openai import OpenAI
import google.generativeai as genai
from google.api_core.exceptions import (
    InvalidArgument, 
    ResourceExhausted, 
    DeadlineExceeded, 
    PermissionDenied 
)

import json

def create_chat_completion(prompt, model="gpt-4o"):
    client = OpenAI()
    json_prompt = f"{prompt}\n\nPlease respond in proper JSON format only."
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant that always provides JSON output."},
            {"role": "user", "content": json_prompt}
        ],
        model=model
    )
    return response.choices[0].message.content

def gemini_chat_completion(prompt, model="gemini-1.5-flash", format="json"):
    key = os.getenv("API_KEY")

    if not key:
        raise ValueError("API_KEY environment variable is not set. Please set it using -e or export it in your environment.")

    
    modified_prompt = f"{prompt}\n\nPlease respond in proper {format.upper()} format only."

    response = ""
    try:
        genai.configure(api_key=key)

        # Select the desired Gemini model
        gemini_model = genai.GenerativeModel(model_name=model)

        # Use the model to generate content
        response = gemini_model.generate_content(modified_prompt)
    except (InvalidArgument, ResourceExhausted, DeadlineExceeded, PermissionDenied) as e:
        print(f"Error fetching response: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return response.text if response else "Error: No response generated."

def fetch_and_save_valid_json(message_content):
    """
    Fetches a response from OpenAI, extracts valid JSON parts, and saves them to a file.

    Args:
        prompt (str): The user prompt for OpenAI.
        filename (str): The file to save the JSON content.
        model (str): The model to use for the request.
        max_tokens (int): Maximum tokens for the response.
        temperature (float): Controls randomness in the response.
    """
    try:
        # Attempt to parse and save valid JSON blocks
        valid_json_objects = []

        # Sometime openai just give the proper json
        try:
            # Attempt to parse the entire message content
            parsed_json = json.loads(message_content)
            valid_json_objects.append(parsed_json)
            return valid_json_objects
        except json.JSONDecodeError as e:
            print(f"Skipping first pass")

        start = message_content.find("```json")
        while start != -1:
            end = message_content.find("```", start + len("```json"))
            if end != -1:
                json_snippet = message_content[start + len("```json"):end].strip()
                try:
                    # Attempt to parse the JSON snippet
                    parsed_json = json.loads(json_snippet)
                    valid_json_objects.append(parsed_json)
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid JSON block: {e}")
            else:
                print("Incomplete JSON block found and discarded.")
            start = message_content.find("```json", end + len("```"))

        if valid_json_objects:
            return valid_json_objects
        else:
            print("No valid JSON objects found.")

    except Exception as e:
        print(f"Error fetching response: {e}")

    return []
