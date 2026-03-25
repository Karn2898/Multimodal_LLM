"""
config/settings.py – Application-wide configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Google Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"
    GEMINI_TIMEOUT: int = 60

    # FastAPI / Uvicorn
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_RELOAD: bool = True

    # File uploads
    MAX_IMAGE_SIZE_MB: int = 10
    MAX_AUDIO_SIZE_MB: int = 25
    UPLOAD_DIR: str = "static/uploads"

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # Optional API auth
    API_SECRET_KEY: str = ""


settings = Settings()
