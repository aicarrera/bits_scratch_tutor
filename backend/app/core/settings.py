from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "CreaBits Tutor API"
    environment: str = "development"
    database_url: str = f"sqlite+aiosqlite:///{(_BACKEND_DIR / 'creabits_dev.db').as_posix()}"
    sql_echo: bool = False
    admin_finish_code: str = "99999"
    llm_mode: Literal["mock", "gemini", "openrouter"] = "mock"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    openrouter_api_key: str | None = None
    openrouter_model: str = "google/gemini-2.5-flash"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def async_database_url(self) -> str:
        url = self.database_url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        if url.startswith("sqlite:///"):
            return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
