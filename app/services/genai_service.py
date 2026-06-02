import os
import google.generativeai as genai

# Configure the Gemini API (set GEMINI_API_KEY environment variable)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")




