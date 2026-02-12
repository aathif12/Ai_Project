"""
Configuration settings for UniRAG backend.
Uses pydantic-settings for type-safe environment variable handling.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = ""
    
    # Supabase Configuration
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_db_url: str = ""
    
    # Storage paths
    upload_dir: str = "./uploads"
    
    # Chunking parameters
    chunk_size: int = 800  # tokens
    chunk_overlap: int = 100  # tokens
    
    # Retrieval parameters
    top_k_results: int = 5
    
    # Model configuration
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"
    embedding_dimensions: int = 1536
    
    # Application settings
    app_name: str = "UniRAG"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def ensure_directories():
    """Create necessary directories if they don't exist."""
    settings = get_settings()
    os.makedirs(settings.upload_dir, exist_ok=True)
