# generative_ai_handler.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file or environment variables.")

genai.configure(api_key=GEMINI_API_KEY)

# Configuration for the generative model
generation_config = {
    "temperature": 0.7,  # Adjust for creativity vs. determinism
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048, # Adjust as needed
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Using Gemini 1.5 Pro
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest", # Or "gemini-1.0-pro" if 1.5 isn't available to you
    generation_config=generation_config,
    safety_settings=safety_settings
)

def generate_text_from_prompt(prompt_text):
    """
    Sends a prompt to the Gemini model and returns the generated text.
    """
    try:
        prompt_parts = [prompt_text]
        response = model.generate_content(prompt_parts)
        if response.parts:
            return response.text
        else:
            # Handle cases where the response might be blocked or empty
            print("Warning: Received an empty or blocked response from the API.")
            print(f"Prompt: {prompt_text[:200]}...") # Log part of the prompt for debugging
            if response.prompt_feedback:
                print(f"Prompt Feedback: {response.prompt_feedback}")
            return None # Or raise an error
    except Exception as e:
        print(f"Error generating text: {e}")
        return None

if __name__ == '__main__':
    # Test the connection
    test_prompt = "Tell me a short story about a curious robot."
    story = generate_text_from_prompt(test_prompt)
    if story:
        print("Test story from Gemini:")
        print(story)
    else:
        print("Failed to get a response from Gemini.")