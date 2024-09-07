import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key
genai.configure(api_key=os.getenv("API_KEY"))

def coach_answer(move_history):
    gemini = genai.GenerativeModel("gemini-pro")
    response = gemini.generate_content(f"In a Classic Chess game, analyze the board state based on notation: {move_history} and suggest one key move for white pieces with a brief explanation. Provide only a single sentence summary.")
    
    # Print response for debugging
    print("Raw response:", response.text)
    
    # Ensure response is a single sentence
    analysis = response.text.strip()
    return analysis
