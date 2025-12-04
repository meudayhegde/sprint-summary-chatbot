from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # LLM Configuration
    llm_provider: Literal["openai", "gemini", "anthropic"] = "openai"
    
    # API Keys
    openai_api_key: str = ""
    google_api_key: str = ""
    anthropic_api_key: str = ""
    
    # Model Names
    openai_model: str = "gpt-4-turbo-preview"
    gemini_model: str = "gemini-pro"
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    
    # Application Settings
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    
    # Data File Path
    data_file: str = "sprint_synthetic_data(Tickets).csv"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
