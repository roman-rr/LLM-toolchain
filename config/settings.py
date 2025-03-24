from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Base Configuration
    PROJECT_NAME: str = "LLM-Toolchain"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # Path Configuration
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_BUCKET_NAME: str
    AWS_REGION: str
    
    # LangChain Configuration
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_ENDPOINT: str
    LANGCHAIN_API_KEY: str
    LANGCHAIN_PROJECT: str
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    
    # Pinecone Configuration
    PINECONE_API_KEY: str
    
    # Database Configuration
    POSTGRES_URI: str
    
    # Search Configuration
    SERPAPI_API_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()

# Utility functions
def get_settings() -> Settings:
    """
    Returns the settings instance.
    Use this as a dependency in FastAPI.
    """
    return settings 