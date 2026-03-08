from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/marketplace"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/marketplace"

    REDIS_URL: str = "redis://localhost:6379/0"

    GOOGLE_CLIENT_ID: str = "test.apps.googleusercontent.com"

    MOYASAR_SECRET_KEY: str = "sk_test_fake"
    MOYASAR_WEBHOOK_SECRET: str = "test-webhook-secret"
    MOYASAR_BASE_URL: str = "https://api.moyasar.com/v1"

    S3_BUCKET: str = ""
    S3_REGION: str = "me-central-1"
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_ENDPOINT_URL: str = ""

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    FROM_EMAIL: str = "noreply@marketplace.sa"

    OURSMS_APP_SID: str = ""
    OURSMS_APP_SECRET: str = ""
    OURSMS_SENDER_ID: str = "Marketplace"

    PLATFORM_FEE_PERCENT: float = 1.0

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
