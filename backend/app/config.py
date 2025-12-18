from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost/promptlab"
    api_key_prefix: str = "pl_live_"
    openai_api_key: str | None = None

    # Stripe settings
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_pro: str | None = None  # Price ID for Pro plan
    stripe_price_team: str | None = None  # Price ID for Team plan

    # App URL for Stripe redirects
    app_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
