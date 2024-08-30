import os
import google.generativeai as genai
from dotenv import load_dotenv

f = open("fen.txt", "r")
fen=f.read()

# Load environment variables from .env file
load_dotenv()
# Access the API key
genai.configure(api_key=os.getenv("API_KEY"))

gemini = genai.GenerativeModel("gemini-pro")
response = gemini.generate_content(f"In a Classic Chess game, here is the state of the board according to FEN notation: {fen} . Suggest me 3 good moves and very briefly explain why they are good moves, as if you were a coach.")
print(response.text)
