import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)


def gemini_explain_market_prices(user_query: str, mandi_data):
    """
    mandi_data = list of records from govt API
    Returns Gemini formatted answer
    """

    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
You are a helpful Indian agriculture assistant.

User asked: {user_query}

Here is the REAL mandi price data from Govt API (Agmarknet style):
{mandi_data}

Task:
1) Give the best price range and modal price in a clean format.
2) Mention date and market name.
3) Give short reason why price might be high/low (1 line).
4) Give 1 simple suggestion (sell/hold/transport).
5) Output in Hinglish + Hindi mix (farmer friendly).
6) Keep response short and clear.
"""

    response = model.generate_content(prompt)
    return response.text
