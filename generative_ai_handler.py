# generative_ai_handler.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file or environment variables.")

genai.configure(api_key=GEMINI_API_KEY)

# Configuration for the generative model
generation_config = {
    "temperature": 0.6,  # Slightly lower for more focused persona/strategy generation
    "top_p": 0.95,
    "top_k": 40, # Common setting, adjust if needed
    "max_output_tokens": 3000, # Increased slightly for potentially more detailed outputs
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Using Gemini 1.5 Flash - faster and often more generous free tier
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest", 
    generation_config=generation_config,
    safety_settings=safety_settings
)

def generate_text_from_prompt(prompt_text, attempt_count=0):
    """
    Sends a prompt to the Gemini model and returns the generated text.
    Includes basic retry logic for rate limits.
    """
    max_retries = 2 # Try original + 2 retries
    try:
        prompt_parts = [prompt_text]
        response = model.generate_content(prompt_parts)
        if response.parts:
            return response.text
        else:
            print("Warning: Received an empty or blocked response from the API.")
            if response.prompt_feedback:
                print(f"Prompt Feedback: {response.prompt_feedback}")
            return None
    except Exception as e:
        print(f"Error generating text (Attempt {attempt_count + 1}): {e}")
        # Check for common rate limit error (this is a simple check, might need refinement)
        if "429" in str(e) and attempt_count < max_retries :
            wait_time = (attempt_count + 1) * 15 # Exponential backoff-like delay
            print(f"Rate limit likely hit. Waiting for {wait_time} seconds before retrying...")
            import time
            time.sleep(wait_time)
            return generate_text_from_prompt(prompt_text, attempt_count + 1) # Retry
        return None

if __name__ == '__main__':
    test_prompt = "Tell me a short, uplifting story about a robot learning to paint."
    story = generate_text_from_prompt(test_prompt)
    if story:
        print("\nTest story from Gemini:")
        print(story)
    else:
        print("\nFailed to get a response from Gemini after retries.")