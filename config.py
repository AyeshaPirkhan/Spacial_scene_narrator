import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY")