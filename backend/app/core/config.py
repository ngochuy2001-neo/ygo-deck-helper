from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Cấu hình ứng dụng FastAPI, đọc từ biến môi trường hoặc file .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "YGO Deck Helper API"
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:3000"

    # Đường dẫn tới file cấu hình LM Studio dùng chung với agents/
    LM_STUDIO_CONFIG_PATH: str = ""

    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "2001"
    POSTGRES_DB: str = "ygo-helper"

    @property
    def database_url(self) -> str:
        """URL async cho SQLAlchemy + asyncpg."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def lm_studio_config_path(self) -> Path:
        if self.LM_STUDIO_CONFIG_PATH.strip():
            return Path(self.LM_STUDIO_CONFIG_PATH).resolve()
        return Path(__file__).resolve().parents[3] / "agents" / "config" / "lm_studio.json"


settings = Settings()
