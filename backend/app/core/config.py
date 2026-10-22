from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):
    APP_ENV: str = "development"
    PROJECT_NAME: str = "SkillSwap JKLU"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "mysql+pymysql://skillswap:skillswap_pass@127.0.0.1:3307/skillswap?charset=utf8mb4"
    TEST_DATABASE_URL: str = "mysql+pymysql://skillswap:skillswap_pass@127.0.0.1:3307/skillswap_test?charset=utf8mb4"

    # Security
    JWT_SECRET_KEY: str = "skillswap-dev-secret-key-jklu-2026-very-secure-jwt"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # SMTP (optional in dev)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "no-reply@jklu.edu.in"

    # Business Rules
    REPUTATION_PER_SESSION: int = 10
    REQUIRE_ADMIN_APPROVAL: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
