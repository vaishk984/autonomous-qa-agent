"""Configuration settings for the QA Agent application."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
CHROMA_DIR = DATA_DIR / "chroma_db"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

COLLECTION_NAME = "qa_knowledge_base"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

API_HOST = "0.0.0.0"
API_PORT = 8000

SUPPORTED_EXTENSIONS = {
    ".md": "markdown",
    ".txt": "text",
    ".json": "json",
    ".pdf": "pdf",
    ".html": "html",
    ".docx": "docx"
}