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

    # CORS settings
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Auth settings
    secret_key: str = "CHANGE-ME-IN-PRODUCTION-USE-SECURE-RANDOM-KEY"
    session_cookie_name: str = "promptlab_session"
    session_expire_days: int = 30
    verification_token_expire_hours: int = 24

    # Email settings (SMTP)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str = "noreply@promptlab.ai"
    smtp_from_name: str = "PromptLab"
    smtp_use_tls: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
