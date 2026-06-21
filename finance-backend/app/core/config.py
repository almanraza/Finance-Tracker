from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Claude AI
    ANTHROPIC_API_KEY: str

    # Redis
    REDIS_URL: Optional[str] = None

    # Sentry
    SENTRY_DSN: Optional[str] = None

    # App
    APP_ENV: str = "development"
    APP_NAME: str = "Finance Manager API"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
