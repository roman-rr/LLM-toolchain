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
    
    class Config:
        env_file = ".env"

# Create global settings instance
settings = Settings()

# Utility functions
def get_settings() -> Settings:
    """
    Returns the settings instance.
    Use this as a dependency in FastAPI.
    """
    return settings 