import os
from dotenv import load_dotenv
from google import genai

# ✅ Always load .env from same folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

# ✅ BEST working model from your list
MODEL = "models/gemini-2.0-flash"
# Alternative: MODEL = "models/gemini-flash-latest"

def ask_gemini(prompt: str) -> str:
    api_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY missing in .env")

    client = genai.Client(api_key=api_key)

    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return (resp.text or "").strip()
