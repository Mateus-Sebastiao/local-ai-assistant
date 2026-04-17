from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM Configs
    LLM_PROVIDER: str = "ollama"
    OLLAMA_MODEL: str = "llama3.2:3b"
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_API_KEY: str = "ollama"

    # API Configs
    API_URL: str = "http://127.0.0.1:8000"

    # Loads .env
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
