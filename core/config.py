from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Security (Use: openssl rand -hex 32 to generate a real one)
    SECRET_KEY: SecretStr = "change-me-in-production"
    ENV: str = "development" # development or production
    
    # LLM Configs
    LLM_PROVIDER: str = "ollama"
    OLLAMA_MODEL: str = "dolphin-phi:latest"
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_API_KEY: str = "ollama"

    # API Configs
    API_URL: str = "http://127.0.0.1:8000"

    # Loads .env
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
