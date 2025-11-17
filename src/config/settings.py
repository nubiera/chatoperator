"""Configuration management using pydantic-settings."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Google Gemini API
    GEMINI_API_KEY: str

    # Browser Configuration
    DEFAULT_BROWSER: Literal["chrome", "firefox"] = "chrome"
    HEADLESS_MODE: bool = True

    # Chatbot API
    CHATBOT_API_URL: str = ""
    CHATBOT_API_KEY: str = ""

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # Cache Directory
    CACHE_DIR: str = "./src/cache"

    # Polling Configuration (seconds)
    POLL_INTERVAL: int = 10

    # Operation Timeouts (seconds)
    PAGE_LOAD_TIMEOUT: int = 30
    ELEMENT_VISIBLE_TIMEOUT: int = 10
    MESSAGE_SEND_TIMEOUT: int = 5

    @property
    def cache_dir_path(self) -> Path:
        """Get cache directory as Path object."""
        path = Path(self.CACHE_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path


# Global settings instance
settings = Settings()
