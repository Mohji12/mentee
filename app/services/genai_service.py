import os
import google.generativeai as genai

# Configure the Gemini API (set GEMINI_API_KEY environment variable)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Using gemma-3-4b-it (Gemma model, separate quota from Gemini Flash)
# Alternative models: gemini-2.5-flash, gemini-2.0-flash, gemini-2.5-flash-lite
model = genai.GenerativeModel("gemma-3-4b-it")




