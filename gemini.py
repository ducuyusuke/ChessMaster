import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key
genai.configure(api_key=os.getenv("API_KEY"))

def coach_answer(move_history):
    gemini = genai.GenerativeModel("gemini-pro")
    response = gemini.generate_content(f"In a Classic Chess game, you must analyse the state of the board according to notation: {move_history} and then suggest three possible moves for white pieces. Briefly explain why they would be good moves, as if you were a coach. Send me the response in a single paragraph and don't include any greetings, only the overall anaylsis.")
    print(response.text)
    return response.text
