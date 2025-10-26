import os
from dotenv import load_dotenv
from google.adk.models import Gemini

# Load API keys from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

# Configure the Gemini model to be used by all agents
gemini_model = Gemini(
    name="gemini-2.5-flash",
    api_key=GEMINI_API_KEY
)