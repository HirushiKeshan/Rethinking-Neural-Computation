import os
import requests
from pydatalog import pyDatalog
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("API key not found. Please set it in the .env file.")

# Gemini API endpoint
GEMINI_API_ENDPOINT = "https://gemini-api.google.com/v1/models/gemini-1:generateText"

# Function to call Gemini API
def call_gemini_api(prompt, temperature=0.7, max_tokens=256):
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(GEMINI_API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return {"error": str(e)}

# Initialize PyDatalog for symbolic reasoning
pyDatalog.create_terms('X, logical_filter, is_valid_response, contains_keywords')

# Define symbolic rules
# Example rule: Check if the response contains specific keywords
contains_keywords[X] = ("neural" in X.lower()) & ("logic" in X.lower())

# Logical filter combining multiple rules
logical_filter[X] = contains_keywords[X]

# Main program logic
def validate_and_refine_response(prompt):
    print("Calling Gemini API with prompt:", prompt)
    response = call_gemini_api(prompt=prompt)

    if "error" in response:
        print(f"Error: {response['error']}")
        return

    generated_text = response.get("text", "")
    print("Generated Response:", generated_text)

    # Apply symbolic validation
    if logical_filter[generated_text]:
        print("Response passed symbolic validation.")
        return generated_text
    else:
        print("Response failed symbolic validation. Refining...")

        # Refining the response by appending constraints to the prompt
        refined_prompt = f"{prompt} (Ensure the response includes the concepts of 'neural' and 'logic'.)"
        refined_response = call_gemini_api(prompt=refined_prompt)
        print("Refined Response:", refined_response.get("text", "No output."))
        return refined_response.get("text", "")

# Example usage
if __name__ == "__main__":
    user_query = input("Enter your query: ")
    final_response = validate_and_refine_response(user_query)
    print("Final Response:", final_response)
