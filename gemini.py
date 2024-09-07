import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key
genai.configure(api_key=os.getenv("API_KEY"))

def coach_answer(move_history):
    gemini = genai.GenerativeModel("gemini-pro")
    response = gemini.generate_content(f"In a Classic Chess game, based on the following notation: {move_history}; analyze White's last move with a brief explanation. Provide only a single sentence summary.")

    print(response)

    if response is not None and hasattr(response, "candidates"):
        if response.candidates[0].finish_reason == "safety":
            analysis = "Houve um erro ao analisar sua jogada."
        analysis = response.text.strip()
    return analysis
