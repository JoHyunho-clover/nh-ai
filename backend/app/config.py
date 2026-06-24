from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://nhaiuser:nhaipass@localhost:5432/nhai_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # App
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
