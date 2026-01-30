"""
Configuration module for RAG Chatbot
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """Application settings"""
    
    # Google Gemini API
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    # ChromaDB Configuration
    chroma_db_dir: str = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    collection_name: str = os.getenv("COLLECTION_NAME", "product_knowledge_base")
    
    # Document Configuration
    knowledge_base_path: str = os.getenv("KNOWLEDGE_BASE_PATH", "./product_info.txt")
    
    # Text Splitting Configuration
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "200"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # Retrieval Configuration
    top_k_results: int = int(os.getenv("TOP_K_RESULTS", "3"))
    
    # LLM Configuration
    model_name: str = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    class Config:
        env_file = ".env"
        protected_namespaces = ('settings_',)  # Fix Pydantic warning


# Global settings instance
settings = Settings()
