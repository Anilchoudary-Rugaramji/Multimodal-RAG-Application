import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    EXTRACTED_DOCS_DIR = os.getenv("EXTRACTED_DOCS_DIR", "./note-books/extracted_docs")
    
    def __init__(self):
        if not self.OPENAI_API_KEY:
            print("WARNING: OPENAI_API_KEY not found. Some features will not work.")

settings = Settings() 