import os
import google.generativeai as genai

# 🔥 Put your Gemini key here
GEMINI_API_KEY = "AIzaSyAT0v817ipnTAW1fltGLKl6eYCABv3nykw"

genai.configure(api_key=GEMINI_API_KEY)

MODEL = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """
You are Kisan SuperAI, an expert Indian agriculture assistant.
Rules:
1) Answer in very simple language.
2) Give step-by-step actionable solutions.
3) Always include safety note if pesticide/chemical mentioned (consult local officer).
4) Give answers focused on India climate, crops, and real farmer problems.
5) If user question is unclear, ask 1 short clarifying question.
"""

def get_ai_answer(user_question: str) -> str:
    prompt = SYSTEM_PROMPT + "\n\nFarmer Question:\n" + user_question + "\n\nAnswer:"
    resp = MODEL.generate_content(prompt)
    return resp.text.strip()
