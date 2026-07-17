from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CreaBits Tutor API"
    environment: str = "development"
    database_url: str = "sqlite+aiosqlite:///./creabits_dev.db"
    auto_create_tables: bool = True
    seed_demo_data: bool = True
    sql_echo: bool = False
    admin_finish_code: str = "99999"
    llm_mode: Literal["mock", "gemini"] = "mock"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash" 
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
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
