import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

f = open("fen.txt", "r")
fen=f.read()

# Access the API key
genai.configure(api_key=os.getenv("API_KEY"))

def coach_answer():
    gemini = genai.GenerativeModel("gemini-pro")
    response = gemini.generate_content(f"In a Classic Chess game, you must analyse the state of the board according to FEN notation: {fen} . Suggest me 3 legal moves (pay close attetion to the current position of the pieces) and very briefly explain why they are good moves, as if you were a coach.")
    print(response.text)
    return response.text
