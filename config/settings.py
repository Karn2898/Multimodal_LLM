"""Application settings loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	"""Centralized runtime configuration."""

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		case_sensitive=True,
	)

	GEMINI_API_KEY: str = Field(default="")
	GEMINI_MODEL: str = Field(default="gemini-2.5-Flash")
	GEMINI_TIMEOUT: int = Field(default=60)

	APP_HOST: str = Field(default="0.0.0.0")
	APP_PORT: int = Field(default=8000)
	APP_RELOAD: bool = Field(default=True)

	MAX_IMAGE_SIZE_MB: int = Field(default=10)
	MAX_AUDIO_SIZE_MB: int = Field(default=25)

	# Optional auth. If empty, auth checks are skipped.
	API_SECRET_KEY: str = Field(default="")

	# Used by utils/file_helpers.py
	UPLOAD_DIR: str = Field(default="static/uploads")


settings = Settings()

