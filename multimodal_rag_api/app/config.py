import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PDF_PATH = os.getenv("PDF_PATH", "./data/attention_paper.pdf")
    EXTRACTED_DOCS_DIR = os.getenv("EXTRACTED_DOCS_DIR", "./note-books/extracted_docs")

settings = Settings() 