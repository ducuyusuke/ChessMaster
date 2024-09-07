import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key
genai.configure(api_key=os.getenv("API_KEY"))

def coach_answer(move_history):
    gemini = genai.GenerativeModel("gemini-pro")
    response = gemini.generate_content(f"In a Classic Chess game, based on notation: {move_history} analyze and make a critique of the last white pieces move with a brief explanation. Provide only a single sentence summary.")


    # Ensure response is a single sentence
    analysis = response.text.strip()
    return analysis
