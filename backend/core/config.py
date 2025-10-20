"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Zerodha API
    KITE_API_KEY: str = ""
    KITE_API_SECRET: str = ""
    KITE_ACCESS_TOKEN: str = ""

    # Database
    DATABASE_URL: str = "sqlite:///./leanflow.db"

    # Backend API
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # LEAN Engine
    LEAN_DATA_FOLDER: str = "./data"
    LEAN_RESULTS_FOLDER: str = "./results"
    LEAN_CONFIG_PATH: str = "./src/config/config.json"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Risk Management (SEBI Compliance)
    MAX_OPS_PER_SECOND: int = 10
    DRAWDOWN_KILL_SWITCH_THRESHOLD: float = 0.05
    ENABLE_KILL_SWITCH: bool = True

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS


settings = Settings()

